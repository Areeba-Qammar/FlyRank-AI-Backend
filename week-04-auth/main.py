import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI(title="FlyRank Auth API - A4")

security = HTTPBearer()


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@app.get("/")
def health_check():
    return {"message": "Server running and connected to Supabase"}


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthRequest):
    try:
        response = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
        if not response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
        if not response.session:
            raise HTTPException(
                status_code=401, detail="Invalid login credentials"
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid login credentials"
        )


@app.get("/auth/me", status_code=status.HTTP_200_OK)
def get_me(current_user=Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at,
        }
    }


# Stage 3: Refresh Token Route
@app.post("/auth/refresh", status_code=status.HTTP_200_OK)
def refresh_token(body: RefreshRequest):
    try:
        response = supabase.auth.refresh_session(body.refresh_token)
        if not response.session:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token"
        )


# Stage 3: Logout Route
@app.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
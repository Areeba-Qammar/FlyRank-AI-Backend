import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="FlyRank Auth API — Week 4 / A4",
    description="Secure API built with FastAPI + Supabase Auth",
)

# Fix Bug 1: Global Validation Handler for 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request"},
    )


# Fix Bug 2: Allow auto_error=False so missing header hits custom 401 logic
security = HTTPBearer(auto_error=False)


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"},
        )

    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"},
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"},
        )


@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}


@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthRequest):
    try:
        response = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
        if not response.user:
            raise HTTPException(
                status_code=400, detail={"error": "Signup failed"}
            )
        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
        if not response.session:
            raise HTTPException(
                status_code=401, detail={"error": "Invalid login credentials"}
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        raise HTTPException(
            status_code=401, detail={"error": "Invalid login credentials"}
        )


@app.get("/protected/profile", status_code=status.HTTP_200_OK)
def get_profile(current_user=Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at,
        }
    }


@app.get("/protected/dashboard", status_code=status.HTTP_200_OK)
def get_dashboard(current_user=Depends(get_current_user)):
    return {
        "message": f"Welcome to your private dashboard, {current_user.email}!",
        "user_id": current_user.id,
    }


@app.post("/auth/refresh", status_code=status.HTTP_200_OK)
def refresh_token(body: RefreshRequest):
    try:
        response = supabase.auth.refresh_session(body.refresh_token)
        if not response.session:
            raise HTTPException(
                status_code=401,
                detail={"error": "Invalid or expired refresh token"},
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or expired refresh token"},
        )


# Updated logout to use get_current_user dependency guard
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
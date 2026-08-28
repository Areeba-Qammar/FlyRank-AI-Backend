# FlyRank Auth API — Week 4 / A4

Secure API built with **FastAPI** + **Supabase Auth**. Handles sign up, log in, log out, and protects routes with JWT verification. (This README grows as each stage is completed — full API reference + Swagger screenshot get added in the final stage.)

## Environment Setup

### 1. Create a Supabase Project
Go to [supabase.com](https://supabase.com), sign up free, and spin up a new project.

### 2. Find Your Project URL and Anon Key
In the Supabase Dashboard: **Project Settings** (⚙️ icon) → **API**.

- **Project URL** — at the top of the page, looks like `https://xxxxxxxx.supabase.co`. This is **not** an API key.
- **anon / publishable key** — a long string (older projects start with `eyJ...`, newer ones with `sb_publishable_...`). Safe to use client-side.
- ⚠️ Never use the `service_role` / `sb_secret_...` key here — it bypasses all security checks and must stay server-side only.

### 3. Create Your `.env` File

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
PORT=8000
```

> `.env` is already in `.gitignore` — never commit real keys. A `.env.example` with placeholder values goes in the repo instead.

## Running the Server

```powershell
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Expected output: `Server running and connected to Supabase`

## Testing — Sign Up (PowerShell)

```powershell
Invoke-RestMethod -Uri http://localhost:8000/auth/signup -Method Post -ContentType "application/json" -Body '{"email":"testuser@example.com", "password":"password123"}'
```

Expect a `201 Created` response containing the new user object.

---
# FlyRank Auth API — Week 4 / A4

Secure API built with FastAPI + Supabase Auth. Handles user registration, login, logout, token refresh, and protected route authorization via JWT.

## API Reference

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/` | GET | No | Server health check |
| `/public/info` | GET | No | Unprotected public information |
| `/auth/signup` | POST | No | Registers a new user account |
| `/auth/login` | POST | No | Authenticates user and returns JWT |
| `/protected/profile` | GET | Yes (Bearer) | Returns authenticated user details |
| `/protected/dashboard` | GET | Yes (Bearer) | Protected dashboard route |
| `/auth/refresh` | POST | No | Generates new access token |
| `/auth/logout` | POST | Yes (Bearer) | Invalidates user session |

## Swagger UI Authorization Verification

![Swagger UI Authorization](./swagger.png)

## Local Setup

1. Clone repository and navigate to `week-04-auth`.
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file using `.env.example` as reference:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   PORT=8000
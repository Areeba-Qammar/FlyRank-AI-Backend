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
*Sections to add later: full API reference table (endpoint / method / auth required), Swagger UI screenshot, "AI vs me" writeup (Stage 7 bonus).*
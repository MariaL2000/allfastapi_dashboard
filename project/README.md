# FastAPI Regulated Project (SQLite + JWT + Refresh Tokens + Roles + Google OAuth2 scaffold)

python -m venv venv
source venv/bin/activate # (Linux/Mac)
venv\Scripts\activate # (Windows)
**Contents**

- Full FastAPI app adapted for SQLite and strengthened for production-like usage
- Access tokens (JWT) + persistent refresh tokens (DB-backed) with revocation
- Roles & permissions model (User, Role, UserRole)
- Protected endpoints and dependencies to require roles
- Google OAuth2 sign-in scaffold (requires Google Cloud credentials)
- `.env.example` provided — **copy to .env** and fill secrets before running

## Quick start (local)

1. Create venv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   ```
2. Install:
   ```bash
   cd project
   pip install -r requirements.txt
   ```
3. Copy `.env.example` -> `.env` and set values.
4. Run app:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
5. Open docs: http://127.0.0.1:8000/docs

## Notes

- For Google OAuth2 sign-in: set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` in `.env`.
- The refresh token system stores refresh tokens in DB and allows revocation.
- Roles system supports creating roles and assigning them to users; protect endpoints with dependencies.

If you want a walkthrough of the main files, or a Docker setup, ask and I'll add it.

# Setup

## Docker

Install Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux).
Copy `.env.example` to `.env`, then run `docker compose up --build` from the root.
Use http://localhost:8080. The backend runs migrations automatically before serving.
This configuration is a local development deployment. Change the database password before production.

## Local development without Docker

Requires Python 3.12+ and Node 24.15+ (verified on 24.19.0). Angular 22.2.1 also supports Node ^22.22.3 or >=26.

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
cd backend
pip install -e '.[test]'
# With no .env, SQLite is used automatically; no database service is needed.
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm ci
npm start
```

Open http://localhost:4200. Angular proxies `/api` to port 8000.

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
python -m pip install -e ".[test]"
uvicorn app.main:app --reload --port 8000
```

In another PowerShell window run `cd frontend`, `npm ci`, then `npm start`.
If activation is unavailable, call `.venv\Scripts\python.exe` and `.venv\Scripts\uvicorn.exe` directly.

To configure a native backend, create `backend/.env`:

```dotenv
DATABASE_URL=sqlite+aiosqlite:///./readme-ai.db
FRONTEND_URL=http://localhost:4200
BACKEND_URL=http://localhost:8000
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
TOKEN_ENCRYPTION_KEY=
```

The root `.env` is for Compose. The backend reads `.env` from its current working directory. Restart the backend after configuration changes.

## OpenAI

Set `OPENAI_API_KEY` on the backend. Choose an available model that supports structured output through `OPENAI_MODEL`; the default is `gpt-4o-mini`.
API usage is billed to your OpenAI API project, separately from any ChatGPT subscription. The UI's “Use AI” toggle controls generation; disabling it uses verified templates. AI rewrite requires a key even with the toggle off. Failed requests count toward the daily quota (reset at UTC midnight).

The model sees the public profile, shortlisted repository metadata, and the README/instruction when rewriting. Do not include sensitive information in a README you submit to the AI assistant.

## GitHub OAuth

1. Register an OAuth app in GitHub Settings → Developer settings → OAuth Apps.
2. Homepage: `http://localhost:4200` (native) or `http://localhost:8080` (Docker).
3. Authorization callback: `http://localhost:8000/api/v1/auth/github/callback`.
4. Configure client ID and secret on the backend.
5. Generate an encryption key using the backend Python environment:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

6. Set `TOKEN_ENCRYPTION_KEY` to that value. Keep it stable; rotating it requires users to reconnect.
7. Use the same hostname (`localhost`) everywhere. Do not mix localhost and 127.0.0.1.

Requested OAuth scopes: `read:user public_repo`. OAuth's `public_repo` scope can write to authorized public repositories; this application's code restricts publishing to the authenticated account's own public `username/username` profile repository. A future GitHub App with per-repository installation could narrow GitHub-level permissions further.

Never put keys in `frontend/`, commit `.env`, or paste access tokens into the UI.

## PostgreSQL and Redis

Set `DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB` and run `alembic upgrade head` in `backend/` before starting the API. SQLite automatic schema creation is only a local convenience. `REDIS_URL` activates shared request rate limiting; when absent, rate limits and the five-minute GitHub cache are process-local. AI quotas are persisted in the database.

## Common failures

| Symptom | Action |
| --- | --- |
| Backend unavailable | Start FastAPI; use the Angular dev server or Docker nginx proxy |
| GitHub rate limit | Wait for reset or configure a server token for public lookups |
| AI not configured | Disable Use AI for generation or set a backend API key |
| OAuth not configured | Configure client ID, secret, encryption key and callback URL |
| CSRF rejected | Match FRONTEND_URL to the browser origin and sign in again |
| Concurrent update | Refresh the publish diff or load the latest cloud draft |
| Stats image fails | Disable that widget; no profile data is fabricated as a substitute |
| Local autosave fails | Browser storage is full/blocked; download Markdown as a backup |

# Deployment

Deploy the Angular static build behind an HTTPS reverse proxy and run FastAPI as a Python service/container. This stack needs a Python runtime; a static-only host cannot run the backend.

1. Provision PostgreSQL and Redis with private connectivity, persistent volumes and backups.
2. Set credentials via your hosting secret manager. Replace Compose development database credentials.
3. Build frontend with `npm ci && npm run build` and serve `frontend/dist/studio/browser`.
4. Route `/api` from the frontend origin to FastAPI. Route all other unknown paths to `index.html`.
5. Set `FRONTEND_URL` to the exact HTTPS browser origin. Set `BACKEND_URL` to the public callback origin (normally the same origin).
6. Configure GitHub's OAuth callback as `https://YOUR_DOMAIN/api/v1/auth/github/callback`.
7. Set `COOKIE_SECURE=true`. Keep the frontend and callback on the same site for cookies.
8. Run `alembic upgrade head` as a one-time release job before serving; don't run competing migrations in many replicas.
9. Start `uvicorn app.main:app --host 0.0.0.0 --port 8000` behind a trusted ingress. Configure forwarded headers only from trusted proxy addresses.
10. Monitor `/api/v1/health`, DB availability, OpenAI costs, GitHub limits, publish errors and migrations.

The sample nginx policy allows the Monaco AMD build's evaluation and inline styles; it disallows embedded frames and arbitrary objects. Review CSP if migrating Monaco to an ESM worker build. Third-party widget images are allowed from HTTPS providers; they can make requests from the user's browser.

Use Redis for shared request limits. IP daily AI quotas are a basic cost guard, not a billing system. The implementation uses atomic database-backed IP quotas; add authenticated per-user quotas and abuse controls before exposing AI to large traffic. Keep proxy client-address handling trustworthy. Add cleanup policies for expired sessions, OAuth states, profile snapshots and old drafts. Encrypt and back up the database and keep the Fernet key separate from it.

Never claim production readiness from local tests alone. Run real OAuth, sandbox AI calls, PostgreSQL integration, load tests and operational recovery checks with your deployment's credentials before release.

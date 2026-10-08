<h1 align="center">README.AI — GitHub README Studio</h1>

<p align="center"><strong>Your code tells a story. Give it a great introduction.</strong></p>

<p align="center">
  <a href="https://readme-ai-studio.dilangamalshan15.chatgpt.site">
    <img src="https://img.shields.io/badge/%E2%86%97_OPEN_README_STUDIO-d6f58c?style=for-the-badge&logo=googlechrome&logoColor=1a1a1a" alt="Open README Studio" height="42">
  </a>
</p>

<h2 align="center"><a href="https://readme-ai-studio.dilangamalshan15.chatgpt.site">Explore the live README Studio ↗</a></h2>

<p align="center">Public website · Open in your browser · No installation needed</p>

<hr>

<h3 align="center">Why build alone when GPT is right there?</h3>
<p align="center">My ideas. Built with GPT. Hosted on ChatGPT Sites.</p>

<hr>

An Angular + Python FastAPI GitHub profile README studio. Analyze real public repositories, choose a template, refine content with AI, edit Markdown with Monaco, preview it live, and explicitly review changes before publishing.

Created for **Dilanga Malshan** · [GitHub](https://github.com/Dilanga-Malshan)

## Hosted app

**[Open README.AI Studio ↗](https://readme-ai-studio.dilangamalshan15.chatgpt.site)**

Use the hosted edition in your browser without Docker or local setup. The website is **public** and available to anyone with the link.

The hosted edition supports public GitHub analysis, six templates, Markdown editing, preview, downloads, and ChatGPT-authenticated cloud drafts. AI generation and direct GitHub publishing are not connected; use the download/upload guide.

This repository contains the Angular + FastAPI local edition. The hosted edition uses a Sites-compatible server and D1 storage.

## Start locally

### Windows: double-click to start

1. Install **Docker Desktop** and make sure it is running.
2. [Download the project ZIP](https://github.com/Dilanga-Malshan/Readme-Ai-Studio/archive/refs/heads/main.zip) and extract it.
3. Double-click **[start-local.bat](start-local.bat)** inside the extracted project folder.

The launcher creates `.env` from `.env.example` only if it is missing, starts the Docker services, waits for the app, and opens your browser automatically. The first launch needs an internet connection and may take several minutes to build. Existing `.env` settings are preserved.

**[Open Local App → http://localhost:8080](http://localhost:8080)** · **[Open API Docs → http://localhost:8000/docs](http://localhost:8000/docs)**

The links open an app that is already running on your own computer. Clicking a GitHub README link cannot start a local server; use the launcher first.

### Terminal startup (any OS)

```bash
cp .env.example .env
docker compose -p readme-ai-studio up --build
```

No AI key is needed for factual template generation, public GitHub analysis, local editing, or downloads. OpenAI generation and rewriting require your own server-side API key and incur API usage charges. GitHub sign-in, cloud drafts, and publishing require a registered GitHub OAuth app and a Fernet encryption key.

See [Setup](docs/SETUP.md) for local Python/Node development, Windows commands, credentials, and troubleshooting.

## Implemented

- Public GitHub profile import; paginated repositories; language inference; transparent ranking based on metadata, recency, topics, README presence and popularity.
- Six data-driven starting templates, project selection, section visibility/order, alignment, palette, badges, skill icons, typing headers and optional stats widgets.
- Monaco Markdown editor: search/replace, undo/redo, safe whitespace formatting, copy, import and download.
- Sanitized live preview; desktop/mobile widths; light/dark preview; zoom; exported HTML preview.
- Structured LangChain/OpenAI content generation, rewrite/optimization endpoints and a review-before-apply AI assistant.
- Local browser autosave/history; authenticated cloud drafts and revision history; optimistic cloud-save concurrency.
- OAuth state validation and PKCE; server-side encrypted GitHub tokens; HTTP-only sessions; CSRF protection.
- Exact publishing diff; account-owned public profile repository validation; explicit confirmation; GitHub SHA/branch conflict detection; idempotency records.
- Async SQLAlchemy models, frozen Alembic migration, PostgreSQL deployment, SQLite convenience for local development, optional Redis rate limiting.
- Automated backend and frontend tests; CI; Docker Compose; setup/API/deployment documentation.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Angular 22.2.1, TypeScript 6, Signals, Router, Tailwind CSS 4, Monaco, marked, DOMPurify |
| Backend | Python 3.12+, FastAPI, Pydantic 2, async SQLAlchemy, httpx, Jinja2 |
| AI | LangChain + OpenAI structured Pydantic output; configurable model |
| Persistence | PostgreSQL, Alembic; SQLite for local development |
| Security | Fernet tokens, opaque sessions, CSRF, strict CORS, sanitization, rate limits |

## Project structure

```text
frontend/src/app/   Landing, studio, API service, Monaco editor, preview sanitizer
backend/app/api/    Versioned routes and authentication flows
backend/app/ai/     Structured, evidence-grounded generation and proposals
backend/app/core/   Configuration, authentication and database
backend/app/models/ Normalized persistence entities
backend/app/schemas/ Validated API contracts
backend/app/services/ GitHub, composition, publishing
backend/alembic/    Frozen schema migration
backend/tests/     API, persistence, security and GitHub mocks
docs/              Setup, API, architecture, deployment and verification
```

## Tests

```bash
cd backend
python -m pip install -e '.[test]'
pytest -q
cd ../frontend
npm ci
npm test
npm run build
```

## Honest boundaries

This is a runnable implementation, not a claim of commercial production certification. Real OAuth and live OpenAI calls need your credentials; their external happy paths were not executed during development. See [Verification](docs/VERIFICATION.md).

GitHub preview is approximate, not pixel-perfect. External stats and typing services may fail. AI-generated facts require review. Pinned repositories are not inferred; GitHub public REST metadata does not expose the pinned list. Arbitrary README fonts and CSS do not work on GitHub.

Revocable seven-day sharing links expose only a saved snapshot. The studio includes three style variants, selected-section regeneration, a downloadable SVG banner generator and animated footer widgets. Remaining extensions are tracked in [Roadmap](docs/ROADMAP.md).

## License

MIT. Third-party libraries and widget providers retain their own licenses and terms.

## Publish the source repository

On your own Windows machine, after installing Git and GitHub CLI, run the following from the extracted project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-github.ps1
```

The script checks that you are signed in as `Dilanga-Malshan`, creates `readme-ai-studio` as a **public** repository, pushes the source and reports the actual visibility. It does not overwrite an existing repository.

The downloadable package itself is not proof that a remote repository has been created.

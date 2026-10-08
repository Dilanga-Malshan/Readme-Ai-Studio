# Verification

Executed during development:

- Backend: **45 pytest tests passed**. Includes username validation, GitHub pagination/rate-limit mocks, zero repositories, AI mocks/quota, rendering attacks, cloud revisions, ownership, share snapshot/revocation, OAuth callback/state/session/CSRF, publish confirmation/conflicts/idempotency/permissions, SVG escaping and selected-section preservation.
- Frontend: **25 Vitest tests passed**. Includes form validation, preview sanitization, live edits, manual draft preservation across reload, review-before-apply, history, error preservation and CSRF headers.
- Angular production build completed with compatible Angular 22.2.1 / TypeScript 6 / Node 24.19.0 dependencies.
- Alembic upgrades through `0003` and `alembic check` executed against SQLite; no schema drift was detected.

Not executed:

- Real OAuth authorization or live OpenAI generation: external credentials were not supplied. Automated tests use clearly identified provider mocks.
- Live PostgreSQL/database containers or Docker image builds: Docker was unavailable. CI includes a PostgreSQL migration job.
- Browser visual QA / Playwright execution: the available environment did not provide the required supported browser QA workflow. The Playwright suite is supplied for desktop/mobile validation using labeled test fixtures; it does not substitute for live-provider validation.

To run browser tests locally:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

The Playwright tests cover invalid usernames, fixture profile → generation → preview → anonymous download, imported manual drafts across reload, and malicious Markdown. Run them in your configured environment before deployment.

See ROADMAP.md for remaining specification extensions. Tests do not constitute a production security certification. No credentials, .env files, databases, dependencies, or build caches are included in the deliverable.

# Architecture

The Angular client analyzes public GitHub data through FastAPI, edits a local draft, composes Markdown through a data-driven Jinja2 template, and renders a sanitized approximation of GitHub Markdown. A direct editor change updates the preview immediately. Visual changes are applied explicitly; if a draft differs from the last generated document, a review dialog is shown before replacement.

AI generation is an optional evidence-based path: extraction → transparent repository ranking → structured profile content → template composition → safe rendering and review warnings. AI rewriting submits the current README, a bounded instruction and verified public metadata; it returns a proposed document for human review. Repository content is never executed.

## Persistence

Users are keyed by immutable GitHub IDs. Account tokens are Fernet-encrypted. Opaque session cookies are stored only as hashes; sessions expire. CSRF tokens are per-session. OAuth state is bound to an HTTP-only browser cookie, persisted with an expiry, atomically consumed and paired with a PKCE verifier.

Readme projects have owners and revisions. A save conditionally increments the expected revision and writes a version in one transaction. A stale revision is rejected. Publish attempts use a unique `(user_id, idempotency_key)` and a request hash; an identical successful retry reuses the original result. GitHub file SHA provides external concurrency protection. The default branch is also validated against the preview.

## Public analysis

Public REST repository pages are fetched until completion (bounded to 10,000). Private repositories are excluded. Forks and archived repositories remain selectable but are excluded from automatic ranking. Top candidates are checked for README existence. Complexity is represented by repository-size metadata only, not a claim about code quality. Stars never prove professional ability. Languages are primary-language suggestions, not a complete technology inventory.

## Trust boundaries

- Backend secrets never enter client JavaScript.
- Rendering uses explicit safe tag/attribute/URL rules and DOMPurify, then Angular's own sanitizer.
- AI instructions distinguish repository metadata from system instructions. This reduces prompt injection exposure; it is not a formal guarantee against all model errors.
- GitHub publishing operates only on the authenticated user's owned, writable, public profile repository.
- Local drafts remain browser-local; authenticated cloud drafts are owner-only. Sharing requires an explicit owner action and produces an unlisted, revocable seven-day token URL to a saved snapshot. Tokens are stored hashed; account/configuration data are never included.
- Widget images may make requests to third-party providers when previewed or viewed on GitHub.

## Operational limits

Without Redis, rate limits/cache apply per process. For distributed production traffic, use Redis and a trusted ingress with correct client-address forwarding. The daily AI budget is IP-based with an atomic transactional counter and UTC-day reset; failures consume reservations. Per-account billing needs an authenticated billing identity. Public snapshot retention and cleanup should be added for sustained deployments. AI claims are not mechanically proved; review is required.

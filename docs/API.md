# API reference

Interactive documentation: `/docs`; machine-readable schema: `/openapi.json`.
All application routes start with `/api/v1`.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Backend health and configured capability flags |
| GET | `/github/profile/{username}` | Public GitHub profile |
| GET | `/github/repositories/{username}` | Paginated public repository metadata |
| POST | `/github/analyze` | Snapshot, language inference and ranked public repositories |
| POST | `/ai/generate` | Structured content + composed Markdown; `use_ai:false` needs no AI key |
| POST | `/ai/variants` | Three visual variants with the same verified content |
| POST | `/ai/regenerate-section?section=About%20me` | Regenerate one section while preserving others |
| GET | `/banners/svg` | Download a safe generated SVG banner |
| POST | `/readmes/{id}/share` | Explicitly share or revoke a seven-day snapshot link |
| GET | `/shared/{token}` | Read an unexpired shared snapshot |
| POST | `/ai/rewrite` | Proposed Markdown rewrite with explanation |
| POST | `/ai/optimize` | Same evidence-grounded proposal contract |
| POST | `/ai/chat` | Natural-language instruction → reviewable Markdown proposal |
| GET | `/templates` | Six data-driven templates |
| GET | `/templates/{id}` | Template metadata |
| POST | `/readmes/render` | Anonymous sanitized rendering |
| POST | `/readmes` | Create an owned cloud draft |
| GET | `/readmes` | List the current user's drafts |
| GET | `/readmes/{id}` | Read an owned draft |
| PATCH | `/readmes/{id}` | Conditional revision-based save |
| GET | `/readmes/{id}/versions` | Up to 100 stored revisions |
| POST | `/readmes/{id}/render` | Render an owned cloud draft |
| GET | `/readmes/{id}/export` | Download an owned cloud draft |
| GET/PUT | `/preferences` | Current user's preferences |
| GET | `/auth/github/login` | OAuth authorization redirect |
| GET | `/auth/github/callback` | State-validated PKCE token exchange |
| GET | `/auth/me` | Session identity and CSRF token |
| POST | `/auth/logout` | Invalidate current session |
| POST | `/github/publish-preview` | Exact diff against the authenticated profile repository |
| POST | `/github/publish` | Explicitly confirmed, concurrency-protected commit |
| GET | `/github/publish-status/{id}` | Owned publish result |

Cloud, preference and publishing routes require the HTTP-only session cookie. Mutating authenticated routes also require `Origin` equal to `FRONTEND_URL` and `X-CSRF-Token` obtained from `/auth/me`.

Example generation:

```json
{"username":"Dilanga-Malshan","use_ai":false,"config":{"template":"professional","accent":"38BDF8","projects":[],"sections":{"about":true,"skills":true,"projects":true,"social":true}}}
```

Example publish (use the exact SHA and branch from a fresh publish-preview):

```json
{"markdown":"# My profile\n","expected_sha":"CURRENT_FILE_SHA","expected_branch":"main","confirm":true,"create_repository":false,"idempotency_key":"a-new-unique-uuid"}
```

Do not publish when a preview changed or confirmation has not been given. A missing repository additionally requires `create_repository:true`. A stale SHA, branch or cloud revision returns 409. Idempotency key reuse with different content also returns 409.

Errors use `{"error":{"message":"…","status":400}}`. Validation errors additionally list field details. Inputs and request bodies are bounded. Public user names are validated before reaching GitHub. Standard route-not-found and unexpected infrastructure failures may use framework-level responses.

Local Markdown download is implemented in the browser and requires no authentication; cloud export is authenticated so private drafts are not exposed.

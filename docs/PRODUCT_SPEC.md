# MASTER PROMPT — README.AI
## Build a Production-Ready AI-Powered GitHub README Studio

You are a **Senior Full-Stack Software Engineer, AI Engineer, SaaS Architect, UI/UX Designer, and DevOps Engineer**.

Your mission is to architect, design, and implement a complete, modern, production-quality AI-powered GitHub README generation platform called **README.AI**.

This must be a real, functional web application — not just a landing page, static prototype, or mockup.

### 1. Product Vision

Build an intelligent GitHub Profile README Studio that transforms a GitHub username into a beautifully designed, personalized, professional GitHub Profile README.

The application should automatically analyze public GitHub data, identify the user's technical background, generate accurate AI-powered profile content, allow complete customization, and export or publish the README to GitHub.

**Core philosophy:**
"Your GitHub profile deserves more than a template."

The platform must combine AI intelligence, visual customization, automation, and a premium developer-focused user experience.

### 2. Technology Stack

**Frontend**
- Angular (latest stable compatible version)
- TypeScript
- Tailwind CSS
- Angular Signals
- Angular Router
- Monaco Editor
- Markdown rendering and sanitization
- Lucide Icons
- Responsive layouts
- Accessible UI components

**Backend**
- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0 (Async)
- PostgreSQL
- Alembic
- httpx
- Jinja2
- Redis for optional caching and rate limiting

**AI**
- OpenAI API
- LangChain
- Structured AI responses using Pydantic
- Context-aware prompt engineering
- Intelligent repository ranking
- README content optimization
- AI-powered content rewriting

**External Integrations**
- GitHub REST API
- GitHub OAuth
- GitHub repository content API
- GitHub profile stats services
- Shields.io
- Skill Icons
- Readme Typing SVG
- GitHub contribution visualization integrations where reliable

Use environment variables for all secrets. Never expose OpenAI or GitHub credentials in frontend code.

### 3. Premium UI/UX Design

Create an original, visually striking developer SaaS interface inspired by modern IDEs and professional design tools, without copying any existing product.

**Design system**

- Primary background: #09090B
- Secondary surface: #111318
- Card background: #181B22
- Primary text: #F8FAFC
- Secondary text: #94A3B8
- Accent: #38BDF8
- Secondary accent: #A78BFA
- Optional neon green: #C8F77C
- Clean typography
- Subtle gradient highlights
- Glassmorphism used sparingly
- Smooth micro-interactions
- Professional spacing
- Rounded cards and subtle borders

Support both dark and light modes.

Build responsive desktop, tablet, and mobile experiences.

**Landing page requirements**

- Animated hero section
- Live example README preview
- GitHub username input
- "Generate My README" primary CTA
- Interactive feature showcase
- Visual before/after README comparison
- Theme gallery
- How-it-works section
- FAQ
- Professional footer

Use meaningful animations, skeleton loaders, polished hover states, and helpful empty states.

### 4. Main Application Dashboard

Create an advanced dashboard with a three-panel layout.

**Left panel — Customization**

Provide controls for:

- Profile information
- About section
- Social links
- Technical skills
- Featured projects
- GitHub statistics
- Animations
- Layout
- Colors
- Fonts
- Sections visibility
- Custom badges

**Center panel — Live Preview**

Display the actual rendered README using a GitHub-compatible Markdown renderer and safely supported HTML.

Include:

- Desktop preview
- Mobile-width preview
- GitHub dark appearance
- GitHub light appearance
- Zoom controls
- Refresh preview
- Export preview

Do not claim pixel-perfect GitHub rendering unless it has been verified.

**Right panel — Code Editor**

Implement a professional Monaco-based Markdown editor with:

- Syntax highlighting
- Line numbers
- Search and replace
- Undo and redo
- Auto formatting where safe
- Copy Markdown
- Download Markdown
- Live synchronized preview

Changes in the editor should update the preview immediately.

Changes in visual controls should update the generated Markdown without unintentionally overwriting manual edits.

### 5. GitHub Profile Analyzer

Allow users to enter any valid public GitHub username.

Example:
`Dilanga-Malshan`

Fetch and analyze:

- Profile name
- Username
- Bio
- Location
- Website
- Public repositories
- Repository descriptions
- Programming languages
- Topics
- Stars
- Forks
- Recently updated projects
- Pinned repositories when available through an authorized supported API
- Public organization information where relevant

Handle pagination and GitHub API rate limits.

**Intelligent repository analysis**

Create a ranking algorithm that considers:

- Repository quality
- Description completeness
- Documentation
- Primary language
- Recency
- Popularity
- Project complexity indicators
- User selection

Never automatically assume repository stars indicate professional ability.

Do not invent work history, certifications, achievements, or technologies.

Allow the user to verify and correct AI-inferred skills and project descriptions.

### 6. AI README Generation Engine

Build a modular AI pipeline.

**Stage 1 — Data Extraction**

Fetch GitHub profile and repository metadata.

**Stage 2 — Profile Understanding**

Use structured output to determine:

- Professional identity
- Main programming languages
- Technical specialization
- Relevant projects
- Potential portfolio highlights
- Available social information

**Stage 3 — Content Generation**

Generate:

- Professional headline
- Personalized introduction
- About Me
- Tech Stack
- What I'm Working On
- Featured Projects
- GitHub Stats
- Social Links
- Optional Fun Facts
- Contact section

**Stage 4 — README Composition**

Compose valid GitHub Flavored Markdown and only GitHub-supported HTML.

Use reusable templates.

**Stage 5 — Validation**

Verify:

- Markdown syntax
- Safe image URLs
- Valid GitHub links
- No unsupported scripts
- No invented factual claims
- Well-structured sections
- Reasonable README length
- Accessible image alt text

**Stage 6 — Optimization**

Offer AI actions:

- Make More Professional
- Make More Minimal
- Make More Creative
- Improve Introduction
- Rewrite Project Descriptions
- Optimize for Recruiters
- Shorten Content
- Improve Readability
- Generate Alternative Version

All AI actions must preserve verified facts.

### 7. README Template Engine

Implement at least six high-quality templates:

1. Minimal Developer
2. Professional Engineer
3. Futuristic Neon
4. AI / Machine Learning Engineer
5. Full-Stack Developer
6. Creative Portfolio

Every template must support customization of:

- Heading alignment
- Colors
- Badges
- Tech icons
- Animations
- Project layout
- Section order
- Stats display
- Footer design

Make templates data-driven rather than hardcoded individually.

### 8. Visual README Components

Implement a reusable component library with:

- Animated typing headers
- SVG banner generators
- Programming language icons
- Skills badges
- GitHub statistics cards
- Top language cards
- Contribution streak widgets
- Social media badges
- Featured project cards
- Profile visitor counter
- Divider designs
- Animated footer banners

Support third-party widget integration with clear fallback behavior when an external service is unavailable.

Allow users to toggle any component independently.

### 9. AI Chat Assistant

Add an integrated AI assistant within the editor.

Example commands:

"Make my README look more professional."

"Highlight my Python and FastAPI projects."

"Create a futuristic AI engineer profile."

"Use a charcoal and neon-green color palette."

"Remove the GitHub stats section."

"Make my introduction shorter."

The assistant must understand the current README configuration and convert user instructions into structured, validated changes.

Show a preview of proposed changes before applying them.

Maintain undo history.

### 10. GitHub Authentication & Publishing

Implement secure GitHub OAuth authentication.

Users must be able to:

- Sign in with GitHub
- Import profile details
- Browse their repositories
- Select their profile README repository
- Preview proposed changes
- Commit README updates
- View publishing results

GitHub profile READMEs require a public repository with the same name as the account username and a README.md file in the repository root.

Before publishing:

1. Check repository existence.
2. Verify repository ownership and permissions.
3. Show the exact Markdown diff.
4. Require explicit user confirmation.
5. Create or update the README using GitHub's supported API.
6. Handle conflicts and missing permissions.
7. Never overwrite existing content silently.

Request the minimum necessary GitHub permissions.

Support README downloading without authentication.

### 11. Backend REST API

Design versioned FastAPI endpoints.

**GitHub**

- GET `/api/v1/github/profile/{username}`
- GET `/api/v1/github/repositories/{username}`
- POST `/api/v1/github/analyze`

**AI Generation**

- POST `/api/v1/ai/generate`
- POST `/api/v1/ai/rewrite`
- POST `/api/v1/ai/optimize`
- POST `/api/v1/ai/chat`

**README**

- POST `/api/v1/readmes`
- GET `/api/v1/readmes/{id}`
- PATCH `/api/v1/readmes/{id}`
- POST `/api/v1/readmes/{id}/render`
- GET `/api/v1/readmes/{id}/export`

**Templates**

- GET `/api/v1/templates`
- GET `/api/v1/templates/{id}`

**Publishing**

- POST `/api/v1/github/publish`
- GET `/api/v1/github/publish-status/{id}`

**Authentication**

- GET `/api/v1/auth/github/login`
- GET `/api/v1/auth/github/callback`
- POST `/api/v1/auth/logout`

Use consistent Pydantic request/response schemas, error handling, authentication dependencies, logging, and OpenAPI documentation.

Use idempotency and concurrency protection where necessary for publishing operations.

### 12. Database Architecture

Design normalized PostgreSQL tables for:

- users
- github_accounts
- github_profile_snapshots
- readme_projects
- readme_versions
- templates
- user_preferences
- generation_history
- publish_history

Include:

- UUID identifiers
- Foreign keys
- Appropriate indexes
- Creation timestamps
- Update timestamps
- Ownership validation
- Migration scripts

Encrypt sensitive stored tokens or avoid persisting them when practical.

### 13. Security Requirements

Implement:

- Input validation
- Output sanitization
- Prompt injection protection
- GitHub OAuth state validation
- Secure token handling
- CSRF defenses
- Strict CORS configuration
- Rate limiting
- Request timeouts
- API usage limits
- Safe Markdown rendering
- URL validation
- GitHub API error handling
- AI cost controls

Treat repository descriptions, README contents, GitHub metadata, and AI-generated text as untrusted input.

Never execute repository content or arbitrary user-supplied scripts.

### 14. Advanced Features

After completing the stable core application, implement:

- README version history
- Side-by-side diff viewer
- Drag-and-drop section reordering
- Custom color palette builder
- Shareable previews with privacy controls
- README quality analysis
- AI-powered section recommendations
- Multiple generated variants
- Project selection and ranking controls
- Import existing README
- Regenerate selected sections only
- Local autosave and authenticated cloud saves

### 15. Testing & Quality

Provide comprehensive automated testing.

**Backend**

- pytest
- pytest-asyncio
- httpx test client
- Mock GitHub API calls
- Mock AI responses
- Database integration tests

**Frontend**

- Component tests
- Service tests
- Form validation tests
- Markdown editor behavior tests
- E2E tests for critical user flows

**Critical test scenarios**

- Invalid GitHub username
- User with zero repositories
- Private repository access restrictions
- GitHub rate limit
- Missing OAuth permissions
- AI request failure
- Malicious Markdown content
- Failed publish
- Concurrent README update
- Existing README preservation
- Export without login

### 16. Development Structure

Use a clean, modular monorepo.

```
readme-ai/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   ├── shared/
│   │   │   ├── features/
│   │   │   ├── services/
│   │   │   └── layouts/
│   │   └── styles/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── ai/
│   │   └── templates/
│   ├── alembic/
│   └── tests/
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
```

Separate routing, business logic, persistence, AI orchestration, and external API integrations.

### 17. Implementation Phases

**Phase 1 — Foundation**

Initialize frontend, backend, database, project configuration, design system, and routing.

**Phase 2 — GitHub Intelligence**

Implement GitHub profile lookup, repository analysis, caching, and validation.

**Phase 3 — AI Generation**

Implement structured AI outputs, README composition, and reliable generation endpoints.

**Phase 4 — Studio**

Build premium dashboard, template selector, Markdown editor, live preview, and component controls.

**Phase 5 — Authentication and Publishing**

Implement secure GitHub OAuth, repository checks, diff preview, and explicit-confirmation publishing.

**Phase 6 — Advanced Features**

Add AI assistant, history, multiple variants, quality analysis, and editor enhancements.

**Phase 7 — Testing and Deployment**

Add automated tests, Docker configuration, environment setup, security review, and deployment documentation.

### 18. Deliverables

Generate:

1. Complete Angular frontend source code.
2. Complete Python FastAPI backend source code.
3. PostgreSQL database models and Alembic migrations.
4. Working AI integration with configurable models.
5. Functional GitHub API integration.
6. Secure OAuth and publishing workflow.
7. Beautiful responsive UI.
8. Live Markdown editor and renderer.
9. Customizable README templates.
10. Automated tests.
11. Docker Compose setup.
12. Environment variable example.
13. API documentation.
14. Local development setup instructions.
15. Production deployment guide.

### 19. Critical Execution Instructions

- Do not deliver only design mockups.
- Do not implement decorative buttons that have no functionality.
- Do not substitute hardcoded sample profiles for real GitHub integration.
- Use sample fixtures only for automated tests or an explicitly labeled demo mode.
- Do not use fabricated repository data.
- Do not hardcode API keys.
- Prefer maintainable, readable, typed code.
- Use actual API integrations and error handling.
- Verify framework and library compatibility before installing dependencies.
- Implement the product incrementally while preserving working functionality.
- Do not claim that tests pass unless executed.
- Clearly identify features requiring external credentials or configuration.
- When tools support file editing, create and modify actual project files rather than merely displaying code.
- If an integration cannot be completed, document the blocker instead of simulating success.

**Start by creating the application architecture, then implement Phase 1 and continue through the remaining phases in order.**

The final result must feel like a polished, commercial-grade AI developer tool, combining the usability of a visual design studio with intelligent, personalized GitHub README generation.
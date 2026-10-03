# 2. Architecture, Stack, Folders, Database, API

## Architecture
```
User → Privacy Questionnaire → Input Validation → Feature Extraction
        ┌──────────────────────────────┐
        │ Profile / Personal Info      │
        │ Location / Content           │   (per-category scoring in scoring_engine.py)
        │ Account Security / Social Eng│
        │ Third-party / Digital Footprint│
        └──────────────────────────────┘
→ Category Scores → Risk Scoring Engine → Overall Risk → Findings Engine
→ Recommendation Engine → Privacy Dashboard → Privacy Report
Optional anonymised aggregates → Analytics (synthetic cohort CSV)
```

## Technology stack
| | Option A - Beginner (**used**) | Option B - Modern |
|---|---|---|
| Frontend | HTML, CSS, vanilla JS (+ hand-written SVG charts, no CDN) | React |
| Backend | Python Flask | FastAPI |
| Database | SQLite | PostgreSQL / SQLite |
| Charts | Custom SVG (works offline) - Chart.js is a drop-in alternative | Recharts / Chart.js |
| Reports | HTML → browser "Save as PDF" | server-side PDF |

**Option A trade-offs:**

- **Advantages:** one command to run, nothing to build, easy to read.
- **Limits:** no type-checked API docs, manual state handling.
- **Recommendation for students:** start with A (this repo), then port the API to FastAPI and the UI to React.

## Folder guide
| Path | Purpose |
|---|---|
| `backend/app.py` | Flask app factory, rate limiting, security headers, error handlers |
| `backend/config.py` | Categories, weights, risk bands, limits (all tunable) |
| `backend/questionnaire.py` | The 53 questions + risk value per answer |
| `backend/knowledge_base.py` | Finding text, recommendations, priorities, risk-matrix values, checklist |
| `backend/routes/` | `api.py` (REST) and `pages.py` (serves the UI) |
| `backend/models/database.py` | SQLite schema + privacy-first storage functions |
| `backend/services/` | `assessment_engine`, `scoring_engine`, `findings_engine`, `recommendation_engine`, `improvement_simulator`, `report_service`, `analytics_service`, `metadata_service`, `demo_profile` |
| `backend/utils/` | validators, rate limiter, security headers |
| `frontend/` | `index`, `assessment`, `results`, `dashboard`, `checklist`, `tools` pages + `css/` + `js/` |
| `data/` | `generate_dataset.py` and the generated 1,200-row CSV |
| `tests/` | 54 automated tests (30 documented scenarios + privacy/security) |
| `docs/` | Everything in this folder |
| `reports/` | Where you may save exported reports (git-ignored) |
| `screenshots/` | Proof screenshots for GitHub/LinkedIn |

## Scoring maths
```
category_score = 100 × Σ(weight_q × risk_q) / Σ(weight_q)
overall        = Σ(category_weight × category_score) / Σ(category_weight)
points_q       = category_weight/Σ × weight_q×risk_q/Σ(weight in category) × 100     (exact contribution)
```
Default category weights (sum = 100):

- Profile 10
- Personal Info 15
- Location 15
- Content 10
- Connections 10
- Tagging 5
- Account Security 15
- Third-Party 5
- Social Engineering 10
- Footprint 5

Override with `CATEGORY_WEIGHTS_JSON`. *Weights and thresholds are educational assumptions that must be validated before professional use.*

## Database (privacy-first)
```
ASSESSMENTS(assessment_id PK, overall_score, risk_level, created_at)
CATEGORY_SCORES(category_score_id PK, assessment_id FK→ON DELETE CASCADE, category, score)
FINDINGS(finding_id PK, assessment_id FK→ON DELETE CASCADE, category, finding_type, severity, description, impact_points)
RECOMMENDATIONS(recommendation_id PK, finding_type UNIQUE, recommendation, priority)   -- static catalogue
```
No columns for phone, email, address, birth date, password, exact location, messages, IP addresses - **or the questionnaire answers themselves**.

## REST API
| Method & path | Request | Response | Notes |
|---|---|---|---|
| `POST /api/assessment` | `{"answers":{"A1":"PUBLIC",…}}` (all 53) | 201 + score, level, categories, findings, recommendations, `assessment_id` | Strict allow-list validation → 400 with details |
| `GET /api/assessment/{id}` | - | stored assessment view | 400 bad id format, 404 unknown |
| `GET /api/assessment/{id}/recommendations` | - | recommendations + counts + tips | |
| `GET /api/assessment/{id}/report[?download=1]` | - | standalone HTML report | CSP `default-src 'none'`, all values escaped |
| `DELETE /api/assessment/{id}` | - | `{"deleted":true}` | Hard delete, cascades |
| `POST /api/assessment/simulate-improvement` | `{"answers":…, "fix_findings":[…] \| "changes":{…} \| "fix_priority":"IMMEDIATE" \| "fix_all":true}` | before/after score, per-category change, applied changes, disclaimer | Stateless; nothing stored |
| `GET /api/dashboard/stats` | - | aggregates of the synthetic cohort | |
| `GET /api/privacy-checklist` | - | the 18-item checklist | |
| `GET /api/questionnaire`, `GET /api/demo`, `POST /api/metadata/inspect|strip` | - | questionnaire, fictional demo profile, local image tools | |

**API security notes:**

- **Authentication / authorisation:** there are no accounts (data minimisation). The unguessable assessment id (a random token) acts as a capability: only its holder can read or delete.
- **Rate limiting:** 120 requests/min and 20 writes/min per IP, kept in memory.
- **Errors:** generic JSON; no stack traces and no echo of submitted values.
- **Privacy:** answers are used in memory and discarded.
- **Simulator:** it receives answers from the browser tab (sessionStorage), so the server never remembers them.

## Privacy by design in this app
| Principle | Implementation |
|---|---|
| Data minimisation | Only scores/finding types stored; never the answers |
| Purpose limitation | Data used only to display your result and anonymous trends |
| Least privilege | No accounts, no external calls, localhost-bound, strict CSP |
| Privacy by default | Server binds to 127.0.0.1; nothing optional is switched on |
| Transparency | Landing page and README state exactly what is stored; scoring is open and explainable |
| User control | Delete button + API; checklist state stays in your browser |
| Retention limitation | Auto-purge after `RETENTION_DAYS` (default 30) |
| Secure processing | Validation, parameterised SQL, escaping, headers, rate limiting, tests |

# Social Media Privacy Risk Assessment Framework

> **This project is designed for defensive cybersecurity and privacy education. It uses synthetic or voluntarily provided assessment responses and does not scrape, track, or profile real social-media users.**

![Dashboard](screenshots/privacy_dashboard.png)

## Overview
- A privacy-risk assessment platform for social-media exposure.
- The user answers **53 questions about settings and habits** (never the sensitive data itself).
- The user receives:
  - A **0-100 Privacy Risk Score** and risk level
  - 10 category scores
  - Ranked weaknesses and prioritised recommendations
  - A what-if simulator
- Extras:
  - A printable checklist
  - An HTML/PDF report
  - An analytics dashboard built on a **1,200-record synthetic dataset**

## Problem Statement
- Oversharing and weak settings make doxxing, impersonation and social engineering easier.
- Typical weak spots: public phone number, live location, no MFA, open tagging.
- People rarely get structured, explainable feedback about their exposure.

## Objectives
- Assess exposure in 10 areas.
- Explain every point of the score.
- Recommend prioritised fixes.
- Simulate improvements.
- Educate users.
- Practise privacy-by-design.

## Cybersecurity Relevance
- Security awareness and privacy engineering
- GRC (governance, risk and compliance)
- IAM: MFA, recovery, sessions and third-party grants
- SOC-style account-takeover hygiene
- Application security: validation, XSS defence, rate limiting, secure headers and tests
- Details: [docs/01_PROJECT_EXPLANATION.md](docs/01_PROJECT_EXPLANATION.md)

## Privacy vs Security
- **Privacy:** control over what information is exposed.
- **Security:** protecting accounts from unauthorised access.
- **Strong account security ≠ strong privacy.**
- Example: a strong password and MFA do not hide a public phone number and live location.

## Features
- **Assessment:** 53-question wizard with input validation
- **Scoring:** feature extraction, 10 category scores, configurable weighted overall score, LOW / MODERATE / HIGH / CRITICAL
- **Guidance:** findings engine and recommendation engine (IMMEDIATE / IMPORTANT / GOOD PRACTICE)
- **Simulator:** improvement simulator showing before/after scores
- **Dashboard:** dense analytics dashboard with 15 panels
- **Outputs:** printable checklist, HTML/PDF report
- **Tools:** local photo-metadata viewer and cleaner
- **Platform:** SQLite privacy-first storage, REST API, 54 automated tests

## Architecture
```
User → Questionnaire → Validation → Feature Extraction → Category Analyzers
     → Scoring Engine → Overall Risk → Findings → Recommendations → Dashboard → Report
```
Details and diagrams: [docs/02_ARCHITECTURE_AND_API.md](docs/02_ARCHITECTURE_AND_API.md).

## Technology Stack
Python 3.10+ · Flask · SQLite · Pillow (metadata tool) · HTML/CSS/vanilla JS · hand-written SVG charts (no CDN, works offline) · pytest.

## Privacy Questionnaire
- 53 questions in 10 categories (A-J). Full list: [docs/QUESTIONNAIRE.md](docs/QUESTIONNAIRE.md)
- Answer styles: PUBLIC / FRIENDS / PRIVATE, YES / NO / SOMETIMES / NOT SURE, and similar.
- No phone numbers, addresses, passwords or birth dates are ever typed.

## Risk Categories & Weights
- Profile: **10**
- Personal Info: **15**
- Location: **15**
- Content: **10**
- Connections: **10**
- Tagging: **5**
- Account Security: **15**
- Third-Party Apps: **5**
- Social Engineering: **10**
- Digital Footprint: **5**
- Configurable in `backend/config.py` or with `CATEGORY_WEIGHTS_JSON`.

## Risk Scoring
- **Category score:** `100 × Σ(w·risk) / Σw`
- **Overall score:** `Σ(categoryWeight × category) / Σ weights`
- **Risk levels:**
  - 0-20 = LOW
  - 21-40 = MODERATE
  - 41-70 = HIGH
  - 71-100 = CRITICAL
- Higher score = higher exposure.
- *Weights and thresholds are educational assumptions and must be validated before professional risk decisions.*
- *The score is not a guarantee that an account will or will not be compromised.*

## Privacy Findings / Recommendation Engine / Improvement Simulator
- **Findings:** `generate_privacy_findings()` ranks risky answers by their exact point contribution.
- **Recommendations:** `generate_recommendations()` prioritises the fixes.
- **Simulator:** `simulate_improvement()` re-scores a copy of your answers with the chosen fixes (for example 72 → 34, a 38-point reduction).
- The simulator is labelled as a *framework simulation*.

## Digital Footprint · Social Engineering Awareness · Account Security
- Covered by categories **J** (footprint), **I** (social engineering) and **G** (account security).
- Defensive guidance is in the docs.
- No attack scripts or message templates exist in this repository.

## Privacy Dashboard
- Open `/dashboard`.
- **Top row:** 6 KPI cards.
- **Category views:** radar, category breakdown, gauge.
- **Weaknesses and controls:** top weaknesses, account-security controls, digital-footprint panel.
- **Improvement:** before/after comparison, biggest single wins, heat-map.
- **Cohort views:** risk distribution, histogram, 12-month trend, segment comparison.
- **Guidance:** action plan and awareness corner.
- Works with your own assessment or the fictional demo profile.

## Privacy Report
- Route: `/api/assessment/{id}/report` returns a standalone HTML report.
- Contents:
  - Assessment ID and date
  - Score and level
  - Category scores
  - Findings and recommendations
  - Priority actions
  - Checklist and disclaimer
- Use *Print → Save as PDF* to export.
- No sensitive data is included.

## Privacy by Design
- **Data minimisation:** only scores and finding types are stored, never answers.
- **Purpose limitation:** data is used only to show your result.
- **Least privilege:** no accounts and no external calls.
- **Privacy by default:** the server binds to 127.0.0.1.
- **Transparency:** scoring is open and explainable.
- **User control:** you can delete your assessment at any time.
- **Retention limitation:** records auto-delete after 30 days.
- **Secure processing:** validation, escaping, headers and rate limiting.

## Installation
```bash
# 1. Create project folder and unzip / clone into it
cd Social-Media-Privacy-Risk-Assessment
# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
# 3. Dependencies
pip install -r requirements.txt
# 4. (optional) regenerate the synthetic dataset
python data/generate_dataset.py
# 5. Start (backend + frontend are served together)
python -m backend.app
# 6. Open http://127.0.0.1:5000
```

## Usage
1. Open **Assessment** (or click *Fill with demo profile*).
2. Answer all 10 sections, then click *Calculate my score*.
3. Review the score, radar, findings and recommendations.
4. Tick fixes in the **Simulator** and watch the score change.
5. Open the **Dashboard** to compare with the cohort.
6. Click *View report*, then Print → Save as PDF.
7. Use the **Checklist** and the **Metadata Tool**.
8. Click *Delete my assessment* when done.

## API Documentation
- Full details: [docs/02_ARCHITECTURE_AND_API.md](docs/02_ARCHITECTURE_AND_API.md)
- Main routes:
  - `POST /api/assessment`
  - `GET /api/assessment/{id}`
  - `GET /api/assessment/{id}/recommendations`
  - `POST /api/assessment/simulate-improvement`
  - `GET /api/dashboard/stats`
  - `GET /api/privacy-checklist`
  - `DELETE /api/assessment/{id}`

## Testing
```bash
python -m pytest -v                 # 54 tests
python -m tests.run_test_report     # regenerates docs/TEST_REPORT.md
python scripts/generate_docs.py     # regenerates QUESTIONNAIRE / DEMO_RESULTS / RISK_MATRIX docs
```
## Security & Privacy Testing
See [docs/SECURITY_PRIVACY_TESTING.md](docs/SECURITY_PRIVACY_TESTING.md).

## Results
- **Demo profile:** **79/100 CRITICAL → 50/100 HIGH** after the brief's improvements (−29 pts). See [docs/DEMO_RESULTS.md](docs/DEMO_RESULTS.md).
- **Synthetic cohort (n = 1,200):**
  - Average score ≈ 44
  - LOW ≈ 18%
  - MODERATE ≈ 26%
  - HIGH ≈ 42%
  - CRITICAL ≈ 13%

## Limitations
- Answers are self-reported.
- Weights are assumed, not empirically calibrated.
- The dataset is synthetic.
- Platform settings change over time.
- The model measures exposure, not the likelihood of compromise.

## Future Improvements
- Platform-specific checklists
- Organisational policies
- Awareness quizzes
- Privacy-maturity scoring
- Family and teen modules
- Enterprise training and GRC reporting
- Model calibration
- Localisation and accessibility
- Report comparison over time
- Local-only mode
- No scraping or invasive monitoring

## Screenshots
See [`screenshots/`](screenshots/) and the checklist in [docs/04_GITHUB_AND_PROOF.md](docs/04_GITHUB_AND_PROOF.md).

## Learning Outcomes
- Risk modelling
- Privacy engineering
- Secure API design
- Threat modelling
- Data analytics
- Testing
- Ethical, defensive project scoping

## Ethical Disclaimer
- Defensive education only.
- Use synthetic data or your own voluntary answers.
- Do not use this project to scrape, profile or track anyone.
- Do not use it to access any real person's accounts.

## Author
*Shikha* - Cybersecurity student

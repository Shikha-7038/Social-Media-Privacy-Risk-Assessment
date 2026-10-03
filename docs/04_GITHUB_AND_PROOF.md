# 4. GitHub Upload Strategy, Proof Checklist, Resume & LinkedIn

**Repository name:** `Social-Media-Privacy-Risk-Assessment`
**Description:**

- Privacy-focused cybersecurity framework for assessing social-media exposure.
- Covers account-security practices, social-engineering risk and digital-footprint risk.
- Gives personalised privacy improvements.
- Uses synthetic or self-reported data only.
**Topics:**

- cybersecurity, privacy, social-media-privacy, privacy-risk
- security-awareness, python, flask, fastapi
- digital-footprint, risk-assessment, grc
- privacy-by-design, defensive-security

## Exact Git commands
```bash
cd Social-Media-Privacy-Risk-Assessment
git init
git add .
git commit -m "Initialize social media privacy risk assessment"
git branch -M main
git remote add origin <repository-url>      # create an empty repo on github.com first
git push -u origin main
```
## Recommended commit history (shows real progress)
Instead of one big commit, stage in this order (`git add <paths>` then commit):
1. `Create privacy assessment architecture` - folders, `config.py`, `.gitignore`, `.env.example`
2. `Add privacy questionnaire` - `backend/questionnaire.py`, `docs/QUESTIONNAIRE.md`
3. `Generate synthetic assessment dataset` - `data/`
4. `Implement privacy feature extraction` - `assessment_engine.py`
5. `Add category risk scoring` - `scoring_engine.py`
6. `Implement overall privacy risk engine` - classification + weights
7. `Add privacy findings engine` - `findings_engine.py`, `knowledge_base.py`
8. `Implement recommendation engine` - `recommendation_engine.py`
9. `Build privacy improvement simulator` - `improvement_simulator.py`
10. `Create privacy analytics dashboard` - `frontend/dashboard.html`, `js/charts.js`, `js/dashboard.js`, `analytics_service.py`
11. `Add privacy assessment report` - `report_service.py`
12. `Implement privacy-by-design controls` - `database.py`, validators, rate limiter, headers
13. `Add automated privacy tests` - `tests/`
14. `Complete README and documentation` - `README.md`, `docs/`, `screenshots/`

## Screenshot / proof checklist
Run `python -m backend.app`, then capture with these filenames in `screenshots/`:
| # | Capture | Filename |
|---|---|---|
| 1 | Project folder structure | `01_project_structure.png` |
| 2 | Architecture diagram (docs) | `02_architecture_diagram.png` |
| 3 | Assessment homepage | `03_homepage.png` ✔ provided |
| 4-9 | Questionnaire + sections (profile, personal info, location, account security, social engineering) | `04_questionnaire_profile_section.png` ✔, `05_…personal_info.png`, `07_location_section.png` ✔, `08_account_security_section.png` ✔, `09_social_engineering_section.png` |
| 10-14 | Overall score, category scores, radar chart, top findings, recommendations | `10_results_overview.png` ✔ (covers 10-14) |
| 15-17 | Simulator before / after / risk reduction | `15_simulator_before.png`, `16_simulator_after.png`, `17_risk_reduction.png` |
| 18-20 | Dashboard, distribution, top-weakness chart | `18_privacy_dashboard.png` ✔ |
| 21 | Privacy checklist | `21_privacy_checklist.png` ✔ |
| 22 | Privacy report | `22_privacy_report.png` |
| 23 | Synthetic dataset (CSV in editor) | `23_synthetic_dataset.png` |
| 24-25 | Automated tests / security tests | `24_pytest_results.png`, `25_security_tests.png` |
| 26 | Database schema | `26_database_schema.png` |
| 27-29 | GitHub commits, repository, README preview | `27_…`, `28_…`, `29_…` |

## Resume bullets
* Built a **privacy-by-design social-media risk assessment framework** (Python/Flask/SQLite) scoring 53 self-reported controls across 10 weighted categories into an explainable 0-100 score with LOW-CRITICAL classification and prioritised remediation.
* Engineered a **what-if improvement simulator and analytics dashboard** over 1,200 synthetic profiles; validated with **54 automated tests** (scoring boundaries, XSS, injection, rate limiting, data-deletion).
* Applied **GRC and data-minimisation principles**: stored only scores and finding types (never answers or PII), added retention limits, strict CSP/validation, threat model and risk matrix.

**Short description:**

- Defensive privacy-risk platform that turns a 53-question self-assessment into a 0-100 risk score.
- Gives ranked findings and a simulator showing how much each setting change reduces exposure.
- Uses only synthetic or self-reported data and stores no personal information.

**LinkedIn description:**

- I built the *Social Media Privacy Risk Assessment Framework*, a defensive cybersecurity project.
- Users answer questions about settings and habits, never sharing the data itself.
- The engine scores 10 categories:
  - Profile visibility
  - Personal info
  - Location
  - Content
  - Connections
  - Tagging
  - Account security
  - Third-party apps
  - Social engineering
  - Digital footprint
- It returns an explainable score, prioritised recommendations and a what-if simulator.
- It demonstrates:
  - Privacy-by-design
  - Risk scoring
  - Secure API design
  - Data analytics on a 1,200-record synthetic dataset
  - Threat modelling
  - Automated security testing
- No real profiles are scraped or tracked.

**Skills:**

- Cybersecurity, Privacy Risk Assessment, Privacy by Design
- Digital Footprint Analysis, Social Engineering Awareness
- Risk Scoring, GRC concepts, Threat Modelling
- Python, Flask, SQLite, REST APIs
- Data Analytics, Security Awareness, pytest

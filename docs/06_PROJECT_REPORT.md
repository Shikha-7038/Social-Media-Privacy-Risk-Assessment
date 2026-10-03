# Project Report - Social Media Privacy Risk Assessment Framework

## Abstract
- A defensive, privacy-by-design framework that evaluates social-media exposure from self-reported settings and behaviours.
- A 53-question questionnaire feeds a transparent scoring engine.
- Outputs:
  - Category scores
  - An overall 0-100 risk score
  - Ranked findings
  - Personalised recommendations
  - A what-if simulator
- A 1,200-record synthetic dataset powers an analytics dashboard.
- The system stores no personal data and is explicitly educational.

## Introduction & Problem Statement
- Oversharing and weak settings enable doxxing, impersonation and social engineering.
- Individuals rarely get structured, understandable feedback about their exposure.
- Hiring teams, schools and organisations increasingly care about online footprints and data minimisation.

## Objectives
- Assess exposure across ten areas.
- Give explainable scores.
- Recommend prioritised fixes.
- Simulate improvements.
- Educate users.
- Follow privacy-by-design without scraping or profiling anyone.

## Background
- **Privacy vs security:** see docs/01.
- **Digital footprint:** active (shared on purpose) vs passive (collected by use).
- **Social engineering:** exploitation of trust using public context.
- **Existing approaches:**
  - Vendor privacy check-ups: platform-specific and unscored.
  - Generic cyber-hygiene quizzes: little coverage of exposure.
  - OSINT tools: invasive, so deliberately **not** used here.

## Proposed Framework
- **Architecture:** questionnaire → validation → feature extraction → category analyzers → scoring → findings → recommendations → dashboard → report (see docs/02).
- **Questionnaire design:** questions ask about settings and behaviours only; "NOT SURE" counts as partial risk.
- **Synthetic dataset:**
  - 1,200 records.
  - Generated from a hidden awareness variable per profile, so answers correlate realistically.
  - Scored by the same engine as the app.
- **Feature engineering:** `extract_privacy_features()` maps each answer to a risk value (0-1) with a weight.
- **Category analysis and scoring:**
  - Weighted means.
  - Overall score from configurable weights.
  - Bands: 0-20, 21-40, 41-70, 71-100.
- **Findings engine:** risk ≥ 0.5 raises a finding, ranked by exact points.
- **Recommendation engine:** IMMEDIATE / IMPORTANT / GOOD PRACTICE.
- **Simulator:** re-scores a copy of the answers with the chosen fixes.
- **Specialised analysis areas:**
  - Account security (category G)
  - Third-party apps (category H)
  - Location privacy (category C)
  - Digital footprint (category J)

## Privacy Dashboard & Privacy by Design
- **Dashboard:** dense 12-column layout with:
  - KPIs, radar, category bars and gauge
  - Weaknesses, controls adoption and footprint
  - Improvement comparison, biggest wins and heat-map
  - Distribution, histogram, trend and segments
  - Action plan
- **Privacy by design:** the full table is in docs/02.

## Testing & Results
- **Tests:** 54 pass (see docs/TEST_REPORT.md).
- **Synthetic cohort (seed 42):**
  - LOW ≈ 18%
  - MODERATE ≈ 26%
  - HIGH ≈ 42%
  - CRITICAL ≈ 13%
  - Average ≈ 44
- **Effect of fixes on the cohort:**
  - Fixing only IMMEDIATE items: average falls from about 44 to about 32.
  - Fixing everything: average falls to about 3.
- **Demo profile:** 79 (CRITICAL) → 50 (HIGH) after the brief's listed improvements (see DEMO_RESULTS.md).

## Limitations
- Self-reported data can be inaccurate.
- Weights and thresholds are assumptions, not empirically calibrated.
- Synthetic data does not represent real populations.
- Platform settings differ and change.
- The model measures exposure categories, not the likelihood of actual compromise.

## Future Scope
- Platform-specific checklists
- Configurable organisational policies
- Awareness quizzes
- Privacy-maturity scoring
- Teen and family safety modules
- Enterprise training
- Anonymous trend reporting
- Model calibration
- Localisation and accessibility
- Report comparison over time
- Client-side-only mode
- No invasive monitoring or scraping

## Conclusion
- Privacy exposure can be measured, explained and reduced.
- The approach is transparent, ethical and useful for learning.
- The framework itself practises data minimisation.

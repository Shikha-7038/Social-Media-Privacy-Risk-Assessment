# Project Report - Social Media Privacy Risk Assessment Framework

## Abstract
This project presents a defensive, privacy-by-design framework that evaluates social-media exposure from self-reported settings and behaviours. A 53-question questionnaire feeds a transparent scoring engine producing category scores, an overall 0-100 risk score, ranked findings, personalised recommendations and a what-if simulator. A 1,200-record synthetic dataset powers an analytics dashboard. The system stores no personal data and is explicitly educational.

## Introduction & Problem Statement
Oversharing and weak settings enable doxxing, impersonation and social engineering, yet individuals rarely get structured, understandable feedback about their exposure. Hiring teams, schools and organisations increasingly care about online footprints and data minimisation.

## Objectives
Assess exposure across ten areas; give explainable scores; recommend prioritised fixes; simulate improvements; educate; and follow privacy-by-design without scraping or profiling anyone.

## Background
**Privacy vs security** (see docs/01). **Digital footprint:** active vs passive. **Social engineering:** exploitation of trust using public context.
**Existing approaches:** vendor privacy check-ups (platform-specific, unscored), generic cyber-hygiene quizzes (little on exposure), and OSINT tools (invasive; deliberately *not* used here).

## Proposed Framework
Architecture: questionnaire → validation → feature extraction → category analyzers → scoring → findings → recommendations → dashboard → report (docs/02). **Questionnaire design:** setting/behaviour questions only; NOT SURE treated as partial risk. **Synthetic dataset:** 1,200 records generated from a hidden awareness variable per profile so answers correlate realistically; scored by the same engine. **Feature engineering:** `extract_privacy_features()` maps answers to risk 0-1 with weights. **Category analysis & scoring:** weighted means; overall via configurable weights; bands 0-20/21-40/41-70/71-100. **Findings engine:** risk ≥ 0.5 → finding, ranked by exact points. **Recommendation engine:** IMMEDIATE / IMPORTANT / GOOD PRACTICE. **Simulator:** re-scores a copy with chosen fixes. **Account security, third-party apps, location privacy and digital-footprint analysis** are implemented as questionnaire categories G, H, C, J with dedicated findings and advice.

## Privacy Dashboard & Privacy by Design
Dense 12-column dashboard: KPIs, radar, category bars, gauge, weaknesses, controls adoption, footprint, improvement comparison, biggest wins, heat-map, distribution, histogram, trend, segments, action plan. Privacy by design table in docs/02.

## Testing & Results
54 tests pass (docs/TEST_REPORT.md). Synthetic cohort (seed 42): ~18% LOW, ~26% MODERATE, ~42% HIGH, ~13% CRITICAL; average ≈ 44. Fixing only IMMEDIATE items lowers the cohort average from about 44 to about 32; fixing everything to about 3. The fictional demo profile scores 79 (CRITICAL) and 50 (HIGH) after the brief's listed improvements (see DEMO_RESULTS.md).

## Limitations
Self-reported data can be inaccurate; weights/thresholds are assumptions, not empirically calibrated; synthetic data do not represent real populations; platform settings differ and change; the model measures exposure categories, not actual compromise likelihood.

## Future Scope
Platform-specific checklists, configurable organisational policies, awareness quizzes, privacy-maturity scoring, teen/family safety modules, enterprise training and anonymous trend reporting, model calibration, localisation, accessibility, report comparison over time, client-side-only mode. No invasive monitoring or scraping.

## Conclusion
The framework shows that privacy exposure can be measured, explained and reduced in a way that is transparent, ethical and useful for learning, while itself practising data minimisation.

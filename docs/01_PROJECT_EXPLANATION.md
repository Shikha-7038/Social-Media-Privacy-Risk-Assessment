# 1. Project Explanation (Beginner-Friendly)

> **Educational framework.** The score is based on self-reported answers. It is *not* a guarantee that an account will or will not be compromised.

## A. Simple explanation
| Term | Plain-English meaning |
|---|---|
| **Social-media privacy** | Your control over *who can see what* about you on social platforms. |
| **Digital footprint** | The trail of information about you online. **Active** = what you deliberately share (posts, bio). **Passive** = what is collected as you use services (e.g. device data). This project scores only *self-reported* practices. |
| **Personal-information exposure** | Details such as phone, email, birthday, workplace that strangers can see. |
| **Oversharing** | Posting more than needed (live location, travel plans, documents in photos). |
| **Social engineering** | Tricking people (not hacking machines) into revealing information or acting. Public details make the trick more believable. |
| **Identity-related risk** | Impersonation, fake accounts or fraud made easier by exposed details. |
| **Location exposure** | Live locations, geotags and check-ins reveal where you are and when you are away. |
| **Why public profiles raise exposure** | Visibility is not automatically unsafe, but it increases how much information is *potentially accessible* to anyone. |
| **Why historical posts matter** | Old posts stay searchable; things that felt fine years ago may expose school, home or habits today. |
| **Why review settings regularly** | Platforms add features and change defaults, so settings drift. |
| **How MFA helps** | A stolen password alone is not enough: the attacker also needs your second factor. |

## B. Technical explanation
Answers → **allow-list validation** → **feature extraction** (each answer becomes a risk value 0–1 with a weight) → **category scores** (weighted mean, 0–100) → **overall score** (configurable category weights) → **classification** (0–20 LOW, 21–40 MODERATE, 41–70 HIGH, 71–100 CRITICAL) → **findings** (answers with risk ≥ 0.5, ranked by exact point contribution) → **recommendations** (prioritised) → **dashboard** → **report**.

```
User → Privacy Questionnaire → Input Validation → Privacy Feature Extraction
     → Category Risk Analysis → Risk Scoring Engine → Overall Score
     → Risk Classification → Personalised Recommendations
     → Privacy Dashboard → Privacy Assessment Report
```
Because the model is linear, every answer contributes an *exact number of points*; this makes findings explainable ("this adds +4.0 points") and the simulator exact.

## Privacy vs Security
* **Privacy** controls how personal information is collected, shared, exposed and used.
* **Security** protects systems, accounts and information from unauthorised access or misuse.
* **Strong account security ≠ strong privacy.**

| Scenario | Security | Privacy |
|---|---|---|
| Strong unique password + MFA, but phone, birthday and live location are public | Strong | Weak |
| Private profile, but the same weak password is reused everywhere | Weak | Strong |
| Friends can tag you freely; your own posts are minimal | Strong | Weak (others expose you) |
| Authenticator-app MFA + tag review + private profile | Strong | Strong |

## Topic notes (what the code evaluates)
* **Profile visibility (A):** public / friends / private, search-engine indexing, friends-list visibility, contact look-up. Visibility is not unsafe by itself; it widens potential access.
* **Personal information (B):** only *"is it visible? YES/NO"* is asked. The app never collects the value itself.
* **Location (C):** real-time sharing, geotags, check-ins, travel posts, routines. Posting a photo *after* you leave a place reduces immediate exposure versus broadcasting a live location. No tracking is performed.
* **Photos & metadata:** photos can reveal location context, workplace, school, vehicles, badges, documents, screens, family and travel. **EXIF** is hidden data (device, time, sometimes GPS) embedded in image files. The optional *Metadata Tool* reads a file you choose, shows only what is present, and creates a cleaned copy. It is processed in memory by your own local server and not stored.
* **Social engineering (I):** unknown connections, suspicious DMs, unexpected links, shared verification codes, impersonation, fake giveaways. No attack scripts exist in this project.
* **Account security (G):** MFA (and method), unique password, password manager, login alerts, recovery info, sessions, unknown devices. Privacy risk and account-security risk overlap but are not identical.
* **Third-party apps (H):** apps, unused integrations, permissions, "Sign in with…". **Principle of least privilege:** grant only the access needed and revoke the rest.
* **Tagging (F):** another person's post can expose you even if you post very little. Enable tag review.
* **Digital footprint (J):** old posts, old accounts, public comments, review habits; recommend a periodic privacy review.

## 2. Industry relevance
| Area | How the project relates |
|---|---|
| Cybersecurity / SOC | Account-takeover and phishing risk factors, MFA/alerts/session hygiene. |
| Privacy engineering | Data minimisation, purpose limitation, privacy-by-design implemented in code. |
| Security awareness | Plain-language findings, checklist, micro-lessons. |
| Enterprise security & training | Same model can power employee privacy training (see Future Improvements). |
| Digital-risk management / identity protection | Quantifies exposure that fuels impersonation and doxxing. |
| Security consulting & GRC | Transparent, configurable weights; risk matrix; evidence-style reports. |
| Application security | Input validation, XSS defences, rate limiting, secure headers, safe storage, tests. |
| IAM | MFA method, recovery, sessions, third-party grants (least privilege). |

**Roles:** Cybersecurity Analyst, Privacy Analyst, GRC Analyst, SOC Analyst, Security Consultant, IAM Analyst, Security Awareness Specialist, Privacy Engineer.
**Skills shown:** risk modelling, secure API design, privacy-by-design, data analysis (1,200-record synthetic dataset), threat modelling, testing, documentation, ethical judgement.

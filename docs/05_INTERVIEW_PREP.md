# 5. Interview Preparation (10 questions + answers)

## 1. Explain your project.
- I built a defensive **Social Media Privacy Risk Assessment Framework**.
- A user answers 53 questions about their *settings and habits*, such as "is your phone number publicly visible?". They never enter the data itself.
- A Python engine then:
  - Validates the answers.
  - Converts them into weighted risk features.
  - Scores 10 categories from 0-100.
  - Combines them with configurable weights into an overall score.
  - Classifies it as LOW, MODERATE, HIGH or CRITICAL (higher = more exposure).
- It also produces:
  - Ranked findings
  - Prioritised recommendations
  - A what-if simulator
  - A dashboard compared with a 1,200-record synthetic cohort
- It stores only scores and finding types.

## 2. What is the difference between privacy and security, and how does the project show it?
- **Security** protects accounts and systems from unauthorised access.
- **Privacy** controls how personal information is exposed.
- A profile can have a strong password and MFA yet still publish a phone number and live location.
- My questionnaire separates the two:
  - Category G covers account security.
  - Categories B, C and D cover exposure.
- The score shows that the two can disagree.

## 3. What is a digital footprint?
- It is the trail of information about you online.
- **Active footprint:** what you deliberately share.
- **Passive footprint:** what is collected through usage.
- The project evaluates only self-reported practices:
  - Reviewing old posts
  - Unused accounts
  - Public comments
- It recommends a periodic review.

## 4. How does social engineering relate to oversharing?
- Scammers can use public context (employer, college, travel plans, family) to make messages believable.
- So I score both exposure and behaviours:
  - Accepting unknown requests
  - Clicking unexpected links
  - Sharing verification codes
- The awareness content is purely defensive, with no attack scripts.

## 5. How does your scoring work, and how do you justify the weights?
- Each answer has a **risk value (0-1)** and a **weight**.
- **Category score** = weighted mean × 100.
- **Overall score** = weighted mean of categories, using default weights such as Account Security 15% and Location 15%.
- The model is linear, so each finding has an exact point contribution.
- I state clearly that the weights and thresholds are **educational assumptions** that need validation.
- They are configurable through an environment variable.

## 6. What does data minimisation mean in your app?
- Collect and keep only what is necessary.
- I never ask for the sensitive values.
- I don't even store the answers.
- Only these are stored:
  - Assessment ID
  - Overall score and level
  - Category scores
  - Finding types
- Data auto-expires and can be deleted through the API.

## 7. Why is MFA important, and which method do you recommend?
- MFA means a stolen or reused password is not enough to take over an account.
- Authenticator apps or hardware keys are stronger than SMS.
- SMS can be intercepted or SIM-swapped.
- My model scores them as:
  - Authenticator or key: 0 risk
  - SMS: 0.5 risk (partial)
  - No MFA: 1.0 risk

## 8. How do you treat third-party applications?
- I apply the **principle of least privilege**:
  - Review connected apps.
  - Remove unused ones.
  - Check permissions before connecting.
  - Limit "Sign in with…" use.
- Apps keep access after you stop using them, so they are a silent exposure.

## 9. What is Privacy by Design, and where do you apply it?
- It means building privacy in from the start.
- Principles and where they appear in the app:
  - **Data minimisation:** scores only, never answers.
  - **Purpose limitation:** data is used only to show your result.
  - **Privacy by default:** the server binds to localhost.
  - **Transparency:** open, explainable scoring.
  - **User control:** a delete button and API.
  - **Retention limit:** auto-purge after 30 days.
  - **Secure processing:** validation, CSP and rate limiting.
- Each principle maps to specific code, listed in the README.

## 10. How did you test it?
- **54 automated tests.**
- **30 documented scenarios:**
  - Private and public profiles
  - Each risk factor
  - The 20/40/70 score boundaries
  - Score calculations
  - Database save
  - No sensitive data stored
  - Report generation
- **Security tests:**
  - Input validation
  - XSS
  - SQL-injection attempts
  - Rate limiting
  - Deletion cascade
  - Security headers
  - The metadata cleaner
- I also verified the UI in a real browser.

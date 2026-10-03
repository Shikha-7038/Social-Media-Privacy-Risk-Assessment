# 5. Interview Preparation (10 questions + answers)

**1. Explain your project.**
I built a defensive Social Media Privacy Risk Assessment Framework. A user answers 53 questions about their *settings and habits* - for example "is your phone number publicly visible?" - never the data itself. A Python engine validates the answers, converts them into weighted risk features, scores ten categories from 0-100, combines them with configurable weights into an overall score, and classifies it LOW, MODERATE, HIGH or CRITICAL, where higher means more exposure. It then lists ranked findings, prioritised recommendations, a what-if simulator and a dashboard compared with a 1,200-record synthetic cohort. It stores only scores and finding types.

**2. What is the difference between privacy and security, and how does the project show it?**
Security protects accounts and systems from unauthorised access; privacy controls how personal information is exposed. A profile can have a strong password and MFA yet publish a phone number and live location. My questionnaire separates them: Category G covers account security, while B, C and D cover exposure, and the score shows both can disagree.

**3. What is a digital footprint?**
The trail of information about you online: active footprint is what you deliberately share, passive is what is collected through usage. I evaluate only self-reported practices such as reviewing old posts, unused accounts and public comments, and recommend periodic review.

**4. How does social engineering relate to oversharing?**
Scammers can use public context - employer, college, travel plans, family - to make messages believable. So I score behaviours (accepting unknown requests, clicking unexpected links, sharing verification codes) and exposure together, and the awareness content is purely defensive; there are no attack scripts.

**5. How does your scoring work and how do you justify the weights?**
Each answer has a risk value 0-1 and a weight; category score = weighted mean ×100; overall = weighted mean of categories using default weights such as Account Security 15% and Location 15%. The model is linear, so each finding has an exact point contribution. I state clearly that weights and thresholds are educational assumptions needing validation, and they're configurable through an environment variable.

**6. What does data minimisation mean in your app?**
Collect and keep only what is necessary. I never ask for the sensitive values, and I don't even store the answers - only assessment ID, overall score, level, category scores and finding types. Data auto-expires and can be deleted via API.

**7. Why is MFA so important and which method would you recommend?**
MFA means a stolen or reused password isn't enough. Authenticator apps or hardware keys are stronger than SMS, which can be intercepted or SIM-swapped. My model rewards authenticator/key (0 risk), scores SMS partially (0.5) and no MFA fully (1.0).

**8. How do you treat third-party applications?**
Under the principle of least privilege: review connected apps, remove unused ones, check permissions before connecting, limit "Sign in with…". Apps keep access after you stop using them, so they're a silent exposure.

**9. What is Privacy by Design and where do you apply it?**
Building privacy in from the start: data minimisation, purpose limitation, privacy by default (localhost binding), transparency, user control (delete), retention limit and secure processing (validation, CSP, rate limiting). Each principle maps to a specific piece of code in the README.

**10. How did you test it?**
54 automated tests: 30 documented scenarios (private/public profiles, each risk factor, 20/40/70 boundaries, calculations, DB save, no sensitive data, report generation) plus security tests for validation, XSS, SQL-injection attempts, rate limiting, deletion cascade, headers and the metadata cleaner. I also verified the UI in a real browser.

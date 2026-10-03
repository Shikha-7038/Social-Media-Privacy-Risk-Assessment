# 3. Threat Model (defensive) and Privacy Risk Matrix

Scope: a **fictional** social-media user. Purpose: help the user *reduce* exposure. No attack instructions.

| Asset | Threat | Exposure | Potential impact | Existing control (in framework) | Recommended control |
|---|---|---|---|---|---|
| Account | Account takeover | Weak/reused password, no MFA, no alerts | Loss of account, abuse of contacts | MFA / password / alert questions (Category G) | App-based MFA, password manager, login alerts, review sessions |
| Identity information | Impersonation | Public birthday, workplace, photos, same handle | Fake profiles, fraud | Personal-info + profile checks | Hide details, unique handles, report fakes |
| Contact information | Phishing / spam | Public phone / email | Targeted scams, SIM-swap attempts | `PHONE_PUBLIC`, `EMAIL_PUBLIC` findings | Hide contact info, alias email |
| Location privacy | Unwanted profiling / physical-safety risk | Live location, geotags, check-ins, travel | Stalking risk, home-absence exposure | Category C | Post after leaving, disable geotags |
| Private content | Oversharing / leakage | Public posts, sensitive photo backgrounds | Doxxing, reputational harm | Category D | Friends-only default, blur/crop |
| Social relationships | Social engineering | Unknown connections, public friends list | Believable scams via trust | Category E, I | Verify requests, hide lists, verify urgent asks |
| Third-party access | Over-privileged apps | Old integrations, broad permissions | Data leakage via apps | Category H | Review/revoke, least privilege |
| Others' content | Tag-based exposure | Open tagging | Information you never posted appears | Category F | Tag review, restrict tagging |

## Privacy risk matrix
Likelihood and impact are **educational estimates**; real risk depends on context. The full per-finding matrix (53 rows) is generated in **RISK_MATRIX.md**.

| Example | Likelihood | Impact |
|---|---|---|
| Public phone number | Medium | Medium |
| Real-time location exposure | Medium | High |
| MFA disabled | Medium | High |
| Password reuse | High | High |
| Unknown connections accepted | High | Medium |

## Social-engineering awareness: how oversharing can increase risk
- Scammers may use **publicly available context** to make a message feel genuine.
- Information that adds believability:
  - **Employer:** fake "HR/IT" notices
  - **College:** fake "scholarship/exam" messages
  - **Travel plans:** fake "emergency abroad" requests
  - **Family references:** urgent "relative needs help" stories
  - **Interests:** tailored giveaways
  - **Public events:** fake ticket/refund offers
- Defences:
  - Share less publicly.
  - Verify through a second channel.
  - Never share verification codes.
  - Treat urgency as a red flag.
- This project intentionally contains no message templates for attackers.

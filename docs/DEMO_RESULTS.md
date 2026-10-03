# Safe Demonstration Profile - Results

Entirely fictional profile defined in `backend/services/demo_profile.py`.

## Assessment

**Overall Privacy Risk: 79/100 - CRITICAL**

### Category scores

| Category | Score | Level |
|---|---|---|
| Profile Visibility | 90/100 | CRITICAL |
| Personal Information | 67/100 | HIGH |
| Location Privacy | 86/100 | CRITICAL |
| Posts & Content | 80/100 | CRITICAL |
| Friends / Followers | 91/100 | CRITICAL |
| Tagging & Mentions | 91/100 | CRITICAL |
| Authentication & Account Security | 88/100 | CRITICAL |
| Third-Party Apps | 69/100 | HIGH |
| Messaging & Social Engineering | 43/100 | HIGH |
| Digital Footprint | 86/100 | CRITICAL |

### Top findings

1. Unknown connection requests accepted (+4.0 pts, HIGH)
2. Multi-factor authentication is disabled (+3.3 pts, CRITICAL)
3. Posts are publicly visible by default (+3.3 pts, HIGH)
4. Phone number reported as publicly visible (+3.0 pts, HIGH)
5. Profile is publicly visible (+3.0 pts, HIGH)
6. Anyone can send connection requests (+2.7 pts, MEDIUM)
7. Live check-ins while at a place (+2.4 pts, HIGH)
8. Posts carry location tags (+2.4 pts, HIGH)

### Top recommendations

| Priority | Recommendation |
|---|---|
| IMMEDIATE | Verify unfamiliar profiles (mutual contacts, account age, activity) before accepting, or decline. |
| IMMEDIATE | Enable multi-factor authentication using the strongest supported method available. |
| IMMEDIATE | Limit phone-number visibility to 'only me' wherever possible. |
| IMMEDIATE | Avoid publicly broadcasting real-time location unless intentionally needed; share live location only with specific trusted people. |
| IMMEDIATE | Set a unique, long password for this account and every other account. |
| IMMEDIATE | Crop or blur badges, documents, screens, boarding passes and plates; delete past posts that show them. |
| IMMEDIATE | Share family photos only with a small trusted audience; avoid faces, uniforms and school names. |
| IMMEDIATE | Be cautious with unexpected links; confirm with the sender through another channel. |

## Improvement simulation (changes listed in the brief)

| Setting | From | To |
|---|---|---|
| Phone number reported as publicly visible | YES | NO |
| Full birth date is publicly visible | YES | NO |
| Location shown on public profile | YES | NO |
| Travel plans posted before / during trips | OFTEN | NEVER |
| Real-time location sharing enabled | SOMETIMES | NEVER |
| Live check-ins while at a place | OFTEN | NEVER |
| Unknown connection requests accepted | OFTEN | NEVER |
| Tag review is disabled | NO | YES |
| Multi-factor authentication is disabled | NO | YES |
| MFA method is weak or unknown | NONE | APP_OR_KEY |
| Login alerts are disabled | NO | YES |
| Third-party apps not reviewed | NEVER | RECENT |

**Before:** 79/100 CRITICAL  
**After:** 50/100 HIGH  
**Risk reduction: 29 points**

_Framework simulation only: this estimates how the educational score would change if you applied these settings. It is not a guarantee of real-world safety._

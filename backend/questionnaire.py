"""
FILE: backend/questionnaire.py
PURPOSE: The privacy assessment questionnaire (53 questions, 10 categories).

Design rules (privacy by design):
  * Every question asks about a SETTING or a BEHAVIOUR ("Is your phone number
    publicly visible?"), never for the sensitive value itself.
  * Each answer option carries a risk value from 0.0 (lowest exposure) to 1.0
    (highest exposure). "NOT SURE" is scored as partial risk because an
    unknown setting is an unverified setting.
  * Each question has a weight (importance inside its category).
"""
from .config import CATEGORIES

# ---------------------------------------------------------------------------
# Answer scales: (code, label shown to user, risk value 0..1)
# ---------------------------------------------------------------------------
SCALES = {
    "visibility": [("PUBLIC", "Public (anyone)", 1.0), ("FRIENDS", "Friends / followers only", 0.35),
                   ("PRIVATE", "Only me / private", 0.0)],
    "exposed":    [("YES", "Yes, publicly visible", 1.0), ("NO", "No, hidden / private", 0.0),
                   ("NOT_SURE", "Not sure", 0.6)],
    "enabled":    [("YES", "Yes", 0.0), ("NO", "No", 1.0), ("NOT_SURE", "Not sure", 0.7)],
    "risky":      [("YES", "Yes", 1.0), ("NO", "No", 0.0), ("NOT_SURE", "Not sure", 0.5)],
    "risky_freq": [("OFTEN", "Often", 1.0), ("SOMETIMES", "Sometimes", 0.6), ("NEVER", "Never", 0.0),
                   ("NOT_SURE", "Not sure", 0.5)],
    "protective": [("YES", "Yes, consistently", 0.0), ("SOMETIMES", "Sometimes", 0.5), ("NO", "No", 1.0),
                   ("NOT_SURE", "Not sure", 0.7)],
    "review":     [("RECENT", "In the last 6 months", 0.0), ("OLD", "More than 6 months ago", 0.55),
                   ("NEVER", "Never", 1.0), ("NOT_SURE", "Not sure", 0.8)],
    "audience":   [("ANYONE", "Anyone", 1.0), ("FRIENDS", "Friends only", 0.35), ("NO_ONE", "No one / approval needed", 0.0)],
    "requests":   [("EVERYONE", "Everyone", 1.0), ("FRIENDS_OF_FRIENDS", "Friends of friends", 0.45),
                   ("APPROVAL", "Only after I approve", 0.0)],
    "mfa_method": [("APP_OR_KEY", "Authenticator app or security key", 0.0), ("SMS", "SMS text message", 0.5),
                   ("NONE", "I do not use MFA", 1.0), ("NOT_SURE", "Not sure", 0.7)],
}

# (id, key, category, text, scale, weight, finding_type, base_severity, control_label, help)
_RAW = [
 # ---- A: Profile Visibility -------------------------------------------------
 ("A1","profile_visibility","profile","Who can see your main profile (bio, posts, photos)?","visibility",3,"PUBLIC_PROFILE","HIGH",None,
  "A public profile lets anyone, including strangers, read what you share."),
 ("A2","search_engine_indexing","profile","Can search engines such as Google or Bing show your profile in their results?","exposed",2,"SEARCH_ENGINE_INDEXING","MEDIUM",None,
  "Search-engine visibility makes your profile discoverable without an account."),
 ("A3","friends_list_visibility","profile","Who can see your friends or followers list?","visibility",2,"FRIENDS_LIST_VISIBLE","MEDIUM",None,
  "Public connection lists reveal who you trust, which can be used to build convincing scams."),
 ("A4","contact_lookup_enabled","profile","Can people find your account by searching your phone number or email address?","exposed",2,"CONTACT_LOOKUP_ENABLED","MEDIUM",None,
  "Contact look-up makes your account easy to link to your real identity."),
 ("A5","username_reuse","profile","Do you use the same username on most of your social platforms?","risky",1,"USERNAME_REUSE","LOW",None,
  "A shared handle lets someone correlate your accounts across platforms."),
 # ---- B: Personal Information ----------------------------------------------
 ("B1","phone_public","personal_info","Is your phone number visible to the public?","exposed",3,"PHONE_PUBLIC","HIGH",None,
  "You only answer whether it is visible. Never type your number into this tool."),
 ("B2","email_public","personal_info","Is your personal email address visible to the public?","exposed",2,"EMAIL_PUBLIC","MEDIUM",None,
  "Public email addresses are used for spam, phishing and account-recovery attacks."),
 ("B3","birthday_public","personal_info","Is your full birth date (day, month AND year) visible to the public?","exposed",2,"BIRTHDAY_PUBLIC","MEDIUM",None,
  "A full birth date is a common identity-verification detail."),
 ("B4","home_info_public","personal_info","Are your home address, street or neighbourhood details publicly visible?","exposed",3,"HOME_INFO_PUBLIC","HIGH",None,
  "Home-related details link your online identity to a physical place."),
 ("B5","workplace_public","personal_info","Is your employer or workplace publicly visible?","exposed",2,"WORKPLACE_PUBLIC","MEDIUM",None,
  "Employer details make impersonation and targeted phishing more believable."),
 ("B6","education_public","personal_info","Is your school or college publicly visible?","exposed",1.5,"EDUCATION_PUBLIC","LOW",None,
  "Education details add context that can be reused in scams."),
 ("B7","relationship_public","personal_info","Are your relationship status or family members publicly visible?","exposed",1.5,"FAMILY_INFO_PUBLIC","MEDIUM",None,
  "Family details are often used in 'family emergency' scams and security-question guessing."),
 # ---- C: Location Privacy ---------------------------------------------------
 ("C1","location_public","location","Is your current city or location visible on your public profile?","exposed",2,"PROFILE_LOCATION_PUBLIC","MEDIUM",None,
  "A city on your profile is usually low risk alone, but it narrows searches about you."),
 ("C2","realtime_location","location","Do you publicly share your real-time location (live location, 'nearby' features)?","risky_freq",3,"REALTIME_LOCATION","CRITICAL",None,
  "Real-time sharing tells the world where you are right now."),
 ("C3","location_tagging","location","Do your public posts or photos carry location tags?","risky_freq",2,"LOCATION_TAGGING","HIGH",None,
  "Geotags build a map of the places you visit."),
 ("C4","live_checkins","location","Do you check in to places (home, work, school, gym) while you are still there?","risky_freq",2,"LIVE_CHECKINS","HIGH",None,
  "Live check-ins reveal your presence and your absence from home."),
 ("C5","travel_posts","location","Do you post travel plans before or during a trip?","risky_freq",2,"TRAVEL_POSTS","HIGH",None,
  "Sharing travel after you return is safer than broadcasting it in advance."),
 ("C6","routine_patterns","location","Do your posts reveal routines (same café, commute, gym time)?","risky_freq",1.5,"ROUTINE_PATTERNS","MEDIUM",None,
  "Repeated patterns make your movements predictable."),
 # ---- D: Posts & Content ----------------------------------------------------
 ("D1","posts_public","content","Who can see your posts by default?","visibility",3,"PUBLIC_POSTS","HIGH",None,
  "Your default audience decides how much of what you post is public."),
 ("D2","sensitive_photo_content","content","Have you posted photos showing badges, documents, boarding passes, screens or vehicle plates?","risky_freq",2.5,"SENSITIVE_PHOTO_CONTENT","HIGH",None,
  "Photo backgrounds can leak details you never typed."),
 ("D3","family_photos_public","content","Do you publicly post photos of children or family members' faces or school uniforms?","risky_freq",2,"FAMILY_PHOTOS_PUBLIC","HIGH",None,
  "Photos of minors deserve extra care; others have not consented to being public."),
 ("D4","public_stories","content","Can people outside your connections see your stories, reels or highlights?","exposed",1.5,"PUBLIC_STORIES","MEDIUM",None,
  "Short-lived content is still visible, screenshot-able and often location-rich."),
 # ---- E: Friends / Followers ------------------------------------------------
 ("E1","request_audience","connections","Who can send you friend or follow requests?","requests",2,"OPEN_REQUESTS","MEDIUM",None,
  "Open requests make it easy for strangers or fake accounts to reach you."),
 ("E2","unknown_connections","connections","Do you accept connection requests from people you do not know?","risky_freq",3,"UNKNOWN_CONNECTIONS","HIGH",None,
  "Accepted strangers can view friends-only content and message you as a 'contact'."),
 ("E3","connections_reviewed","connections","When did you last review and remove unfamiliar friends or followers?","review",1.5,"CONNECTIONS_NOT_REVIEWED","LOW",None,
  "Old connections accumulate. Regular pruning keeps your audience what you think it is."),
 ("E4","close_friends_used","connections","Do you use a close-friends or restricted list for personal posts?","protective",1,"NO_AUDIENCE_SEGMENTATION","LOW",None,
  "Audience lists let you share personal content with fewer people."),
 # ---- F: Tagging & Mentions -------------------------------------------------
 ("F1","tag_review_enabled","tagging","Is tag review (approve tags before they appear on your profile) turned on?","enabled",2.5,"TAG_REVIEW_DISABLED","MEDIUM","Tag review",
  "Other people's posts can expose you even when you post very little."),
 ("F2","who_can_tag","tagging","Who is allowed to tag you in posts and photos?","audience",2,"ANYONE_CAN_TAG","MEDIUM",None,
  "Open tagging lets anyone attach your identity to their content."),
 ("F3","tagged_posts_auto_visible","tagging","Do posts you are tagged in appear on your profile automatically?","risky",1.5,"AUTO_TAGGED_POSTS","MEDIUM",None,
  "Automatic display lets others write onto your public profile."),
 ("F4","who_can_mention","tagging","Who is allowed to mention you or message you through mentions?","audience",1,"OPEN_MENTIONS","LOW",None,
  "Open mentions are a channel for harassment and scam outreach."),
 # ---- G: Authentication & Account Security ---------------------------------
 ("G1","mfa_enabled","account_security","Is multi-factor authentication (MFA) turned on for your main social account?","enabled",4,"MFA_DISABLED","CRITICAL","MFA enabled",
  "MFA stops most account takeovers that start with a stolen password."),
 ("G2","mfa_method","account_security","Which MFA method do you use?","mfa_method",2,"WEAK_MFA_METHOD","MEDIUM",None,
  "Authenticator apps and security keys resist SIM-swap and interception better than SMS."),
 ("G3","password_reuse_reported","account_security","Do you reuse this account's password on other websites or apps?","risky_freq",3.5,"PASSWORD_REUSE","HIGH","Unique password",
  "One breach elsewhere can unlock every account that shares the password."),
 ("G4","password_manager_used","account_security","Do you use a password manager to create and store unique passwords?","enabled",1.5,"NO_PASSWORD_MANAGER","MEDIUM","Password manager",
  "Password managers make unique, strong passwords practical."),
 ("G5","login_alerts_enabled","account_security","Are login alerts for new devices or locations turned on?","enabled",2,"LOGIN_ALERTS_DISABLED","MEDIUM","Login alerts",
  "Alerts give you early warning when someone else signs in."),
 ("G6","sessions_reviewed","account_security","When did you last review your active sessions and logged-in devices?","review",1.5,"SESSIONS_NOT_REVIEWED","MEDIUM","Sessions reviewed",
  "Old sessions on lost or shared devices can stay signed in for months."),
 ("G7","recovery_reviewed","account_security","Have you checked that your recovery email and phone number are current and secure?","enabled",2,"RECOVERY_NOT_REVIEWED","MEDIUM","Recovery info checked",
  "Attackers often target recovery channels instead of the password."),
 ("G8","unknown_devices_checked","account_security","Do you check for unknown devices or unfamiliar login locations?","protective",1.5,"DEVICES_NOT_CHECKED","LOW",None,
  "Spotting an unknown device early limits the damage of a takeover."),
 # ---- H: Third-Party Apps ---------------------------------------------------
 ("H1","third_party_apps_reviewed","third_party","When did you last review apps and websites connected to your social account?","review",3,"APPS_NOT_REVIEWED","MEDIUM","Connected apps reviewed",
  "Connected apps can keep access long after you stop using them."),
 ("H2","unused_apps_removed","third_party","Have you removed connected apps and games you no longer use?","protective",2,"UNUSED_APPS_REMAIN","MEDIUM",None,
  "Unused integrations are unnecessary access: remove what you do not need."),
 ("H3","permissions_checked","third_party","Do you check which permissions an app asks for before you connect it?","protective",2,"PERMISSIONS_UNCHECKED","MEDIUM",None,
  "Principle of least privilege: grant only the access an app really needs."),
 ("H4","social_login_overuse","third_party","Do you use 'Sign in with social account' on many unrelated websites?","risky_freq",1.5,"SOCIAL_LOGIN_OVERUSE","LOW",None,
  "Every social-login connection is another place that holds a link to your profile."),
 # ---- I: Messaging & Social Engineering -------------------------------------
 ("I1","responds_to_suspicious_dms","social_engineering","Do you reply to unexpected messages offering jobs, prizes or urgent help from unfamiliar accounts?","risky_freq",2.5,"RESPONDS_TO_SUSPICIOUS_DMS","HIGH",None,
  "Replying confirms your account is active and starts the scammer's conversation."),
 ("I2","suspicious_link_awareness","social_engineering","Do you feel confident spotting suspicious links and scam messages?","protective",2,"LOW_LINK_AWARENESS","MEDIUM",None,
  "Awareness is the main defence against phishing and scam links."),
 ("I3","clicks_unexpected_links","social_engineering","Do you click unexpected links without checking them first, even from friends?","risky_freq",3,"CLICKS_UNEXPECTED_LINKS","HIGH",None,
  "Hijacked friend accounts are a common way phishing links spread."),
 ("I4","shares_verification_codes","social_engineering","Have you ever shared a one-time verification code with someone who asked for it in a message?","risky",3.5,"SHARES_VERIFICATION_CODES","CRITICAL",None,
  "A verification code is a password. Nobody legitimate will ask you to send it."),
 ("I5","impersonation_check","social_engineering","If a friend's account suddenly asks for money or help, do you verify through another channel first?","protective",2,"NO_IMPERSONATION_CHECK","HIGH",None,
  "Impersonation scams rely on trust in a familiar name."),
 ("I6","giveaway_participation","social_engineering","Do you join giveaways or 'free offer' posts that ask you to log in, share or fill in forms?","risky_freq",1.5,"SUSPICIOUS_GIVEAWAYS","MEDIUM",None,
  "Fake giveaways are a classic data-harvesting and phishing tactic."),
 # ---- J: Digital Footprint --------------------------------------------------
 ("J1","old_posts_reviewed","footprint","When did you last review your old public posts, photos and comments?","review",2.5,"OLD_POSTS_NOT_REVIEWED","MEDIUM","Old posts reviewed",
  "Old posts stay searchable. Content that was fine years ago may not be today."),
 ("J2","privacy_settings_reviewed","footprint","When did you last review your privacy settings?","review",2.5,"SETTINGS_NOT_REVIEWED","MEDIUM","Settings reviewed",
  "Platforms change defaults and add features, so settings drift over time."),
 ("J3","unused_accounts","footprint","Do you have old or unused social accounts that are still active?","risky",2,"UNUSED_ACCOUNTS","MEDIUM",None,
  "Forgotten accounts are rarely protected and can be taken over unnoticed."),
 ("J4","photo_metadata_awareness","footprint","Do you remove or disable photo metadata (EXIF location / device info) before posting?","protective",1.5,"PHOTO_METADATA_UNMANAGED","MEDIUM",None,
  "Photos can carry hidden metadata such as device model, time and sometimes GPS."),
 ("J5","public_comments","footprint","Do you leave public comments that reveal personal details (school, workplace, plans)?","risky_freq",1.5,"PUBLIC_COMMENTS_OVERSHARING","MEDIUM",None,
  "Public comments are part of your active digital footprint."),
]


def _build():
    questions = []
    for qid, key, cat, text, scale, weight, ftype, sev, control, help_text in _RAW:
        options = [{"value": v, "label": l, "risk": r} for v, l, r in SCALES[scale]]
        best = min(options, key=lambda o: o["risk"])
        questions.append({
            "id": qid, "key": key, "category": cat, "text": text, "scale": scale,
            "weight": float(weight), "finding_type": ftype, "severity": sev,
            "control": control, "help": help_text, "options": options,
            "risk_map": {o["value"]: o["risk"] for o in options},
            "best_answer": best["value"],
            "worst_answer": max(options, key=lambda o: o["risk"])["value"],
        })
    return questions


QUESTIONS = _build()
QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}
QUESTION_BY_KEY = {q["key"]: q for q in QUESTIONS}
QUESTION_BY_FINDING = {q["finding_type"]: q for q in QUESTIONS}
CONTROL_QUESTIONS = [q for q in QUESTIONS if q["control"]]
assert len(QUESTIONS) >= 40, "Brief requires at least 40 questions"


def resolve_question(id_or_key: str):
    """Accept either 'G1' or 'mfa_enabled'."""
    return QUESTION_BY_ID.get(id_or_key) or QUESTION_BY_KEY.get(id_or_key)


def public_questionnaire() -> dict:
    """What the API sends to the browser (risk values are not needed there)."""
    cats = []
    for c in CATEGORIES:
        qs = [{
            "id": q["id"], "key": q["key"], "text": q["text"], "help": q["help"],
            "options": [{"value": o["value"], "label": o["label"]} for o in q["options"]],
        } for q in QUESTIONS if q["category"] == c["key"]]
        cats.append({**c, "questions": qs})
    return {"total_questions": len(QUESTIONS), "categories": cats}

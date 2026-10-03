"""
FILE: backend/services/demo_profile.py
PURPOSE: The fictional "safe demonstration profile" from the project brief.
Entirely synthetic - it does not describe any real person.
"""
from ..questionnaire import QUESTIONS

# Explicit values from the brief; keys are question keys.
_DEMO = {
 "profile_visibility": "PUBLIC", "search_engine_indexing": "YES", "friends_list_visibility": "PUBLIC",
 "contact_lookup_enabled": "YES", "username_reuse": "NO",
 "phone_public": "YES", "email_public": "NO", "birthday_public": "YES", "home_info_public": "NO",
 "workplace_public": "YES", "education_public": "YES", "relationship_public": "YES",
 "location_public": "YES", "realtime_location": "SOMETIMES", "location_tagging": "OFTEN",
 "live_checkins": "OFTEN", "travel_posts": "OFTEN", "routine_patterns": "SOMETIMES",
 "posts_public": "PUBLIC", "sensitive_photo_content": "SOMETIMES", "family_photos_public": "SOMETIMES",
 "public_stories": "YES",
 "request_audience": "EVERYONE", "unknown_connections": "OFTEN", "connections_reviewed": "OLD",
 "close_friends_used": "NO",
 "tag_review_enabled": "NO", "who_can_tag": "ANYONE", "tagged_posts_auto_visible": "YES", "who_can_mention": "FRIENDS",
 "mfa_enabled": "NO", "mfa_method": "NONE", "password_reuse_reported": "SOMETIMES",
 "password_manager_used": "NO", "login_alerts_enabled": "NO", "sessions_reviewed": "NEVER",
 "recovery_reviewed": "NO", "unknown_devices_checked": "SOMETIMES",
 "third_party_apps_reviewed": "NEVER", "unused_apps_removed": "NO", "permissions_checked": "YES",
 "social_login_overuse": "SOMETIMES",
 "responds_to_suspicious_dms": "SOMETIMES", "suspicious_link_awareness": "SOMETIMES",
 "clicks_unexpected_links": "SOMETIMES", "shares_verification_codes": "NO", "impersonation_check": "SOMETIMES",
 "giveaway_participation": "SOMETIMES",
 "old_posts_reviewed": "NEVER", "privacy_settings_reviewed": "NEVER", "unused_accounts": "YES",
 "photo_metadata_awareness": "SOMETIMES", "public_comments": "SOMETIMES",
}

# The "after" settings listed in the brief's simulation step.
DEMO_IMPROVEMENTS = {
 "phone_public": "NO", "birthday_public": "NO", "location_public": "NO", "travel_posts": "NEVER",
 "realtime_location": "NEVER", "live_checkins": "NEVER", "unknown_connections": "NEVER",
 "tag_review_enabled": "YES", "mfa_enabled": "YES", "mfa_method": "APP_OR_KEY",
 "login_alerts_enabled": "YES", "third_party_apps_reviewed": "RECENT",
}


def demo_answers() -> dict:
    """{question_id: answer} for the fictional demo profile."""
    return {q["id"]: _DEMO[q["key"]] for q in QUESTIONS}

# Security & Privacy Testing

Run: `python -m pytest -v` (54 tests). The privacy/security tests are in `tests/test_privacy_security.py`.

| Check | Test | What it proves |
|---|---|---|
| No sensitive columns | `test_database_stores_no_answers_or_pii`, T29 | Schema has no phone/email/address/birth/password/message fields and raw answers are never persisted |
| No IPs stored | `test_no_ip_address_persisted` | Rate limiter keeps IPs in memory only |
| Input validation | `test_rejects_*` | Unknown ids, invalid options, missing answers, wrong types and extra PII-like fields → HTTP 400 |
| XSS | `test_xss_payload_not_reflected`, `test_report_is_escaped_and_locked_down`, T30 | Payloads are rejected, never echoed; report escapes every value and ships `default-src 'none'` CSP; frontend uses escaping + `script-src 'self'` |
| SQL injection | `test_bad_id_formats_and_sqli_attempts` | Id regex + parameterised queries |
| Rate limiting | `test_rate_limiting` | 4th write inside a minute → HTTP 429 |
| Oversize payloads | `test_oversized_body_rejected` | Body limited to 64 KB |
| Authentication / authorisation | design + tests | No accounts; unguessable capability id; 404 for unknown ids |
| Secure sessions | design | No server-side sessions/cookies; sessionStorage holds answers only in the user's tab |
| Environment variables | `test_secrets_not_committed` | `.env` git-ignored, `.env.example` provided |
| Safe report generation | T30 | Escaped HTML, no personal identifiers |
| Data deletion | `test_data_deletion`, `test_deletion_cascades_to_child_tables`, `test_retention_purge` | DELETE removes all rows; retention purge exists |
| Safe metadata tool | `test_metadata_strip_removes_exif` | Cleaned copy has 0 metadata fields; non-images rejected |
| Security headers | `test_security_headers` | CSP, nosniff, frame-deny, no-store |

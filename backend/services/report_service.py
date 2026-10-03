"""
FILE: backend/services/report_service.py
PURPOSE: Standalone HTML privacy report (open in a browser -> Print -> Save as PDF).
Contains NO sensitive personal data. Every dynamic value is HTML-escaped.
"""
from html import escape

from ..config import DISCLAIMER
from ..knowledge_base import CHECKLIST

COLORS = {"LOW": "#16a34a", "MODERATE": "#ca8a04", "HIGH": "#ea580c", "CRITICAL": "#dc2626"}
PRIO_COLORS = {"IMMEDIATE": "#dc2626", "IMPORTANT": "#ea580c", "GOOD PRACTICE": "#2563eb"}


def generate_report_html(a: dict) -> str:
    """`a` = build_view() output plus assessment_id and created_at."""
    e = escape
    col = COLORS.get(a["risk_level"], "#444")
    cat_rows = "".join(
        f"<tr><td>{e(c['label'])}</td><td style='width:45%'><div class='bar'><i style='width:{int(c['score'])}%;"
        f"background:{COLORS[c['level']]}'></i></div></td><td><b>{int(c['score'])}</b>/100</td>"
        f"<td style='color:{COLORS[c['level']]}'>{e(c['level'])}</td></tr>" for c in a["category_scores"])
    finds = "".join(
        f"<tr><td>{i}</td><td>{e(f['title'])}</td><td>{e(f['severity'])}</td><td>+{float(f['impact_points']):.1f}</td></tr>"
        for i, f in enumerate(a["findings"][:10], 1)) or "<tr><td colspan=4>No significant findings.</td></tr>"
    recs = "".join(
        f"<tr><td><span class='pill' style='background:{PRIO_COLORS.get(r['priority'], '#444')}'>{e(r['priority'])}</span></td>"
        f"<td>{e(r['risk'])}</td><td>{e(r['recommendation'])}</td></tr>" for r in a["recommendations"][:15])
    actions = "".join(f"<li>{e(r['recommendation'])}</li>" for r in a["recommendations"] if r["priority"] == "IMMEDIATE") \
        or "<li>No immediate actions. Keep reviewing your settings periodically.</li>"
    checklist = "".join(f"<li>&#9633; {e(t)}</li>" for t, _ in CHECKLIST)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Privacy Assessment Report {e(a['assessment_id'])}</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;color:#0f172a;max-width:880px;margin:24px auto;padding:0 20px;line-height:1.45}}
h1{{margin:0}} h2{{border-bottom:2px solid #e2e8f0;padding-bottom:4px;margin-top:28px;font-size:1.15rem}}
.hero{{display:flex;gap:24px;align-items:center;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:18px;margin-top:14px}}
.score{{font-size:3.2rem;font-weight:800;color:{col};line-height:1}} .lvl{{font-weight:700;color:{col};font-size:1.2rem}}
table{{width:100%;border-collapse:collapse;font-size:.92rem}} td,th{{padding:6px 8px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top}}
.bar{{background:#e2e8f0;border-radius:6px;height:10px}} .bar i{{display:block;height:10px;border-radius:6px}}
.pill{{color:#fff;font-size:.7rem;padding:2px 8px;border-radius:99px;white-space:nowrap}}
ul.cl{{columns:2;list-style:none;padding:0}} .note{{font-size:.82rem;color:#475569;border:1px solid #cbd5e1;border-radius:8px;padding:10px;margin-top:24px}}
@media print{{body{{margin:0}}}}
</style></head><body>
<h1>Social Media Privacy Risk Assessment Report</h1>
<div style="color:#475569">Assessment ID: <b>{e(a['assessment_id'])}</b> &nbsp;|&nbsp; Date: <b>{e(a['created_at'][:10])}</b></div>
<div class="hero"><div><div class="score">{int(a['overall_score'])}<small style="font-size:1rem;color:#64748b">/100</small></div>
<div class="lvl">{e(a['risk_level'])} RISK</div></div>
<div style="font-size:.9rem">Higher score = higher assessed exposure.<br>High-risk categories: <b>{len(a['high_risk_categories'])}</b> of 10<br>
Controls enabled: <b>{int(a['controls_enabled'])}/{int(a['controls_total'])}</b></div></div>
<h2>Category scores</h2><table>{cat_rows}</table>
<h2>Top findings</h2><table><tr><th>#</th><th>Finding</th><th>Severity</th><th>Points</th></tr>{finds}</table>
<h2>Security recommendations</h2><table><tr><th>Priority</th><th>Risk</th><th>Recommendation</th></tr>{recs}</table>
<h2>Priority actions</h2><ol>{actions}</ol>
<h2>Privacy checklist</h2><ul class="cl">{checklist}</ul>
<div class="note"><b>Disclaimer.</b> {e(DISCLAIMER)} This report contains no personal identifiers.</div>
</body></html>"""

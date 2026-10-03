"""Run:  python scripts/generate_docs.py   - writes QUESTIONNAIRE.md, DEMO_RESULTS.md and RISK_MATRIX.md from the live code."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend.config import CATEGORIES, DEFAULT_CATEGORY_WEIGHTS  # noqa: E402
from backend.knowledge_base import KB  # noqa: E402
from backend.questionnaire import QUESTIONS  # noqa: E402
from backend.services.assessment_engine import run_assessment  # noqa: E402
from backend.services.demo_profile import DEMO_IMPROVEMENTS, demo_answers  # noqa: E402
from backend.services.improvement_simulator import simulate_improvement  # noqa: E402

D = ROOT / "docs"

# ---- QUESTIONNAIRE.md ----
L = [f"# Privacy Assessment Questionnaire ({len(QUESTIONS)} questions)\n",
     "Every question asks about a **setting or behaviour**, never for the sensitive value itself. "
     "Risk values: 0.0 = lowest exposure, 1.0 = highest.\n"]
for c in CATEGORIES:
    L.append(f"\n## Category {c['letter']}: {c['label']}  (weight {DEFAULT_CATEGORY_WEIGHTS[c['key']]}%)\n")
    L.append("| ID | Question | Answers (risk) | Weight |\n|---|---|---|---|")
    for q in [q for q in QUESTIONS if q["category"] == c["key"]]:
        opts = "; ".join(f"{o['label']} ({o['risk']})" for o in q["options"])
        L.append(f"| {q['id']} | {q['text']} | {opts} | {q['weight']:g} |")
(D / "QUESTIONNAIRE.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---- DEMO_RESULTS.md ----
a = demo_answers(); r = run_assessment(a); s = simulate_improvement(a, changes=DEMO_IMPROVEMENTS)
M = ["# Safe Demonstration Profile - Results\n", "Entirely fictional profile defined in `backend/services/demo_profile.py`.\n",
     f"## Assessment\n\n**Overall Privacy Risk: {r['overall_score']}/100 - {r['risk_level']}**\n",
     "### Category scores\n\n| Category | Score | Level |\n|---|---|---|"]
M += [f"| {c['label']} | {c['score']}/100 | {c['level']} |" for c in r["category_scores"]]
M += ["\n### Top findings\n"] + [f"{i}. {f['title']} (+{f['impact_points']:.1f} pts, {f['severity']})" for i, f in enumerate(r["findings"][:8], 1)]
M += ["\n### Top recommendations\n", "| Priority | Recommendation |\n|---|---|"] + [f"| {x['priority']} | {x['recommendation']} |" for x in r["recommendations"][:8]]
M += ["\n## Improvement simulation (changes listed in the brief)\n", "| Setting | From | To |\n|---|---|---|"]
M += [f"| {x['title']} | {x['from']} | {x['to']} |" for x in s["applied_changes"]]
M += [f"\n**Before:** {s['before']['score']}/100 {s['before']['level']}  \n**After:** {s['after']['score']}/100 {s['after']['level']}  \n**Risk reduction: {s['risk_reduction']} points**\n",
      f"_{s['disclaimer']}_"]
(D / "DEMO_RESULTS.md").write_text("\n".join(M) + "\n", encoding="utf-8")

# ---- RISK_MATRIX.md ----
X = ["# Privacy Risk Matrix\n", "Likelihood and impact are **educational estimates**; real risk depends on context (who you are, who might target you, what else is public).\n",
     "| Finding | Likelihood | Impact | Priority |\n|---|---|---|---|"]
X += [f"| {t[0]} | {t[4].title()} | {t[5].title()} | {t[3]} |" for t in KB.values()]
(D / "RISK_MATRIX.md").write_text("\n".join(X) + "\n", encoding="utf-8")
print("docs written:", r["overall_score"], r["risk_level"], "->", s["after"]["score"], s["after"]["level"])

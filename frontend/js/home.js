/* FILE: frontend/js/home.js */
renderNav('home');
$('#flow').innerHTML = [['1', 'Answer', 'Privacy questionnaire: settings & behaviours only.'], ['2', 'Validate & extract', 'Strict allow-list validation, answers → numeric risk features.'],
  ['3', 'Score', 'Category scores → configurable weighted overall score (0–100).'], ['4', 'Explain', 'Ranked findings with exact point impact + prioritised fixes.'],
  ['5', 'Simulate', '"What if I enable MFA and hide my phone?" — instantly.'], ['6', 'Report', 'Dashboard, checklist and printable/PDF report.']]
  .map(s => `<div class="card cat-card"><div class="ltr">${s[0]}</div><h3>${s[1]}</h3><div class="muted small">${s[2]}</div></div>`).join('');
Promise.all([api('/questionnaire'), api('/dashboard/stats'), api('/demo')]).then(([Q, S, D]) => {
  $('#cats').innerHTML = Q.categories.map(c => `<div class="card cat-card"><div style="display:flex;gap:10px;align-items:center"><div class="ltr">${c.letter}</div><h3 style="margin:0">${esc(c.label)}</h3></div>
    <div class="muted small">${esc(c.blurb)}</div><div class="small" style="margin-top:auto;color:var(--accent)">${c.questions.length} questions</div></div>`).join('');
  $('#stats').innerHTML = [[Q.total_questions, 'questions'], [10, 'categories'], [S.cohort_size.toLocaleString(), 'synthetic profiles'], ['0', 'personal data collected']]
    .map(x => `<div class="card" style="padding:12px;text-align:center"><div style="font-size:1.5rem;font-weight:800">${x[0]}</div><div class="small muted">${x[1]}</div></div>`).join('');
  $('#heroGauge').innerHTML = Charts.gauge(D.overall_score, D.risk_level);
  $('#heroBars').innerHTML = Charts.bars(D.category_scores.slice().sort((a, b) => b.score - a.score).slice(0, 5).map(c => ({label: c.label, value: c.score, color: LEVEL_COLOR[c.level], right: c.score})));
}).catch(() => {});

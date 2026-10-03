/* FILE: frontend/js/results.js - score, categories, findings, recommendations, simulator */
renderNav('assessment');
const qs = new URLSearchParams(location.search);
const card = (cls, title, tag, body) => `<section class="card ${cls}"><h3><span>${title}</span>${tag ? `<span class="tag">${tag}</span>` : ''}</h3><div class="grow">${body}</div></section>`;
let A, ANSWERS = null, picked = new Set();

async function init() {
  try {
    if (qs.get('demo')) { A = await api('/demo'); ANSWERS = A.answers; }
    else { const id = qs.get('id') || Session.id; if (!id) { location.href = '/assessment'; return; }
      A = await api('/assessment/' + encodeURIComponent(id)); if (Session.id === id) ANSWERS = Session.answers; }
    draw();
  } catch (e) { $('#err').hidden = false; $('#err').innerHTML = 'Could not load results (' + esc(e.message) + '). The assessment may have expired or been deleted. <a href="/assessment">Start a new one</a>.'; $('#meta').textContent = ''; }
}

function draw() {
  const lv = A.risk_level, col = LEVEL_COLOR[lv], cats = A.category_scores;
  $('#meta').innerHTML = A.demo ? 'Fictional demo profile (not stored)' : `Assessment <b>${esc(A.assessment_id)}</b> · ${esc(A.created_at.slice(0, 10))} · riskier than ${A.percentile}% of the synthetic cohort`;
  const id = encodeURIComponent(A.assessment_id), real = !A.demo;
  $('#actions').innerHTML = (real ? `<a class="btn sm" target="_blank" href="/api/assessment/${id}/report">📄 View report</a><a class="btn sm" href="/api/assessment/${id}/report?download=1">⬇ Download HTML</a><button class="btn sm" id="printBtn">🖨 Print / PDF</button>` : '')
    + `<a class="btn sm" href="/dashboard${real ? '' : '?demo=1'}">📊 Dashboard</a><a class="btn sm" href="/checklist">✅ Checklist</a>` + (real ? `<button class="btn sm danger" id="delBtn">🗑 Delete my assessment</button>` : '<a class="btn sm primary" href="/assessment">Start your own</a>');

  const gauge = Charts.gauge(A.overall_score, lv) + `<div style="text-align:center">${pillLevel(lv)}<div class="small muted" style="margin-top:6px">Higher score = higher assessed exposure</div></div>
    <div class="rows" style="flex:none"><div class="row"><div class="top"><span>High-risk categories</span><b>${A.high_risk_categories.length} / 10</b></div></div>
    <div class="row"><div class="top"><span>Security controls enabled</span><b>${A.controls_enabled} / ${A.controls_total}</b></div></div>
    <div class="row"><div class="top"><span>Findings</span><b>${A.findings.length}</b></div></div></div>
    <div class="small muted">Educational framework, not a guarantee that an account will or will not be compromised.</div>`;
  const top = cats.slice().sort((a, b) => b.score - a.score), box = (l, c, v, k) => `<div style="background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px 10px"><div class="small muted">${l}</div><div style="font-weight:700;font-size:.84rem">${esc(c)}</div><div style="color:${LEVEL_COLOR[levelOf(v)]};font-weight:800">${v}/100</div></div>`;
  const radar = `<div>` + Charts.radar(cats.map(c => c.short.replace('Social Engineering', 'Social Eng.').replace('Third-Party Apps', '3rd-Party Apps')), [{color: col, values: cats.map(c => c.score), dots: true, fill: .28}]) + `</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">${box('Highest-risk category', top[0].short, top[0].score)}${box('Lowest-risk category', top[9].short, top[9].score)}</div>`;
  const bars = Charts.bars(cats.slice().sort((a, b) => b.score - a.score).map(c => ({label: c.label, value: c.score, color: LEVEL_COLOR[c.level], right: c.score + '/100'})));

  const finds = A.findings.slice(0, 15).map((f, i) => `<div class="item"><div class="n">${i + 1}</div><div><div class="t">${esc(f.title)}</div><div class="d">${esc(f.description)}</div></div>
    <div style="margin-left:auto;text-align:right"><span class="pill lvl ${esc(f.severity === 'MEDIUM' ? 'MODERATE' : f.severity)}">${esc(f.severity)}</span><div class="pts" style="--c:${col}">+${f.impact_points.toFixed(1)} pts</div></div></div>`).join('') || '<div class="muted">No significant findings. 🎉</div>';
  const recGroup = ['IMMEDIATE', 'IMPORTANT', 'GOOD PRACTICE'].map(p => { const r = A.recommendations.filter(x => x.priority === p); if (!r.length) return '';
    return `<div style="margin:6px 0 2px">${pillPrio(p)} <span class="small muted">${r.length} item(s)</span></div>` + r.slice(0, p === 'GOOD PRACTICE' ? 3 : 5).map(x => `<div class="item" style="padding:8px 0"><div><div class="t" style="font-size:.86rem">${esc(x.risk)}</div><div class="d">${esc(x.recommendation)}</div></div></div>`).join('') +
      (r.length > (p === 'GOOD PRACTICE' ? 3 : 5) ? `<div class="small muted">+ ${r.length - (p === 'GOOD PRACTICE' ? 3 : 5)} more in the full report</div>` : ''); }).join('');
  const tips = ['Strong account security ≠ strong privacy.', 'Post about a place after you leave, not while you are there.', 'Never share a verification code with anyone.'];

  $('#content').innerHTML = `<div class="grid12">
    ${card('s4', 'Overall Privacy Risk', '0–100', gauge)}${card('s4', 'Category Risk Radar', 'higher = riskier', radar)}${card('s4', 'Category Scores', '10 categories', bars)}
    ${card('s6', 'Top Detected Weaknesses', 'ranked by points', `<div>${finds}</div>`)}${card('s6', 'Personalised Recommendations', 'by priority', `<div>${recGroup}</div>`)}
    <section class="card s12" id="simCard"></section>
    ${card('s12', 'Security-Awareness Guidance', '', `<div class="cards3">${tips.map(t => `<div class="banner" style="color:#a5f3fc;border-color:#164e63;background:#083344aa">💡 ${t}</div>`).join('')}</div><div class="small muted">Open the <a href="/checklist">printable privacy checklist</a> or inspect a photo's hidden metadata with the <a href="/tools">local Metadata Tool</a>.</div>`)}
  </div>`;
  if ($('#printBtn')) $('#printBtn').onclick = () => window.open(`/api/assessment/${id}/report`, '_blank');
  if ($('#delBtn')) $('#delBtn').onclick = async () => { if (!confirm('Permanently delete this assessment from the server?')) return;
    await api('/assessment/' + id, {method: 'DELETE'}); Session.clear(); alert('Deleted.'); location.href = '/'; };
  drawSim();
}

function drawSim() {
  const el = $('#simCard');
  el.innerHTML = `<h3><span>🧪 Privacy Improvement Simulator — “What happens if I improve my settings?”</span><span class="tag">framework simulation</span></h3>`;
  if (!ANSWERS) { el.innerHTML += `<div class="muted">The simulator re-scores your answers, which are deliberately <b>not stored</b> on the server. Retake the assessment in this browser tab to use it. <a href="/assessment">Start assessment</a></div>`; return; }
  const items = A.findings.slice(0, 16);
  if (!picked.size) items.filter(f => A.recommendations.find(r => r.finding_type === f.finding_type && r.priority === 'IMMEDIATE')).forEach(f => picked.add(f.finding_type));
  el.innerHTML += `<div class="grid12" style="gap:20px"><div class="s5" style="display:flex;flex-direction:column;gap:8px">
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" id="sImm">Select IMMEDIATE</button><button class="btn sm" id="sAll">Select all</button><button class="btn sm ghost" id="sNone">Clear</button></div>
      <div style="display:flex;flex-direction:column;gap:6px;max-height:420px;overflow:auto">${items.map(f => `<label class="sim-opt"><input type="checkbox" data-f="${esc(f.finding_type)}" ${picked.has(f.finding_type) ? 'checked' : ''}><span>${esc(f.title)}</span><span class="pts">−${f.impact_points.toFixed(1)}</span></label>`).join('')}</div></div>
    <div class="s7" id="simOut" style="display:flex;flex-direction:column;gap:12px"></div></div>`;
  const run = async () => {
    picked = new Set($$('#simCard input:checked').map(i => i.dataset.f));
    const S = await api('/assessment/simulate-improvement', {json: {answers: ANSWERS, fix_findings: [...picked]}});
    $('#simOut').innerHTML = `<div class="ba"><div><div class="small muted">CURRENT</div><div class="num" style="color:${LEVEL_COLOR[S.before.level]}">${S.before.score}<small class="muted" style="font-size:1rem">/100</small></div>${pillLevel(S.before.level)}</div><div><div class="arrow">➜</div>
      <div class="pill lvl LOW" style="--c:var(--low);font-size:.85rem">−${S.risk_reduction} pts</div></div><div><div class="small muted">SIMULATED</div><div class="num" style="color:${LEVEL_COLOR[S.after.level]}">${S.after.score}<small class="muted" style="font-size:1rem">/100</small></div>${pillLevel(S.after.level)}</div></div>
      ${Charts.compare(S.category_changes.map(c => ({label: c.label, before: c.before, after: c.after})))}
      <div class="small muted">${esc(S.disclaimer)}</div>`;
  };
  $$('#simCard input').forEach(i => i.onchange = run);
  const setAll = fn => { $$('#simCard input').forEach(i => i.checked = fn(i.dataset.f)); run(); };
  $('#sImm').onclick = () => setAll(f => !!A.recommendations.find(r => r.finding_type === f && r.priority === 'IMMEDIATE'));
  $('#sAll').onclick = () => setAll(() => true); $('#sNone').onclick = () => setAll(() => false);
  run();
}
init();

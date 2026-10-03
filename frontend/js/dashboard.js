/* FILE: frontend/js/dashboard.js - builds the dashboard from /api/dashboard/stats + one assessment */
renderNav('dashboard');
const qs = new URLSearchParams(location.search);
let source = qs.get('demo') ? 'demo' : (qs.get('id') ? 'id' : (Session.id ? 'mine' : 'demo'));

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const CAT_ORDER = ['profile','personal_info','location','content','connections','tagging','account_security','third_party','social_engineering','footprint'];
const card = (cls, title, tag, body) => `<section class="card ${cls}"><h3><span>${title}</span>${tag ? `<span class="tag">${tag}</span>` : ''}</h3><div class="grow">${body}</div></section>`;

async function load() {
  try {
    const stats = await api('/dashboard/stats');
    let a, answers = null, sim = null, simAll = null;
    if (source === 'demo') {
      a = await api('/demo'); answers = a.answers; sim = a.immediate_simulation;
    } else {
      const id = source === 'id' ? qs.get('id') : Session.id;
      a = await api('/assessment/' + encodeURIComponent(id)); answers = source === 'mine' ? Session.answers : null;
      if (answers) sim = await api('/assessment/simulate-improvement', {json: {answers, fix_priority: 'IMMEDIATE'}});
    }
    if (answers) simAll = await api('/assessment/simulate-improvement', {json: {answers, fix_all: true}});
    render(stats, a, sim, simAll);
  } catch (e) {
    if (source !== 'demo') { source = 'demo'; Session.clear(); return load(); }
    const el = $('#err'); el.hidden = false; el.textContent = 'Could not load dashboard: ' + e.message;
  }
}

function render(S, A, SIM, SIMALL) {
  const mine = new Set(A.findings.map(f => f.finding_type));
  const catScore = Object.fromEntries(A.category_scores.map(c => [c.key, c.score]));
  const avg = S.avg_category_scores, lv = A.risk_level, col = LEVEL_COLOR[lv];
  $('#subtitle').innerHTML = `${A.demo ? 'Fictional demo profile' : 'Your assessment <b>' + esc(A.assessment_id) + '</b>'} compared with a <b>${S.cohort_size.toLocaleString()}</b>-profile synthetic cohort · educational model, not a guarantee`;
  $('#srcMine').hidden = !Session.id; $('#srcMine').onclick = () => { source = 'mine'; load(); };
  $('#srcDemo').onclick = () => { source = 'demo'; load(); };
  $('#viewResults').href = A.demo ? '/results?demo=1' : '/results?id=' + encodeURIComponent(A.assessment_id);

  const rc = A.recommendation_counts, nRec = A.recommendations.length;
  const potential = SIM ? SIM.risk_reduction : A.potential_reduction;
  const ctrlPct = Math.round(100 * A.controls_enabled / A.controls_total);
  $('#kpis').innerHTML = [
    ['Overall Risk Score', `<div class="val" style="color:${col}">${A.overall_score}<small> /100</small></div><div class="sub">Riskier than ${A.percentile}% of the cohort</div>
      <div class="mini"><div class="track" style="--c:${col}"><i style="width:${A.overall_score}%"></i><b style="left:${Math.min(99, S.average_score)}%"></b></div><div class="small muted" style="margin-top:4px">| cohort avg ${S.average_score}</div></div>`, col],
    ['Risk Level', `<div class="val" style="color:${col};font-size:1.9rem">${esc(lv)}</div><div class="sub">${lv === 'LOW' ? '0–20' : lv === 'MODERATE' ? '21–40' : lv === 'HIGH' ? '41–70' : '71–100'} band · higher = more exposure</div>
      <div class="mini">${pillLevel(lv)}</div>`, col],
    ['High-Risk Categories', `<div class="val">${A.high_risk_categories.length}<small> of 10</small></div><div class="sub">${A.high_risk_categories.length ? esc(A.high_risk_categories.slice(0, 3).join(', ')) + (A.high_risk_categories.length > 3 ? ' +' + (A.high_risk_categories.length - 3) : '') : 'None at 41+ score'}</div>`, '#f97316'],
    ['Recommendations', `<div class="val">${nRec}</div><div class="sub">${rc.IMMEDIATE} immediate · ${rc.IMPORTANT} important · ${rc['GOOD PRACTICE']} good practice</div>`, '#8b5cf6'],
    ['Security Controls Enabled', `<div style="display:flex;align-items:center;gap:12px"><div>${Charts.ring(ctrlPct, ctrlPct >= 70 ? '#22c55e' : ctrlPct >= 40 ? '#eab308' : '#ef4444', A.controls_enabled + '/' + A.controls_total, 'controls')}</div><div class="sub">MFA, alerts, reviews & more</div></div>`, '#22c55e'],
    ['Potential Reduction', `<div class="val" style="color:#22c55e">−${potential}<small> pts</small></div><div class="sub">${SIM ? 'Simulated: fix all IMMEDIATE items → ' + SIM.after.score + ' (' + SIM.after.level + ')' : 'Points saved by fixing IMMEDIATE items'}</div>`, '#22c55e']
  ].map(k => `<section class="card kpi" style="--kc:${k[2]}"><div class="lab">${k[0]}</div>${k[1]}</section>`).join('');

  /* ---- Row 2 : radar | category bars | gauge ---- */
  const labels = CAT_ORDER.map(k => A.category_scores.find(c => c.key === k).short.replace('Social Engineering', 'Social Eng.').replace('Third-Party Apps', '3rd-Party Apps'));
  const radar = Charts.radar(labels, [
    {name: 'Cohort average', color: '#8b5cf6', values: CAT_ORDER.map(k => avg[k]), fill: .12, dash: true},
    {name: 'You', color: col, values: CAT_ORDER.map(k => catScore[k]), dots: true, fill: .28}]) +
    `<div class="legend"><span><i style="background:${col}"></i>${A.demo ? 'Demo profile' : 'You'}</span><span><i style="background:#8b5cf6"></i>Synthetic cohort average</span><span>Higher = higher risk</span></div>`;
  const sorted = [...A.category_scores].sort((a, b) => b.score - a.score);
  const catBars = Charts.bars(sorted.map(c => ({label: c.label, value: c.score, color: LEVEL_COLOR[c.level], right: c.score + ' · ' + c.level, marker: avg[c.key]})))
    + `<div class="legend"><span><i style="background:#fff;width:3px"></i>cohort average</span><span><i style="background:#22c55e"></i>Low</span><span><i style="background:#eab308"></i>Mod</span><span><i style="background:#f97316"></i>High</span><span><i style="background:#ef4444"></i>Crit</span></div>`;
  const bandRows = [['LOW', '0–20'], ['MODERATE', '21–40'], ['HIGH', '41–70'], ['CRITICAL', '71–100']].map(([l, r]) =>
    `<div class="item" style="padding:7px 0;align-items:center"><span class="pill lvl ${l}">${l}</span><span class="small muted">${r}</span><span class="pts" style="--c:${LEVEL_COLOR[l]}">${Math.round(100 * S.level_counts[l] / S.cohort_size)}%</span></div>`).join('');
  const gaugeCard = Charts.gauge(A.overall_score, lv) + `<div style="text-align:center" class="small muted">Your score vs. ${S.cohort_size.toLocaleString()} synthetic profiles</div>` + `<div>${bandRows}</div>`;

  /* ---- Row 3 : top weaknesses | controls | footprint ---- */
  const prioCol = {IMMEDIATE: '#ef4444', IMPORTANT: '#f97316', 'GOOD PRACTICE': '#3b82f6'};
  const weak = Charts.bars(S.top_weaknesses.slice(0, 9).map(w => ({label: w.title, value: w.percent, color: prioCol[w.priority], right: w.percent + '%', you: mine.has(w.finding_type)})))
    + `<div class="legend"><span><i style="background:#ef4444"></i>Immediate</span><span><i style="background:#f97316"></i>Important</span><span><i style="background:#3b82f6"></i>Good practice</span><span>% of cohort affected</span></div>`;
  const ctrlMine = Object.fromEntries(A.controls.map(c => [c.label, c.enabled]));
  const controls = Charts.bars(S.controls_adoption.map(c => ({label: c.label, value: c.percent, color: c.percent >= 50 ? '#22c55e' : c.percent >= 25 ? '#eab308' : '#ef4444',
    right: c.percent + '% · ' + (ctrlMine[c.label] ? '✓ you' : '✗ you')}))) + `<div class="legend"><span>Cohort adoption of each control, and whether you have it</span></div>`;
  const stackDef = [['old_posts_reviewed', 'Old posts reviewed'], ['privacy_settings_reviewed', 'Settings reviewed'], ['unused_accounts', 'Unused accounts active'], ['photo_metadata_awareness', 'Photo metadata managed'], ['public_comments', 'Personal details in public comments']];
  const stackCol = {RECENT: '#22c55e', OLD: '#eab308', NEVER: '#ef4444', NOT_SURE: '#64748b', YES: '#ef4444', NO: '#22c55e', SOMETIMES: '#eab308'};
  const stackOrder = {old_posts_reviewed: ['RECENT', 'OLD', 'NEVER', 'NOT_SURE'], privacy_settings_reviewed: ['RECENT', 'OLD', 'NEVER', 'NOT_SURE'], unused_accounts: ['NO', 'YES', 'NOT_SURE'], photo_metadata_awareness: ['YES', 'SOMETIMES', 'NO', 'NOT_SURE'], public_comments: ['NEVER', 'SOMETIMES', 'OFTEN', 'NOT_SURE']};
  const stackColFix = {public_comments: {NEVER: '#22c55e', SOMETIMES: '#eab308', OFTEN: '#ef4444', NOT_SURE: '#64748b'}, photo_metadata_awareness: {YES: '#22c55e', SOMETIMES: '#eab308', NO: '#ef4444', NOT_SURE: '#64748b'}};
  const stacks = stackDef.map(([k, lab]) => { const d = S.footprint.distributions[k], tot = Object.values(d).reduce((x, y) => x + y, 0);
    return `<div class="row"><div class="top"><span>${lab}</span></div><div style="display:flex;height:11px;border-radius:99px;overflow:hidden;gap:2px">${stackOrder[k].filter(o => d[o]).map(o => `<i title="${o}: ${Math.round(100 * d[o] / tot)}%" style="width:${100 * d[o] / tot}%;background:${(stackColFix[k] || stackCol)[o]}"></i>`).join('')}</div></div>`; }).join('');
  const fp = `<div style="display:flex;align-items:center;gap:12px">${Charts.ring(catScore.footprint, colorOf(catScore.footprint), catScore.footprint, 'footprint')}<div><div class="small muted">Your footprint risk</div><div style="font-weight:700;color:${colorOf(catScore.footprint)}">${levelOf(catScore.footprint)}</div><div class="small muted">cohort avg ${avg.footprint}</div></div></div>
    <div class="rows">${stacks}</div><div class="legend"><span><i style="background:#22c55e"></i>Good</span><span><i style="background:#eab308"></i>Dated</span><span><i style="background:#ef4444"></i>Risky</span></div>`;

  /* ---- Row 4 : improvement | biggest wins | heatmap ---- */
  let imp;
  if (SIM) {
    imp = `<div class="ba"><div><div class="small muted">CURRENT</div><div class="num" style="color:${col}">${SIM.before.score}</div>${pillLevel(SIM.before.level)}</div><div class="arrow">➜</div>
      <div><div class="small muted">AFTER IMMEDIATE FIXES</div><div class="num" style="color:${LEVEL_COLOR[SIM.after.level]}">${SIM.after.score}</div>${pillLevel(SIM.after.level)}</div></div>`
      + Charts.compare(SIM.category_changes.map(c => ({label: c.label, before: c.before, after: c.after})))
      + `<div class="legend"><span>Top bar: current · Bottom bar: after applying all IMMEDIATE recommendations${SIMALL ? ' · all fixes → ' + SIMALL.after.score : ''}. Framework simulation, not a guarantee.</span></div>`;
  } else {
    const I = S.improvement;
    imp = `<div class="ba"><div><div class="small muted">COHORT AVERAGE</div><div class="num" style="color:${colorOf(I.before)}">${Math.round(I.before)}</div></div><div class="arrow">➜</div><div><div class="small muted">AFTER IMMEDIATE FIXES</div><div class="num" style="color:${colorOf(I.after_immediate)}">${Math.round(I.after_immediate)}</div></div></div>`
      + Charts.compare([{label: 'Current average', before: Math.round(I.before), after: Math.round(I.before)}, {label: 'After immediate fixes', before: Math.round(I.before), after: Math.round(I.after_immediate)}, {label: 'After all recommendations', before: Math.round(I.before), after: Math.round(I.after_all)}])
      + `<div class="legend"><span>Take a new assessment to see your personal comparison.</span></div>`;
  }
  const wins = Charts.bars(S.biggest_wins.map(w => ({label: w.title, value: w.avg_points, max: S.biggest_wins[0].avg_points, color: '#22d3ee', right: '−' + w.avg_points + ' pts'})))
    + `<div class="legend"><span>Average points removed from a profile's score by fixing just this one thing</span></div>`;
  const heat = Charts.heat(S.category_heatmap, ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']) + `<div class="legend"><span>Average category score by overall risk level</span></div>`;

  /* ---- Row 5 : distribution | histogram | trend ---- */
  const L = S.level_counts, donut = Charts.donut(['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].map(l => ({label: l, value: L[l], color: LEVEL_COLOR[l]})), S.cohort_size.toLocaleString(), 'synthetic profiles')
    + `<div class="rows" style="flex:none">${['LOW', 'MODERATE', 'HIGH', 'CRITICAL'].map(l => `<div class="row"><div class="top"><span>${pillLevel(l)}</span><span><b>${L[l]}</b> <span class="muted">(${Math.round(100 * L[l] / S.cohort_size)}%)</span>${l === lv ? ' <span class="you">YOU</span>' : ''}</span></div></div>`).join('')}</div>`;
  const hist = Charts.histogram(S.histogram, Math.min(9, Math.floor(A.overall_score / 10))) + `<div class="legend"><span>Number of profiles per 10-point score band · outlined bar = your band</span></div>`;
  const trend = Charts.line(S.trend.map(t => ({label: MONTHS[+t.month.slice(5) - 1], value: t.average}))) + `<div class="legend"><span>Cohort average risk score by month (synthetic) — lower is better</span></div>`;

  /* ---- Row 6 : segments | priority actions | awareness ---- */
  const hi = S.segments[0], lo = S.segments[S.segments.length - 1];
  const strip = `<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">${[['Cohort avg', S.average_score, colorOf(S.average_score)], ['Median', S.median_score, colorOf(S.median_score)], ['Spread', Math.round(hi.average - lo.average) + ' pts', '#22d3ee']].map(b => `<div style="background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px;text-align:center"><div class="small muted">${b[0]}</div><div style="font-weight:800;font-size:1.2rem;color:${b[2]}">${b[1]}</div></div>`).join('')}</div>`;
  const seg = strip + Charts.bars(S.segments.map(s => ({label: s.segment + ' (' + s.count + ')', value: s.average, color: colorOf(s.average), right: s.average, marker: S.average_score}))) + `<div class="legend"><span>Average risk by synthetic user segment · marker = overall cohort average</span></div>`;
  const acts = A.recommendations.slice(0, 5).map((r, i) => `<div class="item" style="padding:9px 0"><div class="n">${i + 1}</div><div style="min-width:0"><div class="t">${esc(r.risk)}</div><div class="d">${esc(r.recommendation)}</div></div><div style="margin-left:auto;text-align:right">${pillPrio(r.priority)}<div class="small" style="color:#22c55e;margin-top:3px">−${r.points_saved.toFixed(1)} pts</div></div></div>`).join('') || '<div class="muted">No outstanding recommendations. Great work.</div>';
  const tip = S.tips[new Date().getDate() % S.tips.length];
  const aware = `<div style="background:linear-gradient(135deg,#0e749044,#6d28d944);border:1px solid var(--line);border-radius:12px;padding:14px"><div class="small muted">💡 AWARENESS TIP</div><div style="font-weight:600;margin-top:4px">${esc(tip)}</div></div>
    ${[1, 2].map(k => `<div class="small" style="border-left:3px solid var(--accent);padding:2px 0 2px 10px;color:var(--muted)">${esc(S.tips[(new Date().getDate() + k) % S.tips.length])}</div>`).join('')}
    <div class="rows" style="flex:none"><div class="row"><div class="top"><span>Privacy vs. security</span></div><div class="small muted">A strong password protects the account; privacy settings control what the account <i>reveals</i>. You need both.</div></div></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn sm" href="/checklist">Privacy checklist</a><a class="btn sm" href="/tools">Metadata tool</a></div>
    <div class="small muted">${S.live.count} assessment(s) stored on this server · scores only, no personal data</div>`;

  $('#rows').innerHTML =
    card('s5', 'Category Risk Scores', 'radar · 10 categories', radar) + card('s4', 'Category Breakdown', 'sorted by risk', catBars) + card('s3', 'Risk Gauge', 'your position', gaugeCard) +
    card('s5', 'Top Privacy Weaknesses', 'prevalence in cohort', weak) + card('s4', 'Account Security Controls', 'adoption', controls) + card('s3', 'Digital Footprint Risk', 'self-reported', fp) +
    card('s5', 'Privacy Improvement Comparison', 'before vs after', imp) + card('s4', 'Biggest Single Wins', 'avg. points saved', wins) + card('s3', 'Risk Heatmap', 'category × level', heat) +
    card('s4', 'Privacy Risk Distribution', 'cohort', donut) + card('s4', 'Score Distribution', 'histogram', hist) + card('s4', 'Risk Trend', '12 months', trend) +
    card('s4', 'Risk by Segment', 'synthetic', seg) + card('s5', 'Priority Action Plan', 'top 5', acts) + card('s3', 'Awareness Corner', '', aware);
}
load();

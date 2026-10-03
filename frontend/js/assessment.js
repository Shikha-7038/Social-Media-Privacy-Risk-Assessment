/* FILE: frontend/js/assessment.js - category-by-category questionnaire wizard */
renderNav('assessment');
let Q, step = 0; const answers = {};
const total = () => Q.total_questions, answered = () => Object.keys(answers).length;

function draw() {
  const c = Q.categories[step];
  $('#steps').innerHTML = Q.categories.map((k, i) => {
    const done = k.questions.every(q => answers[q.id]);
    return `<div class="step ${i === step ? 'active' : ''} ${done ? 'done' : ''}" data-i="${i}"><span class="dot">${done ? '✓' : k.letter}</span>${esc(k.label)}</div>`; }).join('');
  $$('.step').forEach(e => e.onclick = () => { step = +e.dataset.i; draw(); window.scrollTo({top: 0}); });
  $('#panel').innerHTML = `<h2>Category ${c.letter}: ${esc(c.label)}</h2><div class="muted small">${esc(c.blurb)}</div>` + c.questions.map(q => `
    <div class="q"><div class="qt">${esc(q.id)}. ${esc(q.text)}</div><div class="qh">${esc(q.help)}</div>
    <div class="opts" data-q="${q.id}">${q.options.map(o => `<button type="button" class="opt ${answers[q.id] === o.value ? 'sel' : ''}" data-v="${o.value}">${esc(o.label)}</button>`).join('')}</div></div>`).join('');
  $$('.opts').forEach(g => g.onclick = e => { const b = e.target.closest('.opt'); if (!b) return; answers[g.dataset.q] = b.dataset.v;
    $$('.opt', g).forEach(x => x.classList.toggle('sel', x === b)); progress(); markDone(); });
  progress();
  $('#back').disabled = step === 0;
  $('#next').textContent = step === Q.categories.length - 1 ? 'Calculate my score ✓' : 'Next →';
}
function markDone() { $$('.step').forEach((e, i) => { const d = Q.categories[i].questions.every(q => answers[q.id]); e.classList.toggle('done', d); $('.dot', e).textContent = d ? '✓' : Q.categories[i].letter; }); }
function progress() { $('#bar').style.width = (100 * answered() / total()) + '%'; $('#count').textContent = `${answered()} of ${total()} answered`; }

async function next() {
  const c = Q.categories[step], missing = c.questions.filter(q => !answers[q.id]);
  if (missing.length) { $('#msg').textContent = `Please answer ${missing.length} more question(s) in this section.`; $$('.q')[c.questions.indexOf(missing[0])].scrollIntoView({behavior: 'smooth', block: 'center'}); return; }
  $('#msg').textContent = '';
  if (step < Q.categories.length - 1) { step++; draw(); window.scrollTo({top: 0}); return; }
  $('#next').disabled = true; $('#msg').textContent = 'Calculating…';
  try { const r = await api('/assessment', {json: {answers}}); Session.save(r.assessment_id, answers); location.href = '/results?id=' + encodeURIComponent(r.assessment_id); }
  catch (e) { $('#msg').textContent = 'Error: ' + e.message; $('#next').disabled = false; }
}
$('#next').onclick = next; $('#back').onclick = () => { if (step) { step--; draw(); } };
$('#demoFill').onclick = async () => { const d = await api('/demo'); Object.assign(answers, d.answers); draw(); $('#msg').textContent = 'Demo (fictional) answers loaded.'; };
api('/questionnaire').then(q => { Q = q; draw(); });

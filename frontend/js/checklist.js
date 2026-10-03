/* FILE: frontend/js/checklist.js - tick state lives in localStorage (non-sensitive) */
renderNav('checklist');
let items = [], done = new Set(JSON.parse(localStorage.getItem('pra_checklist') || '[]'));
function draw() {
  $('#list').innerHTML = items.map(i => `<label class="ck ${done.has(i.id) ? 'done' : ''}"><input type="checkbox" data-id="${i.id}" ${done.has(i.id) ? 'checked' : ''}><span>${esc(i.text)}</span></label>`).join('');
  $$('#list input').forEach(c => c.onchange = () => { c.checked ? done.add(+c.dataset.id) : done.delete(+c.dataset.id); localStorage.setItem('pra_checklist', JSON.stringify([...done])); draw(); });
  const p = Math.round(100 * done.size / items.length);
  $('#ring').innerHTML = Charts.ring(p, p === 100 ? '#22c55e' : '#22d3ee', p + '%', 'done'); $('#pct').textContent = `${done.size} of ${items.length} completed`;
}
api('/privacy-checklist').then(d => { items = d.items; $('#disc').textContent = d.disclaimer; draw();
  $('#printBtn').onclick = () => window.print();
  $('#dlBtn').onclick = () => { const t = d.title + '\n\n' + items.map(i => (done.has(i.id) ? '[x] ' : '[ ] ') + i.text).join('\n') + '\n\n' + d.disclaimer;
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([t], {type: 'text/plain'})); a.download = 'privacy-checklist.txt'; a.click(); }; });

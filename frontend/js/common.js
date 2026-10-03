/* FILE: frontend/js/common.js - helpers shared by every page (no frameworks) */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const LEVEL_COLOR = {LOW:'#22c55e', MODERATE:'#eab308', HIGH:'#f97316', CRITICAL:'#ef4444'};
const levelOf = s => s <= 20 ? 'LOW' : s <= 40 ? 'MODERATE' : s <= 70 ? 'HIGH' : 'CRITICAL';
const colorOf = s => LEVEL_COLOR[levelOf(Math.round(s))];
const prioClass = p => p === 'GOOD PRACTICE' ? 'GOOD' : p;
const pillLevel = l => `<span class="pill lvl ${esc(l)}">${esc(l)}</span>`;
const pillPrio = p => `<span class="pill ${prioClass(p)}">${esc(p)}</span>`;

async function api(path, opts = {}) {
  const o = {headers: {}, ...opts};
  if (o.json !== undefined) { o.method = o.method || 'POST'; o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(o.json); }
  const res = await fetch('/api' + path, o);
  let data = null; try { data = await res.json(); } catch (e) { /* not json */ }
  if (!res.ok) throw new Error((data && (data.details || []).join(' ')) || (data && data.error) || ('HTTP ' + res.status));
  return data;
}
/* sessionStorage keeps only the assessment id + answers for THIS tab; closing the tab erases it. */
const Session = {
  get id() { return sessionStorage.getItem('pra_id'); },
  get answers() { try { return JSON.parse(sessionStorage.getItem('pra_answers')); } catch (e) { return null; } },
  save(id, answers) { sessionStorage.setItem('pra_id', id); sessionStorage.setItem('pra_answers', JSON.stringify(answers)); },
  clear() { sessionStorage.removeItem('pra_id'); sessionStorage.removeItem('pra_answers'); }
};
function renderNav(active) {
  const links = [['/', 'Home', 'home'], ['/assessment', 'Assessment', 'assessment'], ['/dashboard', 'Dashboard', 'dashboard'],
                 ['/checklist', 'Checklist', 'checklist'], ['/tools', 'Metadata Tool', 'tools']];
  $('#nav').outerHTML = `<header class="nav no-print"><div class="wrap">
    <a class="brand" href="/"><span class="logo">🛡️</span><span>Privacy Risk Framework</span></a>
    ${links.map(l => `<a class="link ${l[2] === active ? 'active' : ''}" href="${l[0]}">${l[1]}</a>`).join('')}
    <span class="spacer"></span><a class="btn primary sm" href="/assessment">Start Privacy Assessment</a></div></header>`;
}
const FOOTER = `<footer class="footer wrap">Educational defensive-privacy project. Uses synthetic or voluntarily provided answers; it does not scrape, track or profile real people.
Scores come from an educational risk model, not a guarantee that an account will or will not be compromised.</footer>`;
document.addEventListener('DOMContentLoaded', () => { const f = $('#footer'); if (f) f.outerHTML = FOOTER; });

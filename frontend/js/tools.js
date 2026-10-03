/* FILE: frontend/js/tools.js - local metadata viewer / cleaner UI */
renderNav('tools');
const drop = $('#drop'), input = $('#file');
['dragover', 'dragenter'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', ev => { if (ev.dataTransfer.files[0]) handle(ev.dataTransfer.files[0]); });
input.onchange = () => input.files[0] && handle(input.files[0]);

async function handle(file) {
  const fd = new FormData(); fd.append('image', file);
  $('#preview').innerHTML = `<img src="${URL.createObjectURL(file)}" alt="selected image preview" style="max-width:100%;max-height:260px;border-radius:10px">`;
  try {
    const m = await api('/metadata/inspect', {method: 'POST', body: fd});
    const rows = Object.entries(m.fields).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('');
    const f = m.flags, flag = (ok, t) => `<span class="pill lvl ${ok ? 'HIGH' : 'LOW'}">${ok ? '⚠ ' : '✓ '}${t}</span>`;
    $('#out').innerHTML = `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">${flag(f.has_gps, f.has_gps ? 'GPS present' : 'No GPS')}${flag(f.has_device, f.has_device ? 'Device info' : 'No device info')}${flag(f.has_timestamp, f.has_timestamp ? 'Timestamp' : 'No timestamp')}</div>
      <div class="small muted">${esc(m.format)} · ${m.size[0]}×${m.size[1]} · ${m.field_count} metadata field(s)</div>
      ${m.gps ? `<div class="banner" style="margin:10px 0">GPS in file: ${esc(JSON.stringify(m.gps))} — anyone who receives this original file could see it.</div>` : ''}
      <table class="t" style="margin:10px 0">${rows || '<tr><td>No EXIF fields found.</td></tr>'}</table>
      <button class="btn primary" id="clean">⬇ Download a cleaned copy (metadata removed)</button>`;
    $('#clean').onclick = async () => { const r = await fetch('/api/metadata/strip', {method: 'POST', body: fd}); if (!r.ok) return alert('Could not clean image');
      const a = document.createElement('a'); a.href = URL.createObjectURL(await r.blob()); a.download = r.headers.get('Content-Disposition').match(/filename="(.+)"/)[1]; a.click(); };
  } catch (e) { $('#out').innerHTML = `<div class="banner">${esc(e.message)}</div>`; }
}

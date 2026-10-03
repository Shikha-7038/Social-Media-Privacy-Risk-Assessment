/* FILE: frontend/js/charts.js - dependency-free SVG/HTML charts (work offline).
   Every function returns an HTML string; all dynamic text is escaped. */
const Charts = (() => {
  const P = (cx, cy, r, deg) => [cx + r * Math.cos(deg * Math.PI / 180), cy - r * Math.sin(deg * Math.PI / 180)];
  const arc = (cx, cy, r, v0, v1) => {            // semicircle gauge arc, v in 0..100
    const [x0, y0] = P(cx, cy, r, 180 - v0 * 1.8), [x1, y1] = P(cx, cy, r, 180 - v1 * 1.8);
    return `M${x0.toFixed(1)} ${y0.toFixed(1)} A${r} ${r} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
  };

  function gauge(score, level) {
    const bands = [[0, 20, '#22c55e'], [20, 40, '#eab308'], [40, 70, '#f97316'], [70, 100, '#ef4444']];
    const [nx, ny] = P(120, 120, 74, 180 - score * 1.8);
    return `<svg class="chart" viewBox="0 0 240 150" role="img" aria-label="Risk gauge ${score} of 100">
      <path d="${arc(120, 120, 90, 0, 100)}" stroke="#0a1224" stroke-width="22" fill="none" stroke-linecap="round"/>
      ${bands.map(b => `<path d="${arc(120, 120, 90, b[0] + .6, b[1] - .6)}" stroke="${b[2]}" stroke-width="16" fill="none" opacity="${score >= b[0] && score <= b[1] ? 1 : .35}"/>`).join('')}
      <line x1="120" y1="120" x2="${nx.toFixed(1)}" y2="${ny.toFixed(1)}" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
      <circle cx="120" cy="120" r="7" fill="#fff"/>
      <text class="big" x="120" y="100" text-anchor="middle" font-size="34" font-weight="800" style="fill:${LEVEL_COLOR[level]}">${score}</text>
      <text x="26" y="142" font-size="10" text-anchor="middle">0</text><text x="214" y="142" font-size="10" text-anchor="middle">100</text>
      <text x="120" y="144" text-anchor="middle" font-size="11" font-weight="700" style="fill:${LEVEL_COLOR[level]}">${esc(level)}</text></svg>`;
  }

  function radar(labels, series) {
    const n = labels.length, cx = 220, cy = 172, R = 112;
    const pt = (i, v) => P(cx, cy, R * v / 100, 90 - i * 360 / n);
    const rings = [25, 50, 75, 100].map(v => `<polygon points="${labels.map((_, i) => pt(i, v).map(x => x.toFixed(1)).join(',')).join(' ')}" fill="none" stroke="#233453" stroke-width="1"/>`).join('');
    const axes = labels.map((_, i) => { const [x, y] = pt(i, 100); return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#1b2a47"/>`; }).join('');
    const lab = labels.map((t, i) => { const [x, y] = P(cx, cy, R + 20, 90 - i * 360 / n);
      const a = Math.abs(x - cx) < 8 ? 'middle' : x > cx ? 'start' : 'end';
      return `<text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="${a}" font-size="11">${esc(t)}</text>`; }).join('');
    const shapes = series.map(s => `<polygon points="${s.values.map((v, i) => pt(i, v).map(x => x.toFixed(1)).join(',')).join(' ')}"
      fill="${s.color}" fill-opacity="${s.fill ?? .22}" stroke="${s.color}" stroke-width="2" ${s.dash ? 'stroke-dasharray="5 4"' : ''}/>` +
      (s.dots ? s.values.map((v, i) => { const [x, y] = pt(i, v); return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" fill="${s.color}"/>`; }).join('') : '')).join('');
    return `<svg class="chart" viewBox="0 0 440 345" role="img" aria-label="Category risk radar">${rings}${axes}${shapes}${lab}
      ${[25, 50, 75].map(v => `<text x="${cx + 3}" y="${(cy - R * v / 100 + 10).toFixed(1)}" font-size="8" opacity=".7">${v}</text>`).join('')}</svg>`;
  }

  function donut(segs, top, bottom) {
    const total = segs.reduce((a, s) => a + s.value, 0) || 1, r = 52, C = 2 * Math.PI * r; let off = 0;
    const rings = segs.map(s => { const len = C * s.value / total, el =
      `<circle r="${r}" cx="70" cy="70" fill="none" stroke="${s.color}" stroke-width="20" stroke-dasharray="${Math.max(0, len - 1.5).toFixed(1)} ${(C - len + 1.5).toFixed(1)}" stroke-dashoffset="${(-off).toFixed(1)}" transform="rotate(-90 70 70)"/>`;
      off += len; return el; }).join('');
    return `<svg class="chart" viewBox="0 0 140 140" style="max-height:170px" role="img"><circle r="${r}" cx="70" cy="70" fill="none" stroke="#0a1224" stroke-width="20"/>${rings}
      <text class="big" x="70" y="68" text-anchor="middle" font-size="22" font-weight="800">${esc(top)}</text>
      <text x="70" y="84" text-anchor="middle" font-size="9">${esc(bottom)}</text></svg>`;
  }

  function ring(pct, color, big, small) {
    const r = 30, C = 2 * Math.PI * r;
    return `<svg viewBox="0 0 80 80" style="width:84px;height:84px"><circle cx="40" cy="40" r="${r}" fill="none" stroke="#0a1224" stroke-width="9"/>
      <circle cx="40" cy="40" r="${r}" fill="none" stroke="${color}" stroke-width="9" stroke-linecap="round" stroke-dasharray="${(C * pct / 100).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 40 40)"/>
      <text class="big" x="40" y="44" text-anchor="middle" font-size="15" font-weight="800">${esc(big)}</text>
      ${small ? `<text x="40" y="55" text-anchor="middle" font-size="7">${esc(small)}</text>` : ''}</svg>`;
  }

  function histogram(bins, mark) {            // bins: 10 counts (0-9, 10-19 ...)
    const W = 400, H = 150, max = Math.max(...bins, 1), bw = W / bins.length;
    return `<svg class="chart" viewBox="0 0 ${W} ${H + 26}" preserveAspectRatio="none" role="img" aria-label="Score distribution">
      ${bins.map((b, i) => { const h = Math.max(2, (H - 16) * b / max), mid = i * 10 + 5, x = i * bw + 4;
        return `<rect x="${x}" y="${H - h}" width="${bw - 8}" height="${h}" rx="4" fill="${colorOf(mid)}" opacity="${mark === i ? 1 : .72}" ${mark === i ? 'stroke="#fff" stroke-width="2"' : ''}/>
        <text x="${x + (bw - 8) / 2}" y="${H - h - 4}" font-size="10" text-anchor="middle">${b}</text>
        <text x="${x + (bw - 8) / 2}" y="${H + 14}" font-size="9" text-anchor="middle">${i * 10}-${i === 9 ? 100 : i * 10 + 9}</text>`; }).join('')}</svg>`;
  }

  function line(points, color = '#22d3ee') {  // [{label,value}]
    const W = 400, H = 150, pad = 10, vals = points.map(p => p.value), lo = Math.floor(Math.min(...vals) - 4), hi = Math.ceil(Math.max(...vals) + 4);
    const X = i => pad + i * (W - 2 * pad) / (points.length - 1), Y = v => H - 8 - (H - 24) * (v - lo) / (hi - lo || 1);
    const d = points.map((p, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)} ${Y(p.value).toFixed(1)}`).join(' ');
    return `<svg class="chart" viewBox="0 0 ${W} ${H + 22}" preserveAspectRatio="none" role="img" aria-label="Trend line">
      <defs><linearGradient id="lg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".35"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
      ${[0, 1, 2, 3].map(k => `<line x1="0" x2="${W}" y1="${8 + k * (H - 24) / 3}" y2="${8 + k * (H - 24) / 3}" stroke="#1b2a47"/>`).join('')}
      <path d="${d} L${X(points.length - 1)} ${H} L${X(0)} ${H} Z" fill="url(#lg)"/><path d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round"/>
      ${points.map((p, i) => `<circle cx="${X(i).toFixed(1)}" cy="${Y(p.value).toFixed(1)}" r="3.2" fill="${color}"/>${i % 2 === 0 ? `<text x="${X(i).toFixed(1)}" y="${H + 16}" font-size="9" text-anchor="middle">${esc(p.label)}</text>` : ''}`).join('')}
      <text x="${X(points.length - 1)}" y="${(Y(points[points.length - 1].value) - 8).toFixed(1)}" font-size="11" font-weight="700" text-anchor="end" style="fill:#fff">${points[points.length - 1].value}</text></svg>`;
  }

  /* HTML horizontal bars. items: {label, value, max, color, right, you, marker} */
  function bars(items, max = 100) {
    return `<div class="rows">${items.map(it => `<div class="row"><div class="top"><span title="${esc(it.label)}">${esc(it.label)}${it.you ? '<span class="you">YOU</span>' : ''}</span>
      <span style="color:${it.color || '#e8eefb'};font-weight:700">${esc(it.right ?? it.value)}</span></div>
      <div class="track" style="--c:${it.color || '#22d3ee'}"><i style="width:${Math.min(100, 100 * it.value / (it.max || max))}%"></i>${it.marker != null ? `<b style="left:${Math.min(99, it.marker)}%" title="cohort average"></b>` : ''}</div></div>`).join('')}</div>`;
  }

  /* before/after paired bars */
  function compare(items) {
    return `<div class="rows">${items.map(it => `<div class="row"><div class="top"><span>${esc(it.label)}</span><span><span style="color:${colorOf(it.before)}">${it.before}</span> → <b style="color:${colorOf(it.after)}">${it.after}</b></span></div>
      <div class="track" style="margin-bottom:3px"><i style="width:${it.before}%;--c:${colorOf(it.before)};background:${colorOf(it.before)};opacity:.55"></i></div>
      <div class="track"><i style="width:${it.after}%;background:${colorOf(it.after)}"></i></div></div>`).join('')}</div>`;
  }

  function heat(rows, levels) {               // rows:[{category, values:{LOW:..}}]
    const cell = v => v == null ? '<div>–</div>' : `<div style="background:${colorOf(v)}${Math.round(18 + v * .55).toString(16).padStart(2, '0')};color:#fff;font-weight:700">${Math.round(v)}</div>`;
    return `<div class="heat"><div class="h"></div>${levels.map(l => `<div class="h">${l.slice(0, 4)}</div>`).join('')}
      ${rows.map(r => `<div class="rl">${esc(r.category)}</div>${levels.map(l => cell(r.values[l])).join('')}`).join('')}</div>`;
  }
  return {gauge, radar, donut, ring, histogram, line, bars, compare, heat};
})();

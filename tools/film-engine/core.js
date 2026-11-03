/* core.js — Startup Motion Studio film engine (adapted from howseen-ai/claude-motion-design remake core, MIT).
   EVERYTHING is a pure function of the global frame F. No timers, no Date, no Math.random, no CSS transitions.
   Shot files register SHOT({id, f0, f1, render(lf, F)}) and return an HTML string for the stage.
   Config comes from film.json via window.FILM (fps, w, h). */
(function () {
  const CFG = window.FILM || {};
  const FPS = CFG.fps || 30000 / 1001, W = CFG.w || 1920, H = CFG.h || 1080;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const inv = (a, b, x) => clamp((x - a) / (b - a));
  const sec = f => f / FPS, fr = s => Math.round(s * FPS);

  // ---- easings (exact 0/1 at the ends — never let a guard fire early)
  const E = {
    lin: t => t, inQ: t => t * t, inC: t => t * t * t,
    outQ: t => 1 - (1 - t) * (1 - t), ioQ: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
    outC: t => 1 - Math.pow(1 - t, 3), ioC: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
    outQuart: t => 1 - Math.pow(1 - t, 4), ioQuart: t => t < .5 ? 8 * t ** 4 : 1 - Math.pow(-2 * t + 2, 4) / 2,
    outExpo: t => t <= 0 ? 0 : t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
    ioExpo: t => t <= 0 ? 0 : t >= 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
    // Apple-ish ease cubic-bezier(0.16,1,0.3,1) approximated by an outExpo-ish curve
    brand: t => t <= 0 ? 0 : t >= 1 ? 1 : 1 - Math.pow(1 - t, 4.2),
  };

  // ---- Framer Motion / Motion spring physics (stiffness k, damping d, mass m, from rest 0 -> 1)
  // Same closed-form solution Motion uses (under-, critically and over-damped). tau in SECONDS.
  function springKD(tau, k = 170, d = 26, m = 1) {
    if (tau <= 0) return 0;
    const w0 = Math.sqrt(k / m), z = d / (2 * Math.sqrt(k * m));
    if (z < 1) { const wd = w0 * Math.sqrt(1 - z * z); return 1 - Math.exp(-z * w0 * tau) * (Math.cos(wd * tau) + (z * w0 / wd) * Math.sin(wd * tau)); }
    if (z === 1) return 1 - Math.exp(-w0 * tau) * (1 + w0 * tau);
    const r1 = -w0 * (z - Math.sqrt(z * z - 1)), r2 = -w0 * (z + Math.sqrt(z * z - 1));
    return 1 - (r2 * Math.exp(r1 * tau) - r1 * Math.exp(r2 * tau)) / (r2 - r1);
  }
  // presets (claude-motion-design): damping ratio >= 0.72, tiny overshoot, never cartoon bounce
  const SP = { ui: [320, 30], box: [170, 26], heavy: [120, 24], soft: [100, 20] };
  // sp(F, f0, 'ui') -> 0..~1.02 progress of a spring that starts at frame f0
  const sp = (F, f0, p = 'box') => { const [k, d] = Array.isArray(p) ? p : SP[p]; return springKD(sec(F - f0), k, d); };
  // spring between two values
  const spv = (F, f0, a, b, p = 'box') => lerp(a, b, sp(F, f0, p));
  // course step 08: a value with SEVERAL targets = sum of one spring per change (continuous, still frame-pure).
  // track(F, [[f0, v0], [f1, v1], ...], 'box') -> value at frame F
  const track = (F, keys, p = 'box') => keys.reduce((v, k, i) => i ? v + (k[1] - keys[i - 1][1]) * sp(F, k[0], p) : k[1], 0);
  // stretchy tab indicator / selection: leading edge stiffer than trailing edge
  const indicator = (F, stops, w = 120) => { const a = track(F, stops, 'ui'), b = track(F, stops, 'soft'); return { left: Math.min(a, b), right: Math.max(a, b) + w }; };
  // text inside a morphing container: in after the morph starts (fIn), out before the next one (fOut)
  const swapAlpha = (F, fIn, fOut, d = 4) => Math.min(clamp((F - fIn - 2) / d), clamp((fOut - 3 - F) / d));
  // seamless loop: last frame == first frame
  const loopF = (F, n) => ((F % n) + n) % n;

  // kf(F, [[f, v], ...], ease|easeArray) -> piecewise interpolation, holds ends
  function kf(F, keys, ease = E.ioC) {
    if (F <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      if (F <= keys[i][0]) {
        const [f0, v0] = keys[i - 1], [f1, v1] = keys[i];
        const e = Array.isArray(ease) ? (ease[i - 1] || E.ioC) : ease;
        return lerp(v0, v1, e((F - f0) / (f1 - f0)));
      }
    }
    return keys[keys.length - 1][1];
  }
  // samples(F, f0, arr): per-frame measured array (from REF measurements) starting at frame f0
  function samples(F, f0, arr) {
    const x = F - f0; if (x <= 0) return arr[0]; if (x >= arr.length - 1) return arr[arr.length - 1];
    const i = Math.floor(x), t = x - i; return lerp(arr[i], arr[i + 1], t);
  }
  // deterministic PRNG
  const rand = (n, s = 1) => { let x = Math.sin(n * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); };

  // ---- brand tokens: defaults below, overridden by brand/tokens.json (new_film.py copies it into film.json.tokens)
  // o / oDeep / oLight = the ONE accent colour (names kept short because every shot uses them)
  const T = {
    white: '#ffffff', paper: '#f7f7f5', ink: '#020108', black: '#000000',
    card: '#121212', card2: '#1c1c1e', line: 'rgba(255,255,255,0.08)', lineDark: 'rgba(2,1,8,0.08)',
    sub: '#8a8a8a', subDark: 'rgba(2,1,8,0.55)',
    o: '#5B5BF7', oDeep: '#3D3DD9', oLight: '#8C8CFF', oTint: '#EEEEFF',
    green: '#34C759',
    gradWarm: 'linear-gradient(180deg,#14142B 0%,#05050B 100%)',
    font: "'Inter', -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif",
  };
  Object.assign(T, CFG.tokens || {});
  const rgb = h => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255].join(','); };
  T.oRGB = rgb(T.o); T.oDeepRGB = rgb(T.oDeep); T.oLightRGB = rgb(T.oLight);
  if (!(CFG.tokens || {}).grad) T.grad = `linear-gradient(90deg,${T.oLight} 0%,${T.o} 45%,${T.oDeep} 100%)`;
  if (!(CFG.tokens || {}).glow) T.glow = `0 0 0 1px rgba(${T.oRGB},.55), 0 0 40px 6px rgba(${T.oRGB},.35), 0 0 120px 30px rgba(${T.oDeepRGB},.18)`;
  const A = n => 'assets/' + n;

  // ---- camera: one transform on a container; zoom keys interpolated in LOG space
  function camera(inner, { s = 1, tx = 0, ty = 0, ox = W / 2, oy = H / 2, rx = 0, ry = 0, persp = 2200, blur = 0, op = 1 } = {}) {
    const f = blur > 0.01 ? `filter:blur(${blur.toFixed(2)}px);` : '';
    const rot = (rx || ry) ? ` perspective(${persp}px) rotateX(${rx}deg) rotateY(${ry}deg)` : '';
    return `<div style="position:absolute;inset:0;transform-origin:${ox}px ${oy}px;transform:translate(${tx}px,${ty}px)${rot} scale(${s});opacity:${op};${f}">${inner}</div>`;
  }
  // cam(F, [[f, zoom, x, y], ...], ease) -> {s, tx, ty}; never zoom in/out back-to-back
  function cam(F, keys, ease = E.ioC) {
    const z = Math.exp(kf(F, keys.map(k => [k[0], Math.log(k[1])]), ease));
    return { s: z, tx: kf(F, keys.map(k => [k[0], k[2]]), ease), ty: kf(F, keys.map(k => [k[0], k[3]]), ease) };
  }
  // ---- cursor (macOS arrow), tip at (x,y)
  function cursor(x, y, { press = 0, scale = 1, op = 1 } = {}) {
    const s = scale * (1 - 0.12 * press);
    return `<svg style="position:absolute;left:${x}px;top:${y}px;transform-origin:0 0;transform:scale(${s});opacity:${op};overflow:visible;z-index:50" width="28" height="40" viewBox="0 0 28 40"><path d="M2 2 L2 31 L9.5 24 L14.5 36 L19 34 L14 22.5 L24 22.5 Z" fill="#000" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>`;
  }
  // ---- text
  const typed = (s, n) => s.slice(0, Math.max(0, Math.floor(n)));
  // per-word reveal (opacity/blur/y), stagger in seconds of progress t (0..1 timeline of the line)
  function words(s, t, { stagger = 0.12, dur = 0.35, y = 14, blur = 6, color = null, accent = [] } = {}) {
    const ws = s.split(' ');
    return ws.map((w, i) => {
      const e = E.outC(clamp((t - i * stagger) / dur));
      const col = accent.includes(i) ? `background:${T.grad};-webkit-background-clip:text;background-clip:text;color:transparent;` : (color ? `color:${color};` : '');
      return `<span style="display:inline-block;opacity:${e};transform:translateY(${(1 - e) * y}px);filter:blur(${(1 - e) * blur}px);${col}">${w}</span>`;
    }).join('<span style="display:inline-block;width:.26em"></span>');
  }
  // masked word rise (claude-motion-design): translateY 105% inside overflow:hidden, 55 ms stagger, small rotation
  function rise(s, F, f0, { stagger = 0.055, p = 'ui', rot = 4, accent = [] } = {}) {
    return s.split(' ').map((w, i) => {
      const e = clamp(sp(F, f0 + fr(i * stagger), p), 0, 1.03);
      const col = accent.includes(i) ? `background:${T.grad};-webkit-background-clip:text;background-clip:text;color:transparent;` : '';
      return `<span style="display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.08em"><span style="display:inline-block;transform:translateY(${(1 - e) * 105}%) rotate(${(1 - e) * rot}deg);transform-origin:0 100%;${col}">${w}</span></span>`;
    }).join('<span style="display:inline-block;width:.26em"></span>');
  }
  const gtext = (s, g = T.grad) => `<span style="background:${g};-webkit-background-clip:text;background-clip:text;color:transparent">${s}</span>`;
  // ---- brand marks (alpha PNG/SVG masks so any fill works)
  const mask = (src, w, h, fill) => `<div style="width:${w}px;height:${h}px;background:${fill};-webkit-mask:url(${A(src)}) center/contain no-repeat;mask:url(${A(src)}) center/contain no-repeat"></div>`;
  const mark = (size, fill = T.o) => mask('brand/mark.svg', size, size, fill);
  const wordmark = (w, fill = T.ink) => mask('brand/wordmark.svg', w, w * 0.25, fill);
  const img = (n, w, h = w, extra = '') => `<img src="${A(n)}" style="width:${w}px;height:${h}px;object-fit:cover;${extra}">`;

  // ---- pixel dissolve / pixel assembly (logo finale)
  function pixelDissolve(x, y, w, h, t, { cell = 24, colors = [T.o, T.oLight, T.oDeep, T.oTint], seed = 3 } = {}) {
    const cols = Math.ceil(w / cell), rows = Math.ceil(h / cell); let out = '';
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const k = r * cols + c, th = rand(k, seed);
      if (!(t > th * 0.8 && t < th * 0.8 + 0.35)) continue;
      out += `<div style="position:absolute;left:${x + c * cell}px;top:${y + r * cell}px;width:${cell}px;height:${cell}px;background:${colors[k % colors.length]};opacity:${(0.35 + 0.65 * rand(k, seed + 1)).toFixed(2)}"></div>`;
    }
    return out;
  }

  // ---- palette filter (remakes only, opt-in with film.json "paletteFilter": true): re-hue leftover reference-brand
  //      colours in hue range [hueFrom, hueTo] to the accent's hue (applied to the final HTML)
  function hexToRgb(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function rgbToHsl(r, g, b) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0, s = 0; const l = (mx + mn) / 2; if (mx !== mn) { const d = mx - mn; s = l > .5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h * 360, s, l]; }
  function hslToHex(h, s, l) { h /= 360; const f = n => { const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l); const c = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)); return Math.round(c * 255).toString(16).padStart(2, '0'); }; return '#' + f(0) + f(8) + f(4); }
  function paletteFilter(html) {
    if (CFG.paletteFilter !== true) return html;
    const [ah] = rgbToHsl(...hexToRgb(T.o)), lo = CFG.hueFrom ?? 185, hi = CFG.hueTo ?? 345;
    return html.replace(/#[0-9a-fA-F]{6}\b/g, m => {
      const [r, g, b] = hexToRgb(m); const [h, s, l] = rgbToHsl(r, g, b);
      if (s > 0.35 && h > lo && h < hi) return hslToHex(ah, Math.min(s, .95), l);
      return m;
    });
  }

  // ---- registry + seek
  const SHOTS = [];
  window.SHOT = def => { SHOTS.push(def); SHOTS.sort((a, b) => a.f0 - b.f0); };
  window.CORE = { FPS, W, H, clamp, lerp, inv, sec, fr, E, springKD, SP, sp, spv, track, indicator, swapAlpha, loopF, kf, samples, rand, T, A, camera, cam, cursor, typed, words, rise, gtext, mask, mark, wordmark, img, pixelDissolve, paletteFilter };
  window.seek = t => {
    const F = Math.round(t * FPS);
    const st = document.getElementById('stage');
    const s = SHOTS.find(x => F >= x.f0 && F < x.f1) || SHOTS[SHOTS.length - 1];
    let html = '';
    if (s && F >= s.f0 && F < s.f1) { try { html = s.render(F - s.f0, F); } catch (e) { html = `<div style="color:red;font:30px monospace;padding:40px">${s.id} error: ${e}</div>`; console.error(s.id, e); } }
    else html = `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:40px monospace;color:#bbb">F${F} - no shot</div>`;
    st.innerHTML = paletteFilter(html);
    return F;
  };
})();

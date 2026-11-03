/* ui.js — starter UI kit for films. Rebuild YOUR product's screens here from real screenshots (see the motion-film
   skill, references/ui-kit.md): copy a component, match radius / colours / type to the screenshot, keep it a pure
   function returning an HTML string. Animate by passing values computed from F (CORE.sp, CORE.track, ...).
   Accent colours come from CORE.T (brand/tokens.json). */
(function () {
  const C = window.CORE, T = C.T, clamp = C.clamp, lerp = C.lerp;
  const px = v => (typeof v === 'number' ? v + 'px' : v);
  const abs = (x, y, w, h, extra = '') => `position:absolute;left:${px(x)};top:${px(y)};${w != null ? `width:${px(w)};` : ''}${h != null ? `height:${px(h)};` : ''}${extra}`;

  // ---------------- icons (24-unit line icons, stroke = currentColor) ----------------
  const P = {
    hanger: 'M12 6.5a2 2 0 1 1 2-2M12 6.5v1.6L3.2 14.3a1.3 1.3 0 0 0 .8 2.4h16a1.3 1.3 0 0 0 .8-2.4L12 8.1',
    calendar: 'M4 6.5h16v13H4zM4 10.5h16M8.5 4v4M15.5 4v4',
    tag: 'M3.5 12.6V4.5h8.1l8.9 8.9-8.1 8.1zM8 8.5h.01',
    sparkle: 'M12 3.5c.6 3.9 2.6 5.9 6.5 6.5-3.9.6-5.9 2.6-6.5 6.5-.6-3.9-2.6-5.9-6.5-6.5 3.9-.6 5.9-2.6 6.5-6.5zM18.5 15.5c.2 1.4.9 2.1 2.3 2.3-1.4.2-2.1.9-2.3 2.3-.2-1.4-.9-2.1-2.3-2.3 1.4-.2 2.1-.9 2.3-2.3z',
    swap: 'M7 8h13l-3-3M17 16H4l3 3',
    figure: 'M12 5.5a1.6 1.6 0 1 0 0-.01M6 9h12M12 9v5M9 21l3-7 3 7',
    users: 'M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3.5 19.5c.6-3 2.8-4.5 5.5-4.5s4.9 1.5 5.5 4.5M16 5.3a3 3 0 0 1 0 5.4M17.5 15.2c1.7.5 2.8 2 3 4.3',
    search: 'M10.5 17a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM15.3 15.3 20 20',
    home: 'M4 10.5 12 4l8 6.5V20H4z',
    chat: 'M4 12a8 8 0 1 1 3.3 6.5L4 19.5l1-3.4A8 8 0 0 1 4 12z',
    profile: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 12.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6.5 18.2c1.2-2 3.1-3 5.5-3s4.3 1 5.5 3',
    plus: 'M12 5v14M5 12h14', check: 'M5 12.5l4.2 4.2L19 7', arrowUp: 'M12 19V5M6 11l6-6 6 6',
    camera: 'M4 8h3.5L9 5.5h6L16.5 8H20v11H4zM12 16.5a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4z',
    star: 'M12 4l2.4 5 5.4.7-4 3.8 1 5.4-4.8-2.6-4.8 2.6 1-5.4-4-3.8 5.4-.7z',
    paperclip: 'M15.5 7.5l-6.8 6.8a2 2 0 0 0 2.8 2.8l7-7a4 4 0 0 0-5.6-5.6l-7 7a6 6 0 0 0 8.5 8.5l6-6',
    share: 'M12 15V4M8 8l4-4 4 4M5 13v6h14v-6', heart: 'M12 20s-7.5-4.5-7.5-10A4.3 4.3 0 0 1 12 7a4.3 4.3 0 0 1 7.5 3c0 5.5-7.5 10-7.5 10z',
    send: 'M4 12l16-8-6 16-2.5-6.5z', mic: 'M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zM6 11.5a6 6 0 0 0 12 0M12 17.5V21',
    shirt: 'M8 4l-4 2.5 1.5 4L8 9.5V20h8V9.5l2.5 1 1.5-4L16 4c-.7 1.3-2.1 2-4 2s-3.3-.7-4-2z',
    gap: 'M4 4h4M12 4h4M20 4v4M20 12v4M20 20h-4M12 20H8M4 20v-4M4 12V8', chevron: 'M9 6l6 6-6 6', dots: 'M5 12h.01M12 12h.01M19 12h.01',
  };
  const icon = (name, size = 24, color = 'currentColor', sw = 1.7) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" style="display:block;flex:none">${(P[name] || '').split('M').filter(Boolean).map(d => `<path d="M${d}"/>`).join('')}</svg>`;

  // ---------------- surfaces ----------------
  const glass = (inner, { pad = '14px 22px', r = 999, dark = true, gap = 12, extra = '' } = {}) =>
    `<div style="display:inline-flex;align-items:center;gap:${gap}px;padding:${pad};border-radius:${r}px;` +
    `background:${dark ? 'rgba(46,46,50,.52)' : 'rgba(255,255,255,.62)'};backdrop-filter:blur(28px) saturate(1.6);-webkit-backdrop-filter:blur(28px) saturate(1.6);` +
    `border:1px solid rgba(255,255,255,${dark ? .14 : .7});box-shadow:inset 0 1px 0 rgba(255,255,255,${dark ? .22 : .9}),inset 0 -1px 0 rgba(0,0,0,.25),0 12px 40px rgba(0,0,0,${dark ? .35 : .08});${extra}">${inner}</div>`;
  const card = (inner, { w = null, h = null, r = 28, dark = true, pad = 28, extra = '' } = {}) =>
    `<div style="${w != null ? `width:${px(w)};` : ''}${h != null ? `height:${px(h)};` : ''}border-radius:${r}px;padding:${px(pad)};background:${dark ? T.card : '#fff'};border:1px solid ${dark ? T.line : 'rgba(2,1,8,.08)'};box-shadow:${dark ? '0 20px 60px rgba(0,0,0,.45)' : '0 20px 60px rgba(2,1,8,.08)'};${extra}">${inner}</div>`;
  // soft accent glow blobs (Gemini-style gradients). phase in 0..1
  const bloom = ({ x = 960, y = 540, r = 700, a = .55, hue = 'o', phase = 0 } = {}) => {
    const cols = { o: [T.oRGB, T.oDeepRGB], peach: [T.oLightRGB, T.oRGB], ember: [T.oDeepRGB, T.oDeepRGB] }[hue];
    const dx = Math.sin(phase * 6.283) * 40, dy = Math.cos(phase * 6.283) * 30;
    return `<div style="${abs(x - r + dx, y - r + dy, r * 2, r * 2)}border-radius:50%;background:radial-gradient(circle at 50% 50%,rgba(${cols[0]},${a}) 0%,rgba(${cols[1]},${a * .45}) 38%,rgba(${cols[1]},0) 70%);filter:blur(40px)"></div>`;
  };

  // ---------------- type helpers ----------------
  const txt = (s, { size = 28, w = 400, color = T.ink, ls = -0.01, lh = 1.2, extra = '' } = {}) =>
    `<span style="font-family:${T.font};font-size:${size}px;font-weight:${w};letter-spacing:${ls}em;line-height:${lh};color:${color};${extra}">${s}</span>`;
  // streaming text (AI answer): words fade/blur up in order; t 0..1 across the whole string
  function stream(s, t, { size = 30, color = '#fff', w = 400, lh = 1.35, blur = 8 } = {}) {
    const ws = s.split(' '), n = ws.length;
    return `<div style="font-family:${T.font};font-size:${size}px;font-weight:${w};line-height:${lh};color:${color}">` + ws.map((x, i) => {
      const e = C.E.outC(clamp(t * (n + 3) - i, 0, 3) / 3);
      return `<span style="opacity:${e};filter:blur(${(1 - e) * blur}px)">${x} </span>`;
    }).join('') + `</div>`;
  }
  // caret blink from frame
  const caret = (F, color = T.o, h = 34) => (Math.floor(F / 16) % 2 === 0 ? `<span style="display:inline-block;width:3px;height:${h}px;background:${color};margin-left:3px;vertical-align:-6px;border-radius:2px"></span>` : `<span style="display:inline-block;width:3px;height:${h}px;margin-left:3px"></span>`);

  // ---------------- controls ----------------
  // prompt bar. n = chars typed of text (Infinity = full). glow 0..1 animated accent border. dark app style or light editorial
  function promptBar({ w = 900, text = '', n = Infinity, placeholder = 'Ask anything', glow = 0, glowAngle = 0, dark = true, F = 0, size = 30, send = 0 } = {}) {
    const shown = C.typed(text, n), empty = shown.length === 0;
    const fg = dark ? '#fff' : T.ink, sub = dark ? 'rgba(255,255,255,.45)' : 'rgba(2,1,8,.4)';
    const ring = glow > 0.01 ? `<div style="position:absolute;inset:-3px;border-radius:999px;padding:3px;background:conic-gradient(from ${glowAngle}deg,${T.oLight},${T.o},${T.oDeep},${T.oDeep},${T.oLight},${T.oLight});-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:${glow}"></div><div style="position:absolute;inset:-24px;border-radius:999px;background:radial-gradient(60% 120% at 50% 50%,rgba(${T.oRGB},${.35 * glow}),rgba(${T.oRGB},0) 70%);filter:blur(18px);z-index:-1"></div>` : '';
    return `<div style="position:relative;width:${w}px;height:${size * 2.6}px;border-radius:999px;background:${dark ? '#1C1C1E' : '#fff'};border:1px solid ${dark ? 'rgba(255,255,255,.1)' : 'rgba(2,1,8,.1)'};box-shadow:0 10px 40px rgba(0,0,0,${dark ? .4 : .06});display:flex;align-items:center;gap:${size * .6}px;padding:0 ${size * .5}px 0 ${size * .8}px">${ring}
      <span style="color:${sub}">${icon('plus', size * .9, sub)}</span>
      <div style="flex:1;font-family:${T.font};font-size:${size}px;color:${empty ? sub : fg};white-space:nowrap;overflow:hidden">${empty ? placeholder : shown}${!empty && n < text.length + 1 ? caret(F, T.o, size * 1.1) : ''}</div>
      <span style="color:${sub}">${icon('paperclip', size * .85, sub)}</span>
      <div style="width:${size * 1.7}px;height:${size * 1.7}px;border-radius:50%;background:${send > 0.5 ? T.o : (dark ? '#2C2C2E' : '#f0f0ef')};display:flex;align-items:center;justify-content:center;transform:scale(${1 - .08 * Math.sin(Math.PI * clamp(send))})">${icon('arrowUp', size * .9, send > 0.5 ? '#fff' : sub, 2.2)}</div></div>`;
  }
  // chip. fill 0..1 animates to the accent (selected). size = font px
  function chip({ icon: ic = null, label = '', size = 26, dark = true, fill = 0, glow = 0, press = 0, active = false, extra = '' } = {}) {
    const bg = active ? '#fff' : (dark ? '#1C1C1E' : '#fff');
    const fg = active ? T.ink : (dark ? '#fff' : T.ink);
    const f = clamp(fill);
    return `<div style="position:relative;display:inline-flex;align-items:center;gap:${size * .45}px;padding:${size * .55}px ${size * .9}px;border-radius:999px;background:${bg};border:1px solid ${dark ? 'rgba(255,255,255,.12)' : 'rgba(2,1,8,.1)'};font-family:${T.font};font-size:${size}px;font-weight:400;color:${f > .5 ? '#fff' : fg};white-space:nowrap;overflow:hidden;transform:scale(${1 - .06 * press});box-shadow:${glow > 0 ? `0 0 0 2px rgba(${T.oRGB},${.6 * glow}),0 0 ${40 * glow}px rgba(${T.oRGB},${.45 * glow})` : 'none'};${extra}">
      <div style="position:absolute;inset:0;background:${T.grad};opacity:${f}"></div>
      ${ic ? `<span style="position:relative;display:flex">${icon(ic, size * 1.05, f > .5 ? '#fff' : (dark ? '#fff' : T.ink))}</span>` : ''}<span style="position:relative">${label}</span></div>`;
  }
  const chipRow = (chips, { gap = 18 } = {}) => `<div style="display:flex;gap:${gap}px;align-items:center">${chips.join('')}</div>`;
  // segmented control (glass track, sliding thumb). pos float index
  function segmented({ labels = ['Before', 'After'], pos = 0, w = 560, size = 26, dark = true } = {}) {
    const n = labels.length, cw = (w - 12) / n, h = size * 2.3;
    return `<div style="position:relative;width:${w}px;height:${h}px;border-radius:999px;background:${dark ? 'rgba(28,28,30,.85)' : 'rgba(2,1,8,.05)'};border:1px solid ${dark ? 'rgba(255,255,255,.1)' : 'rgba(2,1,8,.08)'}">
      <div style="position:absolute;top:5px;left:${6 + pos * cw}px;width:${cw}px;height:${h - 12}px;border-radius:999px;background:${dark ? 'rgba(255,255,255,.14)' : '#fff'};box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 4px 14px rgba(0,0,0,.25)"></div>
      ${labels.map((l, i) => { const on = 1 - clamp(Math.abs(pos - i)); return `<div style="${abs(6 + i * cw, 0, cw, h)}display:flex;align-items:center;justify-content:center;font-family:${T.font};font-size:${size}px;color:${dark ? `rgba(255,255,255,${.45 + .55 * on})` : `rgba(2,1,8,${.45 + .55 * on})`}">${l}</div>`; }).join('')}</div>`;
  }
  // floating glass tab bar (home, hanger, chat, search, profile). sparkle 0..1 on hanger.
  function tabBar({ active = 1, w = 640, badge = true, sparkle = 0, size = 34 } = {}) {
    const ics = ['home', 'hanger', 'chat', 'search', 'profile'], cw = w / 5;
    return `<div style="position:relative;width:${w}px;height:${size * 2.6}px">${glass('', { pad: 0, extra: `position:absolute;inset:0;border-radius:999px;` })}
      ${ics.map((ic, i) => `<div style="${abs(i * cw, 0, cw, size * 2.6)}display:flex;align-items:center;justify-content:center">
        ${i === active ? `<div style="position:absolute;width:${size * 2.1}px;height:${size * 2.1}px;border-radius:50%;background:rgba(255,255,255,.14);box-shadow:inset 0 1px 0 rgba(255,255,255,.3)"></div>` : ''}
        <span style="position:relative">${icon(ic, size, i === active ? T.o : 'rgba(255,255,255,.85)')}</span>
        ${i === 1 && badge ? `<div style="position:absolute;top:${size * .35}px;left:${cw / 2 + size * .3}px;width:${size * .62}px;height:${size * .62}px;border-radius:50%;background:${T.o};color:#fff;font:500 ${size * .4}px ${T.font};display:flex;align-items:center;justify-content:center">1</div>` : ''}
        ${i === 1 && sparkle > 0 ? `<div style="position:absolute;top:${size * .1}px;left:${cw / 2 - size * 1.1}px;opacity:${sparkle};transform:scale(${.6 + .4 * sparkle}) rotate(${sparkle * 30}deg)">${icon('sparkle', size * .8, T.oLight, 1.5)}</div>` : ''}
      </div>`).join('')}</div>`;
  }
  // 4-dot accent spinner (an AI-is-working loader)
  function spinner(F, size = 30) {
    return `<div style="position:relative;width:${size}px;height:${size}px;transform:rotate(${(F * 9) % 360}deg)">${[0, 1, 2, 3].map(i => `<div style="position:absolute;left:${size / 2 - size * .17 + Math.cos(i * Math.PI / 2) * size * .32}px;top:${size / 2 - size * .17 + Math.sin(i * Math.PI / 2) * size * .32}px;width:${size * .34}px;height:${size * .34}px;border-radius:${size * .08}px;background:${[T.o, T.oLight, T.oDeep, T.oTint][i]}"></div>`).join('')}</div>`;
  }
  // shimmer loader: spinner + label + sweeping skeleton bars. t = seconds into the shot (sweep phase)
  function shimmer({ label = 'Thinking', F = 0, bars = [.62, .48, .7], w = 760, dark = true, size = 30 } = {}) {
    const ph = (F * 2.2) % 200;
    const g = dark ? `linear-gradient(90deg,rgba(${T.oRGB},.18) 0%,rgba(${T.oLightRGB},.55) ${ph / 2}%,rgba(${T.oRGB},.18) ${Math.min(100, ph / 2 + 25)}%)` : `linear-gradient(90deg,rgba(${T.oRGB},.12) 0%,rgba(${T.oLightRGB},.45) ${ph / 2}%,rgba(${T.oRGB},.12) ${Math.min(100, ph / 2 + 25)}%)`;
    return `<div style="width:${w}px;font-family:${T.font}">
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:${size * .9}px">${spinner(F, size * 1.1)}<span style="font-size:${size}px;color:${dark ? '#fff' : T.ink}">${label}</span></div>
      ${bars.map(b => `<div style="height:${size * .62}px;width:${b * 100}%;border-radius:999px;background:${g};margin-bottom:${size * .45}px"></div>`).join('')}</div>`;
  }
  // checklist: items tick on in sequence. t 0..1
  function checklist(items, t, { size = 30, dark = true } = {}) {
    return `<div style="font-family:${T.font};font-size:${size}px;color:${dark ? '#fff' : T.ink}">` + items.map((it, i) => {
      const e = C.E.outC(clamp(t * items.length * 1.2 - i));
      return `<div style="display:flex;align-items:center;gap:${size * .55}px;margin:${size * .35}px 0;opacity:${e};transform:translateY(${(1 - e) * 16}px)"><div style="width:${size * 1.05}px;height:${size * 1.05}px;border-radius:50%;background:${e > .6 ? T.o : 'transparent'};border:2px solid ${T.o};display:flex;align-items:center;justify-content:center">${e > .6 ? icon('check', size * .7, '#fff', 2.6) : ''}</div><span>${it}</span></div>`;
    }).join('') + `</div>`;
  }

  // score ring (a score / progress that counts up)
  function scoreRing({ value = 7.8, t = 1, size = 300, dark = true } = {}) {
    const v = value * C.E.outC(clamp(t)), r = size * .42, c = 2 * Math.PI * r;
    return `<div style="position:relative;width:${size}px;height:${size}px"><svg width="${size}" height="${size}" style="position:absolute;inset:0;transform:rotate(-90deg)"><circle cx="${size / 2}" cy="${size / 2}" r="${r}" stroke="rgba(255,255,255,.12)" stroke-width="${size * .06}" fill="none"/><circle cx="${size / 2}" cy="${size / 2}" r="${r}" stroke="${T.o}" stroke-width="${size * .06}" fill="none" stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - v / 10)}"/></svg>
      <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:${T.font};color:${dark ? '#fff' : T.ink}"><span style="font-size:${size * .26}px">${v.toFixed(1)}</span><span style="font-size:${size * .07}px;opacity:.6">out of 10</span></div></div>`;
  }
  // Instagram-like feed post
  function feedPost({ user = 'Amira', img = '', caption = '', likes = 128, likeT = 0, w = 560, chipText = '', chipT = 0 } = {}) {
    const hb = clamp(likeT);
    return `<div style="width:${w}px;font-family:${T.font};color:#fff">
      <div style="display:flex;align-items:center;gap:14px;padding:14px 4px"><div style="width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,${T.oLight},${T.oDeep});padding:2px"><div style="width:100%;height:100%;border-radius:50%;background:#1C1C1E;display:flex;align-items:center;justify-content:center;font:500 20px ${T.font}">${user[0]}</div></div><span style="font-size:24px">${user}</span><span style="margin-left:auto;opacity:.6">${icon('dots', 26, '#fff')}</span></div>
      <div style="position:relative;width:${w}px;height:${w * 1.2}px;border-radius:6px;overflow:hidden;background:#111"><img src="${img}" style="width:100%;height:100%;object-fit:cover">
        ${hb > 0 && hb < 1 ? `<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(${.6 + Math.sin(Math.PI * hb) * .8});opacity:${Math.sin(Math.PI * hb)}"><svg width="160" height="160" viewBox="0 0 24 24"><path d="${P.heart}" fill="#fff"/></svg></div>` : ''}
        ${chipText ? `<div style="position:absolute;left:18px;bottom:18px;opacity:${clamp(chipT)};transform:translateY(${(1 - clamp(chipT)) * 16}px)">${glass(`${icon('users', 24, T.oLight)}<span style="font:400 22px ${T.font};color:#fff">${chipText}</span>`, { pad: '12px 18px' })}</div>` : ''}</div>
      <div style="display:flex;gap:22px;padding:16px 4px;align-items:center">${icon('heart', 32, hb > .3 ? T.o : '#fff')}${icon('chat', 30, '#fff')}${icon('send', 30, '#fff')}</div>
      <div style="font-size:22px;padding:0 4px">${Math.round(likes + hb * 1)} likes · <span style="opacity:.7">${caption}</span></div></div>`;
  }
  // bottom sheet that springs up. t 0..1 (use CORE.sp)
  function sheet(inner, { t = 1, w = 760, h = 560, dark = true } = {}) {
    return `<div style="width:${w}px;height:${h}px;border-radius:36px 36px 0 0;background:${dark ? '#1C1C1E' : '#fff'};transform:translateY(${(1 - t) * (h + 40)}px);box-shadow:0 -20px 80px rgba(0,0,0,.4);padding:22px 36px;font-family:${T.font}">
      <div style="width:64px;height:7px;border-radius:9px;background:${dark ? 'rgba(255,255,255,.25)' : 'rgba(2,1,8,.15)'};margin:0 auto 24px"></div>${inner}</div>`;
  }
  // AR tag pinned to a point: ring at (x,y), leader line to a glass pill. t 0..1
  function tag({ x, y, text, t = 1, side = 1, len = 160, dark = true, size = 24 } = {}) {
    const e = clamp(t), ring = C.E.outC(clamp(e * 2)), line = C.E.ioC(clamp(e * 2 - .5)), pill = C.E.outC(clamp(e * 2 - 1));
    const ex = x + side * len * line, ey = y - len * .55 * line;
    return `<div style="${abs(x - 26, y - 26, 52, 52)}border-radius:50%;border:3px solid ${T.o};transform:scale(${ring});box-shadow:0 0 30px rgba(${T.oRGB},.6)"></div>
      <div style="${abs(x - 7, y - 7, 14, 14)}border-radius:50%;background:${T.o};opacity:${ring}"></div>
      <svg style="${abs(0, 0, C.W, C.H)}overflow:visible"><line x1="${x}" y1="${y}" x2="${ex}" y2="${ey}" stroke="${T.o}" stroke-width="2.5"/></svg>
      <div style="${abs(side > 0 ? ex + 10 : ex - 10, ey - 30)}transform:translate(${side > 0 ? 0 : -100}%,0) scale(${.9 + .1 * pill});transform-origin:${side > 0 ? 'left' : 'right'} center;opacity:${pill}">${glass(`${icon('tag', size, T.oLight)}<span style="font:400 ${size}px ${T.font};color:${dark ? '#fff' : T.ink};white-space:nowrap">${text}</span>`, { pad: '12px 20px', dark })}</div>`;
  }
  // voice wave (dark screen, layered accent gradients)
  function voiceWave({ F = 0, w = 600, h = 400, level = 1 } = {}) {
    const b = k => .5 + .5 * Math.sin(F * .21 + k * 1.7) * Math.sin(F * .07 + k);
    return `<div style="position:relative;width:${w}px;height:${h}px;overflow:hidden">${[0, 1, 2].map(k => `<div style="position:absolute;left:${-w * .2}px;right:${-w * .2}px;bottom:${-h * .55 + b(k) * h * .25 * level}px;height:${h}px;border-radius:50%;background:radial-gradient(50% 50% at 50% 50%,${['rgba(${T.oLightRGB},.85)', 'rgba(${T.oRGB},.75)', 'rgba(${T.oDeepRGB},.8)'][k]},rgba(0,0,0,0));filter:blur(${18 + k * 8}px)"></div>`).join('')}</div>`;
  }
  // iPhone body (thin bezel, dynamic island, status bar). inner = screen HTML (w x h px)
  function phone(inner, { w = 520, h = 1100, dark = true, glare = .0, r = 76 } = {}) {
    return `<div style="position:relative;width:${w}px;height:${h}px;border-radius:${r}px;background:#0a0a0a;padding:14px;box-shadow:0 0 0 2px #2a2a2c,0 40px 120px rgba(0,0,0,.55)">
      <div style="position:relative;width:100%;height:100%;border-radius:${r - 14}px;overflow:hidden;background:${dark ? '#000' : '#fff'}">${inner}
        <div style="${abs(0, 0, '100%', 64)}display:flex;align-items:center;justify-content:space-between;padding:0 44px;font:500 22px ${T.font};color:${dark ? '#fff' : T.ink};z-index:5"><span>9:41</span><span style="display:flex;gap:8px;align-items:center"><span style="width:28px;height:13px;border-radius:4px;border:2px solid currentColor;display:inline-block"></span></span></div>
        <div style="${abs('calc(50% - 64px)', 14, 128, 38)}border-radius:20px;background:#000;z-index:6"></div>
        ${glare > 0 ? `<div style="position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,255,255,${glare * .18}) 45%,rgba(255,255,255,0) 60%);z-index:7"></div>` : ''}</div></div>`;
  }
  // corner-pin an HTML panel onto a quad (device-on-surface). quad = [[x,y]x4] TL,TR,BR,BL in stage px, panel w x h
  function cornerPin(inner, quad, w, h) {
    const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = quad;
    // homography from unit square to quad (Heckbert), then scale from panel size
    const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2, sx = x0 - x1 + x2 - x3, sy = y0 - y1 + y2 - y3;
    const den = dx1 * dy2 - dx2 * dy1, g = (sx * dy2 - dx2 * sy) / den, hh = (dx1 * sy - sx * dy1) / den;
    const a = x1 - x0 + g * x1, b = x3 - x0 + hh * x3, c = x0, d = y1 - y0 + g * y1, e = y3 - y0 + hh * y3, f = y0;
    const m = [a / w, d / w, 0, g / w, b / h, e / h, 0, hh / h, 0, 0, 1, 0, c, f, 0, 1];
    return `<div style="position:absolute;left:0;top:0;width:${w}px;height:${h}px;transform-origin:0 0;transform:matrix3d(${m.map(v => v.toFixed(8)).join(',')})">${inner}</div>`;
  }
  window.UI = { icon, glass, card, bloom, txt, stream, caret, promptBar, chip, chipRow, segmented, tabBar, spinner, shimmer, checklist, scoreRing, feedPost, sheet, tag, voiceWave, phone, cornerPin, abs };
})();

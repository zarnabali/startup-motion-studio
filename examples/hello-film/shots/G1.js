(function () {
  // hello-film: a 6 s demo of the engine (springs, word rise, typing, chip stream, carrier camera, end card).
  // Every value is a pure function of F. Read it as a template for your own shots.
  const C = CORE, T = C.T, U = UI, sp = C.sp, clamp = C.clamp;
  const bg = `<div style="position:absolute;inset:0;background:${T.black}"></div>`;

  // S1 0-60: headline rises word by word; accent word in the brand gradient; a slow glow drifts behind
  SHOT({ id: 'S1_hook', f0: 0, f1: 60, render: (lf, F) => {
    const cam = C.cam(F, [[0, 1, 0, 0], [60, 1.06, 0, -10]]);
    return bg + C.camera(`${U.bloom({ x: 960, y: 560, r: 640, a: .2 + .15 * clamp(lf / 20), phase: F / 180 })}
      <div style="position:absolute;left:0;right:0;top:430px;text-align:center;font:500 110px ${T.font};color:#fff;letter-spacing:-.03em">
        ${C.rise('Ship your launch film.', F, -3, { accent: [2] })}</div>`, cam);
  } });

  // S2 60-130: carrier = the camera keeps moving up while the prompt bar types; chips spring in staggered
  const chips = ['Brief', 'Script', 'Style frames', 'Animatic', 'Final'];
  SHOT({ id: 'S2_prompt', f0: 60, f1: 130, render: (lf, F) => {
    const y = C.spv(F, 60, 120, 0, 'box'), text = 'make a 45 s launch film for my app';
    const n = clamp((F - 66) / 34) * text.length;
    const row = chips.map((l, i) => { const e = clamp(sp(F, 96 + i * 3, 'ui'), 0, 1.03);
      return `<div style="transform:translateY(${(1 - e) * 40}px) scale(${.9 + .1 * e});opacity:${clamp(e * 1.4)}">${U.chip({ label: l, fill: clamp((F - 118 + (4 - i) * 2) / 6) * (i === 4 ? 1 : 0) })}</div>`; }).join('');
    return bg + `${U.bloom({ x: 960, y: 480, r: 700, a: .3, phase: F / 180 })}
      <div style="position:absolute;left:0;right:0;top:${380 + y}px;display:flex;flex-direction:column;align-items:center;gap:44px">
        ${U.promptBar({ w: 1040, text, n, glow: clamp((F - 64) / 12), F })}
        <div style="display:flex;gap:18px">${row}</div></div>`;
  } });

  // S3 130-180: the selected chip's accent becomes the end card background (carrier = colour + scale)
  SHOT({ id: 'S3_end', f0: 130, f1: 180, render: (lf, F) => {
    const e = clamp(sp(F, 130, 'heavy'), 0, 1.02), r = 60 + e * 1400;
    return bg + `<div style="position:absolute;left:${960 - r}px;top:${540 - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;background:${T.grad}"></div>
      <div style="position:absolute;left:0;right:0;top:440px;text-align:center;font:500 96px ${T.font};color:#fff;letter-spacing:-.03em">${C.rise('Made in code.', F, 138)}</div>
      <div style="position:absolute;left:0;right:0;top:580px;text-align:center;font:400 40px ${T.font};color:rgba(255,255,255,.8);opacity:${clamp((F - 150) / 8)}">Startup Motion Studio</div>`;
  } });
})();

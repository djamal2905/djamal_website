/* Lecteur « reel » : scènes animées, lecture auto à l'écran, tap gauche/droite, flèches, pause */
(function () {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.reel').forEach((reel) => {
    const stage = reel.querySelector('.reel-stage');
    const sc = [...reel.querySelectorAll('.rs')];
    const DUR = +(reel.dataset.dur || 5200);
    const bars = reel.querySelector('.reel-bars');
    bars.innerHTML = sc.map(() => '<i><b></b></i>').join('');
    const bi = [...bars.children];
    const playB = reel.querySelector('[data-r="play"]');
    const cnt = reel.querySelector('.cnt');
    let k = 0, timer = null, playing = false;

    function count(el) {
      const end = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length;
      const pre = el.dataset.pre || '', suf = el.dataset.suf || '';
      if (reduce) { el.textContent = pre + end.toFixed(dec) + suf; return; }
      const t0 = performance.now(), T = 1400;
      (function f(t) {
        const p = Math.min(1, (t - t0) / T), e = 1 - Math.pow(1 - p, 3);
        el.textContent = pre + (end * e).toFixed(dec) + suf;
        if (p < 1) requestAnimationFrame(f);
      })(t0);
    }
    function show(n) {
      k = (n + sc.length) % sc.length;
      sc.forEach((s, i) => { s.classList.remove('on'); s.setAttribute('aria-hidden', String(i !== k)); });
      void sc[k].offsetWidth; // relance les animations CSS
      sc[k].classList.add('on');
      sc[k].querySelectorAll('[data-count]').forEach(count);
      bi.forEach((b, i) => {
        b.classList.toggle('done', i < k);
        const fill = b.firstChild;
        fill.style.transition = 'none'; fill.style.transform = i < k ? 'scaleX(1)' : 'scaleX(0)';
      });
      cnt.textContent = (k + 1) + ' / ' + sc.length;
      if (playing) run();
    }
    function run() {
      clearTimeout(timer);
      const fill = bi[k].firstChild;
      void fill.offsetWidth;
      const D = () => +(sc[k].dataset.dur || DUR);
      if (!reduce) { fill.style.transition = 'transform ' + D() + 'ms linear'; fill.style.transform = 'scaleX(1)'; }
      timer = setTimeout(() => { if (k < sc.length - 1) show(k + 1); else stop(true); }, D());
    }
    function play() { if (k === sc.length - 1 && !playing && bi[k].classList.contains('done')) { bi.forEach(b => b.classList.remove('done')); show(0); } playing = true; playB.textContent = 'Pause'; playB.setAttribute('aria-pressed', 'true'); run(); }
    function stop(end) {
      clearTimeout(timer); playing = false; playB.setAttribute('aria-pressed', 'false');
      const fill = bi[k].firstChild; fill.style.transition = 'none';
      if (end) { bi[k].classList.add('done'); fill.style.transform = 'scaleX(1)'; playB.textContent = 'Replay'; }
      else { fill.style.transform = 'scaleX(0)'; playB.textContent = 'Play'; }
    }
    playB.onclick = () => (playing ? stop(false) : play());
    reel.querySelector('[data-r="prev"]').onclick = () => show(k - 1);
    reel.querySelector('[data-r="next"]').onclick = () => show(k + 1);
    reel.querySelector('.reel-tap.l').onclick = () => show(k - 1);
    reel.querySelector('.reel-tap.r').onclick = () => show(k + 1);
    stage.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); show(k + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); show(k - 1); }
      else if (e.key === ' ') { e.preventDefault(); playing ? stop(false) : play(); }
    });
    show(0);
    if (!reduce && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver((es) => {
        es.forEach((en) => {
          if (en.isIntersecting && !playing && !reel.dataset.started) { reel.dataset.started = '1'; show(0); play(); }
          else if (!en.isIntersecting && playing) stop(false);
        });
      }, { threshold: 0.55 });
      io.observe(stage);
    }
  });
})();

/* Musique d'ambiance douce, générée en direct (Web Audio), lancée seulement au clic sur ♪ Music */
(function () {
  const btns = [...document.querySelectorAll('[data-r="music"]')];
  if (!btns.length) return;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) { btns.forEach(b => b.hidden = true); return; }
  let ctx = null, master = null, timer = null, on = false, step = 0;
  // Cmaj7 - Am7 - Fmaj7 - G6 (fréquences en Hz)
  const CHORDS = [[130.81, 164.81, 196.0, 246.94], [110.0, 130.81, 164.81, 196.0], [87.31, 130.81, 174.61, 220.0], [98.0, 146.83, 196.0, 246.94]];
  const BAR = 6;
  function pad(freqs, t) {
    freqs.forEach((f, i) => {
      [1, 2].forEach((mult) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = mult === 1 ? 'sine' : 'triangle';
        o.frequency.value = f * mult; o.detune.value = (i - 1.5) * 4;
        const peak = mult === 1 ? 0.05 : 0.012;
        g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(peak, t + 2); g.gain.linearRampToValueAtTime(peak * .8, t + BAR - 1.5); g.gain.linearRampToValueAtTime(0, t + BAR + 1.5);
        o.connect(g).connect(master); o.start(t); o.stop(t + BAR + 1.6);
      });
    });
    // arpège léger
    const notes = freqs.concat([freqs[1] * 2, freqs[2] * 2]);
    for (let k = 0; k < 8; k++) {
      const o = ctx.createOscillator(), g = ctx.createGain(), tt = t + k * 0.75;
      o.type = 'sine'; o.frequency.value = notes[(k * 3 + step) % notes.length] * 2;
      g.gain.setValueAtTime(0, tt); g.gain.linearRampToValueAtTime(0.025, tt + 0.03); g.gain.exponentialRampToValueAtTime(0.0005, tt + 1.4);
      o.connect(g).connect(master); o.start(tt); o.stop(tt + 1.5);
    }
  }
  function schedule() { const t = ctx.currentTime + 0.1; pad(CHORDS[step % 4], t); step++; timer = setTimeout(schedule, BAR * 1000); }
  function setUI() { btns.forEach(b => { b.setAttribute('aria-pressed', String(on)); b.textContent = on ? '♪ Music on' : '♪ Music'; }); }
  function start() {
    if (!ctx) {
      ctx = new AC(); master = ctx.createGain(); master.gain.value = 0;
      const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1800;
      master.connect(lp).connect(ctx.destination);
    }
    ctx.resume(); master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.linearRampToValueAtTime(0.9, ctx.currentTime + 2);
    on = true; setUI(); if (!timer) schedule();
  }
  function stop() {
    on = false; setUI(); clearTimeout(timer); timer = null;
    if (ctx) { master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setValueAtTime(master.gain.value, ctx.currentTime); master.gain.linearRampToValueAtTime(0, ctx.currentTime + 1.2); }
  }
  btns.forEach(b => b.addEventListener('click', () => (on ? stop() : start())));
  document.addEventListener('visibilitychange', () => { if (document.hidden && on) stop(); });
})();

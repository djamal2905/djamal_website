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
      if (!reduce) { fill.style.transition = 'transform ' + DUR + 'ms linear'; fill.style.transform = 'scaleX(1)'; }
      timer = setTimeout(() => { if (k < sc.length - 1) show(k + 1); else stop(true); }, DUR);
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

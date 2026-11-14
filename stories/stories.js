/* Récits interactifs : révélations au clic, chapitres au défilement, compteurs, lecture rapide.
   Amélioration progressive : sans JavaScript, tout le contenu reste visible. */
(function () {
  const doc = document.documentElement;
  doc.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let revealAll = false;
  const reveals = [];

  /* ---------- barre de lecture ---------- */
  const bar = document.createElement('div');
  bar.className = 'readbar';
  bar.setAttribute('aria-hidden', 'true');
  document.body.prepend(bar);
  const onScroll = () => {
    const h = doc.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- un bloc révélable ---------- */
  let uid = 0;
  function makeReveal(content, label, anchor) {
    const id = 'rv-' + (++uid);
    content.id = id;
    content.classList.add('rv-body');
    content.hidden = true;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rv-btn';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', id);
    btn.innerHTML = '<span>' + label + '</span><span class="rv-arrow" aria-hidden="true">→</span>';
    anchor.before(btn);
    const open = (focus) => {
      content.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
      btn.classList.add('rv-done');
      btn.hidden = true;
      content.classList.add('rv-in');
      content.querySelectorAll('[data-count]:not(.reel [data-count])').forEach(countUp);
      if (focus) { content.setAttribute('tabindex', '-1'); content.focus({ preventScroll: true }); }
    };
    btn.addEventListener('click', () => open(true));
    reveals.push(open);
  }

  /* 1. Les choix : la question et la tension d'abord, la décision au clic */
  document.querySelectorAll('.dp dl').forEach(dl => {
    const dts = [...dl.querySelectorAll('dt')];
    const dt = dts.find(d => /^(choice|outcome)$/i.test(d.textContent.trim()));
    if (!dt || dts.length < 2) return;                       // une seule ligne : rien à cacher
    const wrap = document.createElement('div');
    wrap.className = 'rv-pair';
    const dd = dt.nextElementSibling;
    dt.before(wrap);
    wrap.append(dt, dd);
    makeReveal(wrap, /outcome/i.test(dt.textContent) ? 'What happened?' : 'What was decided?', wrap);
  });

  /* 2. Le résultat : dévoilé au clic */
  document.querySelectorAll('.ch').forEach(ch => {
    const lab = ch.querySelector('.n');
    if (!lab || !/outcome/i.test(lab.textContent)) return;
    const body = lab.nextElementSibling;
    if (!body) return;
    const inner = document.createElement('div');
    while (body.firstChild) inner.append(body.firstChild);
    body.append(inner);
    makeReveal(inner, 'Reveal the outcome', inner);
  });

  /* 3. Compteurs : chiffres qui défilent quand ils apparaissent */
  function countUp(el) {
    if (el.dataset.done || reduce) { el.textContent = el.dataset.final; return; }
    el.dataset.done = '1';
    const target = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length;
    const t0 = performance.now(), dur = 900;
    const step = (now) => {
      const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = el.dataset.prefix + (target * e).toFixed(dec) + el.dataset.suffix;
      if (p < 1) requestAnimationFrame(step); else el.textContent = el.dataset.final;
    };
    requestAnimationFrame(step);
  }
  document.querySelectorAll('.nums b, .headline .num').forEach(el => {
    const txt = el.textContent.trim();
    const m = txt.match(/^([^\d]*)(\d+(?:\.\d+)?)(.*)$/);
    if (!m || /\d/.test(m[3])) return;                       // « 1946 to 2023 » : pas de compteur
    el.dataset.final = txt; el.dataset.prefix = m[1]; el.dataset.count = m[2]; el.dataset.suffix = m[3];
  });

  /* 4. Chapitres et chiffres qui apparaissent au défilement */
  const targets = document.querySelectorAll('.ch, .nums, figure');
  if ('IntersectionObserver' in window && !reduce) {
    targets.forEach(el => el.classList.add('fx'));
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('fx-in');
      en.target.querySelectorAll(':scope [data-count]:not(.reel [data-count])').forEach(c => { if (!c.closest('[hidden]')) countUp(c); });
      if (en.target.matches('.nums')) en.target.querySelectorAll('[data-count]:not(.reel [data-count])').forEach(countUp);
      io.unobserve(en.target);
    }), { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    targets.forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('[data-count]:not(.reel [data-count])').forEach(el => { el.textContent = el.dataset.final; });
  }

  /* 5. Lecture rapide : tout afficher d'un coup */
  if (reveals.length) {
    const quick = document.createElement('button');
    quick.type = 'button';
    quick.className = 'quick';
    quick.textContent = 'Show everything';
    quick.setAttribute('aria-label', 'Show every decision and outcome at once');
    quick.addEventListener('click', () => {
      revealAll = true;
      reveals.forEach(open => open(false));
      document.querySelectorAll('.fx').forEach(el => el.classList.add('fx-in'));
      quick.remove();
    });
    document.body.append(quick);
  }
})();

/* Figures empilées : un onglet par graphique, pour que chaque figure tienne sur un écran */
document.querySelectorAll('.viz-stack[data-tabs]').forEach((st, k) => {
  const panes = [...st.children].filter(e => e.tagName.toLowerCase() === 'svg');
  if (panes.length < 2) return;
  const names = st.dataset.tabs.split('|');
  const bar = document.createElement('div');
  bar.className = 'vt-bar';
  bar.setAttribute('role', 'tablist');
  const tabs = panes.map((p, i) => {
    p.id = p.id || 'vt' + k + '-' + i;
    p.setAttribute('role', 'tabpanel');
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-controls', p.id);
    b.textContent = names[i] || 'View ' + (i + 1);
    b.addEventListener('click', () => show(i));
    b.addEventListener('keydown', e => {
      const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (d) { e.preventDefault(); const j = (i + d + panes.length) % panes.length; show(j); tabs[j].focus(); }
    });
    bar.append(b);
    return b;
  });
  function show(i) {
    panes.forEach((p, j) => p.toggleAttribute('hidden', j !== i));
    tabs.forEach((b, j) => { b.setAttribute('aria-selected', String(j === i)); b.tabIndex = j === i ? 0 : -1; });
  }
  st.before(bar);
  show(0);
});

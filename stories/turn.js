/* Effet de page tournée entre les récits de projets (respecte le mouvement réduit). */
(function () {
  const w = document.querySelector('.wrap');
  if (!w) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let dir = null;
  try { dir = sessionStorage.getItem('turn'); sessionStorage.removeItem('turn'); } catch (e) {}
  if (dir && !reduce) { w.classList.add('pg-in'); if (dir === 'back') w.classList.add('back'); }
  addEventListener('pageshow', ev => { if (ev.persisted) w.classList.remove('pg-out', 'pg-in', 'back'); });
  document.querySelectorAll('.next a').forEach(a => a.addEventListener('click', e => {
    if (reduce || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    const back = a.textContent.trim().charAt(0) === '←';
    try { sessionStorage.setItem('turn', back ? 'back' : 'fwd'); } catch (err) {}
    w.classList.remove('pg-in'); w.classList.add('pg-out'); w.classList.toggle('back', back);
    setTimeout(() => { location.href = a.href; }, 360);
  }));
})();

/* Bible Answer — the website. Cosmetic only: reveal on scroll, parallax, the starfield and the timing of
   the demo. The pages are complete without it, and it makes no requests of any kind. */
(() => {
  'use strict';

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = id => document.getElementById(id);

  function stars() {
    const box = $('stars');
    if (!box) return;
    let s = 20260928;   // fixed seed: the same sky on every visit, no layout jump
    const rnd = () => { s |= 0; s = (s + 0x6D2B79F5) | 0; let x = Math.imul(s ^ (s >>> 15), 1 | s); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
    for (let i = 0; i < 44; i++) {
      const d = document.createElement('i');
      const size = 1 + rnd() * 1.6;
      d.style.cssText = `left:${(rnd() * 100).toFixed(1)}%;top:${(rnd() * 78).toFixed(1)}%;width:${size.toFixed(1)}px;height:${size.toFixed(1)}px;--t:${(3 + rnd() * 4).toFixed(1)}s;--dl:${(rnd() * -6).toFixed(1)}s`;
      box.appendChild(d);
    }
  }

  /** Adds `.in` (or `.play`) to elements as they come into view, once. */
  function onView(selector, cls, options) {
    const items = document.querySelectorAll(selector);
    if (!('IntersectionObserver' in window) || reduced) { items.forEach(n => n.classList.add(cls)); return; }
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add(cls); io.unobserve(en.target); } });
    }, options);
    items.forEach(n => io.observe(n));
  }

  function scrollEffects() {
    if (reduced) return;
    const root = document.documentElement;
    const hero = document.querySelector('.hero');
    const floaters = Array.from(document.querySelectorAll('[data-parallax]'));
    let queued = false;
    const frame = () => {
      queued = false;
      const y = window.scrollY;
      root.style.setProperty('--scroll', y.toFixed(1));
      root.style.setProperty('--hp', Math.min(1, Math.max(0, y / (hero.offsetHeight * 0.7))).toFixed(3));
      const vh = window.innerHeight;
      floaters.forEach(f => {
        const r = f.getBoundingClientRect();
        if (r.bottom < -240 || r.top > vh + 240) return;
        f.style.setProperty('--py', ((r.top + r.height / 2 - vh / 2) * -0.06).toFixed(1));
      });
    };
    const onScroll = () => { if (!queued) { queued = true; requestAnimationFrame(frame); } };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    frame();
  }

  stars();
  onView('.reveal', 'in', { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  onView('[data-demo]', 'is-playing', { threshold: 0.3 });
  scrollEffects();
})();

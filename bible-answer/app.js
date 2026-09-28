/* Bible Answer — the website. Talks to the same server as the app (POST /ask) and nothing else:
   no analytics, no third-party requests. Everything shown from the server is set with textContent. */
(() => {
  'use strict';

  const I18N = window.BA_I18N;
  const LANGS = Object.keys(I18N);
  const FEATURED = [0, 13, 5, 1, 6, 3];      // anxious, lonely, afraid, can't cope, no strength, lost — as in the app
  const POSITIVE = [14, 15, 16, 17, 18];     // "with a thankful heart"
  const ICONS = ['anxious', 'overwhelmed', 'selfworth', 'lost', 'courage', 'future', 'exhausted', 'forgiveness',
                 'morning', 'anger', 'guilt', 'trust', 'money', 'lonely', 'gratitude', 'joy', 'praise', 'goodnews', 'peace'];

  const CONFIG = {
    api: 'https://bible-answer-server-production.up.railway.app',
    appStoreUrl: '',             // set when the App Store page exists; the buttons stay hidden until then
    timeoutMs: 60000,
  };
  // Pointing the page at a local server is for testing only, and only from a local page.
  if (['localhost', '127.0.0.1'].includes(location.hostname)) {
    const o = new URLSearchParams(location.search).get('api');
    if (o && /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o)) CONFIG.api = o;
  }

  const $ = id => document.getElementById(id);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode: fine, it just is not remembered */ } },
  };

  let lang = 'en';
  let busy = false;
  let pending = null;
  let lastQuery = '';

  const t = key => I18N[lang][key];

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function icon(name, cls = 'ico') {
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', cls);
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS(NS, 'use');
    use.setAttribute('href', 'assets/feelings.svg#feel-' + name);
    svg.appendChild(use);
    return svg;
  }

  /* ---------- language ---------- */

  function detectLang() {
    const asked = new URLSearchParams(location.search).get('lang');
    if (asked && LANGS.includes(asked)) return asked;
    const saved = store.get('ba-lang');
    if (saved && LANGS.includes(saved)) return saved;
    for (const l of navigator.languages || [navigator.language || 'en']) {
      const p = String(l).toLowerCase().split('-')[0];
      const code = p === 'tl' ? 'fil' : p;
      if (LANGS.includes(code)) return code;
    }
    return 'en';
  }

  function setLang(next, persist) {
    lang = next;
    if (persist) store.set('ba-lang', lang);
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : lang;

    document.querySelectorAll('[data-i18n]').forEach(n => { n.textContent = t(n.dataset.i18n); });
    document.title = 'Bible Answer — ' + t('tagline');
    const desc = document.querySelector('meta[name="description"]');
    if (desc) desc.setAttribute('content', t('subtitle'));

    $('lang').value = lang;
    $('qLabel').textContent = t('placeholder');
    $('q').placeholder = t('placeholder');
    $('send').setAttribute('aria-label', t('send'));
    $('goodDays').textContent = t('goodDays');
    $('loaderText').textContent = t('loading');
    $('consentOk').textContent = t('cont');
    $('consentBack').textContent = t('back');
    $('fPrivacy').href = 'privacy#' + lang;
    $('fTerms').href = 'terms#' + lang;
    renderMore();
    buildFeelings();
    buildConsent();
    buildLangLinks();

    const names = LANGS.map(l => I18N[l].name).join(' · ');
    $('heroLangs').textContent = names;

    const hasStore = Boolean(CONFIG.appStoreUrl);
    ['store', 'storeNav'].forEach(id => {
      const a = $(id);
      a.hidden = !hasStore;
      if (hasStore) a.href = CONFIG.appStoreUrl;
    });
    $('askLink').className = hasStore ? 'link' : 'btn btn--gold';
  }

  function buildLangLinks() {
    const box = $('fLangs');
    box.textContent = '';
    LANGS.forEach((l, i) => {
      if (i) box.appendChild(el('span', 'dot', '·'));
      const a = el('a', null, I18N[l].name);
      a.href = '?lang=' + l;
      a.lang = l === 'pt' ? 'pt-BR' : l;
      if (l === lang) a.setAttribute('aria-current', 'true');
      a.addEventListener('click', e => { e.preventDefault(); setLang(l, true); });
      box.appendChild(a);
    });
  }

  /* ---------- feelings ---------- */

  function buildFeelings() {
    const feelings = I18N[lang].feelings;
    const big = $('feelings'), warm = $('pills'), rest = $('restPills');
    big.textContent = warm.textContent = rest.textContent = '';

    FEATURED.forEach(i => {
      const b = el('button', 'chip-lg');
      b.type = 'button';
      b.dataset.i = i;
      const disc = el('span', 'disc');
      disc.appendChild(icon(ICONS[i]));
      b.append(disc, el('span', null, feelings[i].label));
      big.appendChild(b);
    });
    POSITIVE.forEach(i => {
      const b = el('button', 'pill pill--warm');
      b.type = 'button';
      b.dataset.i = i;
      b.append(icon(ICONS[i]), el('span', null, feelings[i].label));
      warm.appendChild(b);
    });
    feelings.forEach((f, i) => {
      if (FEATURED.includes(i) || POSITIVE.includes(i)) return;
      const b = el('button', 'pill');
      b.type = 'button';
      b.dataset.i = i;
      b.append(icon(ICONS[i]), el('span', null, f.label));
      rest.appendChild(b);
    });
  }

  function renderMore() {
    const open = !$('rest').hidden;
    $('more').textContent = open ? t('fewer') : t('more');
    $('more').setAttribute('aria-expanded', String(open));
  }

  /* ---------- consent ---------- */

  const hasConsent = () => store.get('ba-consent') === '1';

  function buildConsent() {
    const p = $('consentText');
    p.textContent = '';
    const parts = t('consent').replace('{start}', t('cont')).split(/\[\[|\]\]/);
    p.appendChild(document.createTextNode(parts[0]));
    if (parts.length > 1) {
      const a = el('a', null, parts[1]);
      a.href = 'privacy#' + lang;
      a.target = '_blank';
      a.rel = 'noopener';
      p.appendChild(a);
      p.appendChild(document.createTextNode(parts[2] || ''));
    }
  }

  const dlg = $('consent');
  function openConsent() {
    if (typeof dlg.showModal === 'function') dlg.showModal();
    else dlg.setAttribute('open', '');   // very old browsers: the same card, not modal
  }
  $('consentOk').addEventListener('click', () => {
    store.set('ba-consent', '1');
    dlg.close();
    const q = pending;
    pending = null;
    if (q) run(q);
  });
  $('consentBack').addEventListener('click', () => dlg.close());
  dlg.addEventListener('close', () => { pending = null; });
  dlg.addEventListener('click', e => {
    const r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
  });

  /* ---------- the question ---------- */

  function clientId() {
    let id = store.get('ba-client');
    if (!id) {
      const rnd = (crypto.randomUUID && crypto.randomUUID()) ||
        Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join('');
      id = 'web-' + rnd;
      store.set('ba-client', id);
    }
    return id;
  }

  const str = v => (typeof v === 'string' ? v.trim() : '');

  async function ask(query) {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), CONFIG.timeoutMs);
    let res;
    try {
      res = await fetch(CONFIG.api + '/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json', 'x-client-id': clientId() },
        body: JSON.stringify({ query, lang }),
        signal: ctl.signal,
      });
    } catch (e) {
      throw { kind: e && e.name === 'AbortError' ? 'timeout' : 'network' };
    } finally {
      clearTimeout(timer);
    }
    if (res.status === 429) {
      let code = '';
      try { code = (await res.json()).error.code; } catch { /* no body */ }
      throw { kind: code === 'daily_limit' ? 'daily' : 'rate' };
    }
    if (res.status === 408 || res.status === 504) throw { kind: 'timeout' };
    if (!res.ok) throw { kind: 'server' };
    let data;
    try { data = await res.json(); } catch { throw { kind: 'generic' }; }
    data = (data && (data.data || data.result)) || data || {};   // the app accepts the same wrappers
    const r = {
      reference: str(data.reference), verseText: str(data.verseText), context: str(data.context),
      application: str(data.application), prayer: str(data.prayer), translation: str(data.translation),
    };
    if (!r.reference || !r.verseText) throw { kind: 'generic' };
    return r;
  }

  const ERRORS = { network: 'errNoInternet', timeout: 'errTimeout', rate: 'errRate', daily: 'limit', server: 'errServer', generic: 'errGeneric' };

  function showNotice(text) {
    const n = $('notice');
    n.textContent = text || '';
    n.hidden = !text;
  }

  function requestAsk(raw) {
    const query = str(raw);
    if (!query || busy) return;
    if (!hasConsent()) { pending = query; openConsent(); return; }
    run(query);
  }

  async function run(query) {
    busy = true;
    lastQuery = query;
    showNotice('');
    $('compose').hidden = true;
    $('loader').hidden = false;
    try {
      const r = await ask(query);
      renderAnswer(query, r);
      $('loader').hidden = true;
      $('answer').hidden = false;
      $('answer').focus({ preventScroll: true });
      $('answer').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    } catch (e) {
      $('loader').hidden = true;
      $('compose').hidden = false;
      $('q').value = query;
      autosize();
      showNotice(t(ERRORS[(e && e.kind) || 'generic']));
    } finally {
      busy = false;
    }
  }

  function renderAnswer(query, r) {
    const root = $('answer');
    root.textContent = '';
    let n = 0;
    const part = node => { node.classList.add('part'); node.style.setProperty('--i', n++); return node; };

    const back = el('button', 'answer__back', t('back'));
    back.type = 'button';
    back.addEventListener('click', reset);

    const left = el('div', 'verse-page');
    left.append(
      part(el('div', 'q', query)),
      part(el('p', 'ref', r.reference)),
      part(el('hr', 'hair')),
      part(el('blockquote', 'verse', r.verseText)),
      part(el('hr', 'hair')),
    );
    if (r.translation) left.appendChild(part(el('div', 'credit', r.translation)));

    const right = el('div', 'reading');
    const block = (label, text, quiet) => {
      const b = el('div', 'block');
      const head = el('div', 'head');
      head.append(el('h3', 'label', label), el('i'));
      b.append(head, el('p', 'body' + (quiet ? ' body--quiet' : ''), text));
      right.appendChild(part(b));
    };
    if (r.application) block(t('forYou'), r.application, false);
    if (r.prayer) {
      const p = el('div', 'prayer');
      const head = el('div', 'head');
      head.append(el('i'), el('h3', 'label', t('prayer')), el('i'));
      p.append(head, el('p', null, r.prayer));
      right.appendChild(part(p));
    }
    if (r.context) block(t('context'), r.context, true);

    const diamond = el('div', 'diamond');
    diamond.append(el('i'), el('b'), el('i'));
    right.appendChild(part(diamond));

    const again = el('div', 'again');
    const btn = el('button', 'btn btn--ghost', t('askAgain'));
    btn.type = 'button';
    btn.addEventListener('click', reset);
    again.appendChild(btn);
    right.appendChild(part(again));

    const fine = el('p', 'fine', t('fine') + ' ');
    const terms = el('a', null, t('terms'));
    terms.href = 'terms#' + lang;
    fine.appendChild(terms);
    right.appendChild(part(fine));

    const spread = el('div', 'spread');
    spread.append(left, el('div', 'gutter'), right);
    root.append(back, spread);
  }

  function reset() {
    $('answer').hidden = true;
    $('answer').textContent = '';
    $('compose').hidden = false;
    $('q').value = '';
    autosize();
    $('ask').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    $('q').focus({ preventScroll: true });
  }

  /* ---------- composer ---------- */

  const ta = $('q');
  function autosize() {
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 180) + 'px';
    $('send').disabled = !ta.value.trim();
  }
  ta.addEventListener('input', autosize);
  ta.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); $('form').requestSubmit(); }
  });
  $('form').addEventListener('submit', e => { e.preventDefault(); requestAsk(ta.value); });

  $('compose').addEventListener('click', e => {
    const b = e.target.closest('[data-i]');
    if (!b) return;
    requestAsk(I18N[lang].feelings[Number(b.dataset.i)].query);
  });
  $('more').addEventListener('click', () => {
    $('rest').hidden = !$('rest').hidden;
    renderMore();
  });

  /* ---------- motion ---------- */

  function stars() {
    const box = $('stars');
    let s = 20260928;   // fixed seed: the same sky every visit, no layout jump
    const rnd = () => { s |= 0; s = (s + 0x6D2B79F5) | 0; let x = Math.imul(s ^ (s >>> 15), 1 | s); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
    for (let i = 0; i < 44; i++) {
      const d = document.createElement('i');
      const size = 1 + rnd() * 1.6;
      d.style.cssText = `left:${(rnd() * 100).toFixed(1)}%;top:${(rnd() * 78).toFixed(1)}%;width:${size.toFixed(1)}px;height:${size.toFixed(1)}px;--t:${(3 + rnd() * 4).toFixed(1)}s;--dl:${(rnd() * -6).toFixed(1)}s`;
      box.appendChild(d);
    }
  }

  function reveals() {
    const items = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window) || reduced) { items.forEach(n => n.classList.add('in')); return; }
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
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

  /* ---------- start ---------- */

  const select = $('lang');
  LANGS.forEach(l => {
    const o = el('option', null, I18N[l].name);
    o.value = l;
    select.appendChild(o);
  });
  select.addEventListener('change', () => setLang(select.value, true));

  setLang(detectLang(), false);
  stars();
  reveals();
  scrollEffects();
})();

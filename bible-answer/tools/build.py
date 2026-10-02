#!/usr/bin/env python3
"""Builds the Bible Answer website: one static page per language, plus sitemap.xml and robots.txt.

    python3 tools/build.py                                   # for artypeace.github.io/bible-answer
    python3 tools/build.py --site-url https://bible-answer.com   # when the site moves to its own domain
    python3 tools/build.py --store-url https://apps.apple.com/app/id0000000000 --app-store-id 0000000000

Text comes from two files: app-strings.json (taken out of the app by extract_from_app.py,
never edited by hand) and site-strings.json (the website's own copy). Standard library only.

Why a build step: every language is a page of its own, readable by a search engine without
running a script, with its own title, description, canonical address and hreflang links.
The only script the pages run is cosmetic (reveal on scroll, parallax, the demo's timing).
"""
import argparse, base64, datetime, hashlib, html, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
APP = json.loads((HERE / 'app-strings.json').read_text('utf-8'))
SITE = json.loads((HERE / 'site-strings.json').read_text('utf-8'))
LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']

FEATURED = [0, 13, 5, 1, 6, 3]     # the six the app shows first: anxious, lonely, afraid, can't cope, no strength, lost
POSITIVE = [14, 15, 16, 17, 18]    # "with a thankful heart"
ICONS = ['anxious', 'overwhelmed', 'selfworth', 'lost', 'courage', 'future', 'exhausted', 'forgiveness',
         'morning', 'anger', 'guilt', 'trust', 'money', 'lonely', 'gratitude', 'joy', 'praise', 'goodnews', 'peace']
DEMO_FEELING = 0                   # "I'm anxious and I can't settle." -> Philippians 4:6-7

BOOT = "document.documentElement.classList.add('js')"   # marks that scripts run, so hidden-until-revealed styles apply
BOOT_HASH = 'sha256-' + base64.b64encode(hashlib.sha256(BOOT.encode()).digest()).decode()

e = lambda s: html.escape(str(s), quote=True)


def rel(src, dst):
    """Relative link from the page of language `src` to the page of language `dst`."""
    here = SITE[src]['path']
    there = SITE[dst]['path']
    up = '../' if here else ''
    return (up + there) or './'


def icon(name, base, cls='ico'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><use href="{base}assets/feelings.svg#feel-{name}"></use></svg>'


# ---- small line drawings for the devices section (gold, 1.4 stroke, like the app's own icons) ----
ART = {
    'iphone': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="14" y="14" width="74" height="56" rx="8"/><path d="M26 30h30M26 38h46M26 46h38" opacity=".5"/><rect x="72" y="26" width="34" height="58" rx="8" fill="var(--bg)"/><path d="M80 40h18M80 48h18M80 56h12" opacity=".5"/><path d="M85 31h8" opacity=".5"/></svg>',
    'mac': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="10" width="96" height="58" rx="6"/><path d="M12 18h96M12 10v8"/><path d="M92 14h.01M97 14h.01M102 14h.01" stroke-width="2.4"/><path d="M26 32h38M26 40h52M26 48h30" opacity=".5"/><path d="M50 78h20M60 68v10" opacity=".7"/><path d="M20 14q4-3 8 0q-4 3-8 0zM28 14l3-2v4z" fill="currentColor" stroke-width="1"/></svg>',
    'watch': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="38" y="12" width="44" height="66" rx="13"/><path d="M46 12l3-9h22l3 9M46 78l3 9h22l3-9" opacity=".6"/><circle cx="60" cy="45" r="14" opacity=".55"/><path d="M60 31a14 14 0 0 1 14 14" stroke-width="2.4"/><path d="M56 45h8M60 41v8" opacity=".9"/></svg>',
    'widgets': '<svg viewBox="0 0 120 90" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="14" y="12" width="46" height="46" rx="12"/><path d="M24 26h26M24 33h20M24 40h24" opacity=".5"/><rect x="68" y="12" width="38" height="20" rx="8"/><path d="M76 22h22" opacity=".5"/><rect x="68" y="38" width="38" height="20" rx="8"/><path d="M76 48h16" opacity=".5"/><path d="M14 70h92" opacity=".35"/></svg>',
}


def hreflang_links(site_url):
    out = []
    for l in LANGS:
        out.append(f'<link rel="alternate" hreflang="{e(SITE[l]["hreflang"])}" href="{e(site_url + "/" + SITE[l]["path"])}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{e(site_url + "/")}">')
    return '\n'.join(out)


def page(lang, a):
    s, ap = SITE[lang], APP[lang]
    base = '../' if s['path'] else ''
    site_url = a.site_url.rstrip('/')
    canonical = site_url + '/' + s['path']
    og = f'{site_url}/assets/og.jpg'
    sample = s['sample']
    feelings = ap['feelings']
    query = feelings[DEMO_FEELING]['query']

    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'WebSite', '@id': site_url + '/#site', 'name': 'Bible Answer', 'url': site_url + '/', 'inLanguage': [SITE[l]['hreflang'] for l in LANGS]},
            {'@type': 'MobileApplication', '@id': site_url + '/#app', 'name': 'Bible Answer', 'description': s['metaDescription'],
             'applicationCategory': 'LifestyleApplication', 'operatingSystem': 'iOS, iPadOS, macOS, watchOS',
             'inLanguage': [SITE[l]['hreflang'] for l in LANGS], 'url': canonical, 'image': og,
             **({'downloadUrl': a.store_url} if a.store_url else {})},
        ],
    }
    ld_json = json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/')

    store = ''
    if a.store_url:
        store = f'<a class="btn btn--gold" href="{e(a.store_url)}">{e(s["store"])}</a>'
    nav_store = (f'<a class="btn btn--gold btn--small" href="{e(a.store_url)}">{e(s["store"])}</a>' if a.store_url else '')

    current = ' aria-current="true"'
    lang_items = ''.join(
        f'<li><a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}"'
        f'{current if l == lang else ""}>{e(APP[l]["name"])}</a></li>' for l in LANGS)
    hero_langs = ' · '.join(
        f'<a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}">{e(APP[l]["name"])}</a>' for l in LANGS)
    foot_langs = '<span class="dot">·</span>'.join(
        f'<a href="{rel(lang, l)}" lang="{e(SITE[l]["htmlLang"])}" hreflang="{e(SITE[l]["hreflang"])}">{e(APP[l]["name"])}</a>' for l in LANGS)

    featured = ''.join(
        f'<div class="chip-lg{" first" if i == DEMO_FEELING else ""}"><span class="disc">{icon(ICONS[i], base)}</span><span>{e(feelings[i]["label"])}</span></div>'
        for i in FEATURED)
    warm = ''.join(f'<span class="pill pill--warm">{icon(ICONS[i], base)}<span>{e(feelings[i]["label"])}</span></span>' for i in POSITIVE)

    def block(label, text, quiet, i):
        return (f'<div class="block part" style="--i:{i}"><div class="head"><h3 class="label">{e(label)}</h3><i></i></div>'
                f'<p class="body{" body--quiet" if quiet else ""}">{e(text)}</p></div>')

    answer = f'''<article class="answer demo__answer" aria-label="{e(s["demoTag"])}: {e(sample["reference"])}">
        <p class="tag">{e(s["demoTag"])}</p>
        <div class="spread">
          <div class="verse-page">
            <div class="q part" style="--i:0">{e(query)}</div>
            <p class="ref part" style="--i:1">{e(sample["reference"])}</p>
            <hr class="hair part" style="--i:2">
            <blockquote class="verse part" style="--i:3">{e(sample["verse"])}</blockquote>
            <hr class="hair part" style="--i:4">
            <div class="credit part" style="--i:5">{e(sample["translation"])}</div>
          </div>
          <div class="gutter"></div>
          <div class="reading">
            {block(ap["forYou"], sample["forYou"], False, 6)}
            <div class="prayer part" style="--i:7"><div class="head"><i></i><h3 class="label">{e(ap["prayer"])}</h3><i></i></div><p>{e(sample["prayer"])}</p></div>
            {block(ap["context"], sample["context"], True, 8)}
            <div class="diamond part" style="--i:9"><i></i><b></b><i></i></div>
            <p class="fine part" style="--i:10">{e(s["fine"])} <a href="{base}terms#{e(lang)}">{e(s["terms"])}</a></p>
          </div>
        </div>
      </article>'''

    devices = ''.join(
        f'<article class="device reveal" style="--d:{d}s"><div class="device__art" aria-hidden="true">{ART[k]}</div><h3>{e(s[k + "T"])}</h3><p>{e(s[k + "P"])}</p></article>'
        for d, k in zip((0, .1, .2, .3), ('iphone', 'mac', 'watch', 'widgets')))

    apple_banner = f'<meta name="apple-itunes-app" content="app-id={e(a.app_store_id)}">\n' if a.app_store_id else ''
    others = ''.join(f'<meta property="og:locale:alternate" content="{e(SITE[l]["ogLocale"])}">\n' for l in LANGS if l != lang)

    return f'''<!doctype html>
<html lang="{e(s["htmlLang"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' '{BOOT_HASH}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>{e(s["metaTitle"])}</title>
<meta name="description" content="{e(s["metaDescription"])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{e(canonical)}">
{hreflang_links(site_url)}
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0F1628">
{apple_banner}<meta property="og:type" content="website">
<meta property="og:site_name" content="Bible Answer">
<meta property="og:title" content="{e(s["metaTitle"])}">
<meta property="og:description" content="{e(s["metaDescription"])}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(og)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Bible Answer">
<meta property="og:locale" content="{e(s["ogLocale"])}">
{others}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(s["metaTitle"])}">
<meta name="twitter:description" content="{e(s["metaDescription"])}">
<meta name="twitter:image" content="{e(og)}">
<link rel="icon" type="image/png" sizes="32x32" href="{base}assets/favicon-32.png">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<link rel="preload" href="{base}fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}site.css">
<script>{BOOT}</script>
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>
<a class="skip" href="#main">{e(s["skip"])}</a>
<div class="sky" aria-hidden="true"><div class="sky__img"></div><div class="stars" id="stars"></div><div class="sky__veil"></div></div>

<header class="nav">
  <div class="nav__in">
    <a class="mark" href="{rel(lang, lang)}">Bible Answer</a>
    <nav class="nav__links" aria-label="Bible Answer">
      <a href="#ask">{e(s["navAsk"])}</a>
      <a href="#read">{e(s["navRead"])}</a>
      <a href="#listen">{e(s["navListen"])}</a>
      <a href="#devices">{e(s["navDevices"])}</a>
      <a href="#private">{e(s["navPrivacy"])}</a>
    </nav>
    <div class="nav__tools">
      <details class="langmenu"><summary aria-label="{e(s["langs"])}">{e(ap["name"])}</summary><ul>{lang_items}</ul></details>
      {nav_store}
    </div>
  </div>
</header>

<main id="main">
  <section class="hero" aria-labelledby="h-hero">
    <div class="hero__in" id="heroIn">
      <img class="hero__icon rise" style="--i:0" src="{base}assets/icon.png" width="96" height="96" alt="Bible Answer">
      <h1 id="h-hero" class="rise" style="--i:1">{e(ap["tagline"])}</h1>
      <p class="hero__sub rise" style="--i:2">{e(ap["subtitle"])}</p>
      <div class="hero__cta rise" style="--i:3">
        {store}
        <a class="{"link" if a.store_url else "btn btn--gold"}" href="#ask">{e(s["seeHow"])}</a>
      </div>
      <p class="hero__langs rise" style="--i:4">{hero_langs}</p>
    </div>
    <svg class="hero__hint ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
  </section>

  <section class="section ask" id="ask" aria-labelledby="h-ask">
    <div class="wrap">
      <h2 id="h-ask" class="reveal">{e(ap["prompt"])}</h2>
      <p class="lede reveal" style="--d:.1s">{e(ap["subtitle"])}</p>
      <div class="demo reveal" style="--d:.15s" data-demo>
        <div class="demo__ask" aria-hidden="true">
          <div class="feelings">{featured}</div>
          <div class="good">{e(ap["goodDays"])}</div>
          <div class="pills">{warm}</div>
          <div class="composer demo__composer"><span class="demo__input"><span class="typed" style="--n:{len(query)}">{e(query)}</span><span class="caret"></span></span><span class="send"><svg class="ico" viewBox="0 0 24 24"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg></span></div>
        </div>
        {answer}
      </div>
      <p class="demo__note reveal">{e(s["demoNote"])}</p>
      {('<p class="demo__cta reveal">' + store + '</p>') if a.store_url else ''}
    </div>
  </section>

  <section class="section" id="read" aria-labelledby="h-read">
    <div class="wrap">
      <div class="feature">
        <div class="feature__text reveal">
          <div class="eyebrow">{e(s["navRead"])}</div>
          <h2 id="h-read">{e(s["readH"])}</h2>
          <p>{e(s["readP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card reader" data-parallax aria-hidden="true">
            <span class="skl skl--head"></span>
            <span class="skl"><b></b></span><span class="skl" style="width:96%"></span><span class="skl" style="width:88%"></span>
            <span class="skl" style="margin-top:22px"><b></b></span><span class="skl" style="width:92%"></span><span class="skl" style="width:64%"></span>
            <div class="sheet"><span class="skl skl--head" style="width:28%;margin-bottom:14px"></span><span class="skl" style="margin-top:9px"></span><span class="skl" style="width:82%;margin-top:9px"></span></div>
          </div>
        </div>
      </div>

      <div class="feature feature--flip" id="listen">
        <div class="feature__text reveal">
          <div class="eyebrow">{e(s["navListen"])}</div>
          <h2>{e(s["listenH"])}</h2>
          <p>{e(s["listenP"])}</p>
        </div>
        <div class="reveal" style="--d:.15s">
          <div class="card player" data-parallax aria-hidden="true">
            <div class="player__img"></div><div class="player__veil"></div>
            <div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div>
            <div class="eq"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
            <div class="bar"><i></i></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section platforms" id="devices" aria-labelledby="h-devices">
    <div class="wrap">
      <h2 id="h-devices" class="reveal">{e(s["devicesH"])}</h2>
      <div class="device-grid">{devices}</div>
    </div>
  </section>

  <section class="section privacy" id="private" aria-labelledby="h-priv">
    <div class="wrap">
      <h2 id="h-priv" class="reveal">{e(s["privH"])}</h2>
      <div class="trio">
        <div class="reveal"><h3>{e(s["priv1T"])}</h3><p>{e(s["priv1P"])}</p></div>
        <div class="reveal" style="--d:.12s"><h3>{e(s["priv2T"])}</h3><p>{e(s["priv2P"])}</p></div>
        <div class="reveal" style="--d:.24s"><h3>{e(s["priv3T"])}</h3><p>{e(s["priv3P"])}</p></div>
      </div>
    </div>
  </section>
</main>

<footer class="foot">
  <p><a href="{base}privacy#{e(lang)}">{e(s["privacy"])}</a><span class="dot">·</span><a href="{base}terms#{e(lang)}">{e(s["terms"])}</a><span class="dot">·</span><a href="mailto:bibleanswerapp@gmail.com">bibleanswerapp@gmail.com</a></p>
  <p>{foot_langs}</p>
</footer>
<script src="{base}app.js" defer></script>
</body>
</html>
'''


def sitemap(a):
    site_url = a.site_url.rstrip('/')
    rows = []
    for l in LANGS:
        alts = ''.join(
            f'\n    <xhtml:link rel="alternate" hreflang="{SITE[o]["hreflang"]}" href="{site_url}/{SITE[o]["path"]}"/>' for o in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{site_url}/"/>'
        rows.append(f'  <url>\n    <loc>{site_url}/{SITE[l]["path"]}</loc>{alts}\n    <lastmod>{a.lastmod}</lastmod>\n  </url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--site-url', default='https://artypeace.github.io/bible-answer', help='where the site is served (no trailing slash)')
    p.add_argument('--store-url', default='', help='App Store link; the download buttons appear when it is set')
    p.add_argument('--app-store-id', default='', help='App Store id; adds the Smart App Banner')
    p.add_argument('--lastmod', default=datetime.date.today().isoformat())
    a = p.parse_args()

    for lang in LANGS:
        out = ROOT / SITE[lang]['path'] / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, a), encoding='utf-8')
        print('wrote', out.relative_to(ROOT))
    (ROOT / 'sitemap.xml').write_text(sitemap(a), encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {a.site_url.rstrip("/")}/sitemap.xml\n', encoding='utf-8')
    print('wrote sitemap.xml, robots.txt')


if __name__ == '__main__':
    main()

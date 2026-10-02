# Bible Answer website

Static pages, one per language: `/` (English), `/pt/`, `/es/`, `/ru/`, `/fr/`, `/fil/`. Each is a complete page with its own title, description, canonical address and `hreflang` links, readable without running a script. `privacy.html`, `terms.html` and `style.css` are the legal pages the apps link to and are not generated.

The site shows what the app does; it does **not** ask the server anything. The example answer is fixed text. The pages make no requests to any other host (the Content-Security-Policy says so: `connect-src 'none'`).

## Rebuilding

```
python3 tools/build.py
```

Python 3, standard library only. It rewrites `index.html`, `*/index.html`, `sitemap.xml` and `robots.txt`; commit the result. Options: `--site-url`, `--store-url`, `--app-store-id` (see `--help`).

| File | What it is |
| --- | --- |
| `tools/app-strings.json` | Words shared with the app (tagline, feelings, section names). Produced by `tools/extract_from_app.py` from the app's `Localizable.swift`; do not edit by hand. |
| `tools/site-strings.json` | The website's own copy, titles and descriptions, and the example answer, in all six languages. |
| `tools/build.py` | Turns the two files into pages. |
| `site.css`, `app.js` | Look and motion (reveal on scroll, parallax, the demo's timing). `app.js` is cosmetic; the pages work without it. |

When the App Store page exists: `python3 tools/build.py --store-url https://apps.apple.com/app/id… --app-store-id …` shows the download buttons and adds the Smart App Banner.

## Moving to its own domain

Do not put a `CNAME` in this repository: it is the user site `artypeace.github.io`, and a custom domain here would redirect all of its pages, including the privacy and terms addresses the apps already use.

1. Create a separate public repository for the site and copy the contents of this folder into its root.
2. `python3 tools/build.py --site-url https://bible-answer.com` (and the store options).
3. Add a file `CNAME` containing `bible-answer.com`; turn on GitHub Pages for `main`; once DNS resolves, tick *Enforce HTTPS*.
4. At the registrar: four `A` records for `@` — `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` — and a `CNAME` for `www` pointing to `artypeace.github.io`. (Check GitHub's current Pages documentation for the addresses.)
5. Verify the domain in GitHub (Settings → Pages → Add a domain) and in Google Search Console and Bing Webmaster Tools; submit `sitemap.xml`.
6. Leave `privacy` and `terms` where they are until the app links to the new addresses; then replace the old pages here with redirects.

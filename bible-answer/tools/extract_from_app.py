#!/usr/bin/env python3
"""Reads the strings the website shares with the app out of the app's own source and
writes tools/app-strings.json. Run it when the app's wording changes:

    python3 tools/extract_from_app.py /path/to/bible-answer/BibleAnswer/Models/Localizable.swift

Nothing in app-strings.json is written by hand. The website's own copy lives in
site-strings.json."""
import json, re, sys, pathlib

src_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(__file__).with_name('app-strings.json')
src = src_path.read_text(encoding='utf-8')

LANGS = ['en', 'pt', 'es', 'ru', 'fr', 'fil']
SWIFT = {'en': 'english', 'pt': 'portuguese', 'es': 'spanish', 'ru': 'russian', 'fr': 'french', 'fil': 'filipino'}
KEYS = {
    'tagline': 'appTagline', 'subtitle': 'welcome_subtitle', 'prompt': 'welcome_prompt',
    'placeholder': 'inputPlaceholder', 'goodDays': 'feelingsGoodDays',
    'forYou': 'answerSectionForYou', 'context': 'answerSectionContext', 'prayer': 'answerSectionPrayer',
}
NAMES = {'en': 'English', 'pt': 'Português', 'es': 'Español', 'ru': 'Русский', 'fr': 'Français', 'fil': 'Filipino'}

starts = [(m.group(1), m.start()) for m in re.finditer(r'static let (english|portuguese|spanish|russian|french|filipino) = ', src)]
starts.append(('end', len(src)))
english_strings = src[src.index('private static let englishStrings'):starts[0][1]]
blocks = {n: src[p:starts[i + 1][1]] for i, (n, p) in enumerate(starts[:-1])}


def unescape(s):
    return s.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')


def typo(s):
    """A straight apostrophe between letters becomes a typographic one."""
    return re.sub(r"(?<=\w)'(?=\w)", '’', s)


def grab(block, key):
    m = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % key, block)
    return typo(unescape(m.group(1))) if m else None


def feelings(lang):
    b = blocks[SWIFT[lang]]
    i = b.index('feelings: feelings([')
    body = b[i:b.index('])', i)]
    pairs = re.findall(r'\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)', body)
    assert len(pairs) == 19, (lang, len(pairs))
    return [{'label': typo(unescape(a)), 'query': typo(unescape(q))} for a, q in pairs]


out = {}
for lang in LANGS:
    d = {}
    for k, swift_key in KEYS.items():
        v = grab(blocks[SWIFT[lang]], swift_key) if lang != 'en' else None
        d[k] = v if v is not None else grab(english_strings, swift_key)
    d['name'] = NAMES[lang]
    d['feelings'] = feelings(lang)
    out[lang] = d
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('wrote', out_path, '-', len(KEYS), 'strings and 19 feelings x', len(LANGS), 'languages')

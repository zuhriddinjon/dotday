#!/usr/bin/env python3
"""Dotday saytini yig'adi: src/i18n/*.json + src/guide/*.json -> statik HTML.

    python3 src/build.py

Natija repo ildiziga yoziladi (GitHub Pages `main` / root dan xizmat qiladi).
Barcha ichki havolalar nisbiy — eski github.io/dotday havolalari ham dotday.uz ga 301 bilan o'tadi.
"""
import datetime
import html
import json
import re
import urllib.parse
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
SITE = "https://dotday.uz"
PACKAGE = "uz.habitly.tracker"
EMAIL = "support@dotday.uz"
INSTAGRAM = "https://www.instagram.com/dotday.app/"
PLAY = f"https://play.google.com/store/apps/details?id={PACKAGE}"
TODAY = datetime.date.today().isoformat()

# code, papka, til nomi, yo'nalish, Play hl, og:locale
LANGS = [
    ("en", "", "English", "ltr", "en", "en_US"),
    ("uz", "uz/", "O‘zbekcha", "ltr", "uz", "uz_UZ"),
    ("ru", "ru/", "Русский", "ltr", "ru", "ru_RU"),
    ("es", "es/", "Español", "ltr", "es", "es_ES"),
    ("pt-BR", "pt-BR/", "Português (Brasil)", "ltr", "pt-BR", "pt_BR"),
    ("de", "de/", "Deutsch", "ltr", "de", "de_DE"),
    ("fr", "fr/", "Français", "ltr", "fr", "fr_FR"),
    ("tr", "tr/", "Türkçe", "ltr", "tr", "tr_TR"),
    ("id", "id/", "Bahasa Indonesia", "ltr", "id", "id_ID"),
    ("hi", "hi/", "हिन्दी", "ltr", "hi", "hi_IN"),
    ("ja", "ja/", "日本語", "ltr", "ja", "ja_JP"),
    ("ko", "ko/", "한국어", "ltr", "ko", "ko_KR"),
    ("ar", "ar/", "العربية", "rtl", "ar", "ar_AR"),
]
LANGS = [l for l in LANGS if (SRC / "i18n" / f"{l[0]}.json").exists()]
LANG = {l[0]: dict(code=l[0], path=l[1], name=l[2], dir=l[3], hl=l[4], og=l[5]) for l in LANGS}

T = {code: json.loads((SRC / "i18n" / f"{code}.json").read_text("utf-8")) for code in LANG}
GUIDES = {p.stem: json.loads(p.read_text("utf-8")) for p in sorted((SRC / "guide").glob("*.json"))}
CAPTIONS = json.loads((SRC / "captions.json").read_text("utf-8"))
BLOG_UI = json.loads((SRC / "blog" / "ui.json").read_text("utf-8"))
# Mavzular tartibi (blog sahifasida shu tartibda chiqadi); qolganlari alifbo bo'yicha
TOPIC_ORDER = ["habit-formation", "21-day-rule", "habit-tracker", "procrastination", "wake-up-early"]
TOPIC_ICON = {"habit-formation": "🌱", "21-day-rule": "📅", "habit-tracker": "✅", "procrastination": "⏳", "wake-up-early": "🌅"}
BLOG = {}  # topic -> {code: article}
for _d in sorted((SRC / "blog").iterdir(), key=lambda d: (TOPIC_ORDER.index(d.name) if d.name in TOPIC_ORDER else 99, d.name)):
    if _d.is_dir():
        BLOG[_d.name] = {p.stem: json.loads(p.read_text("utf-8")) for p in sorted(_d.glob("*.json")) if p.stem in LANG}
BLOG_LANGS = [c for c in LANG if any(c in arts for arts in BLOG.values())]


def e(s):
    return html.escape(str(s), quote=True)


def legal(page, code):
    return f"{page}.html" if code == "en" else f"{page}-{code}.html"


def play_url(code, medium="website"):
    ref = f"utm_source%3Ddotday.uz%26utm_medium%3D{medium}%26utm_campaign%3D{code}"
    return f"https://play.google.com/store/apps/details?id={PACKAGE}&hl={LANG[code]['hl']}&referrer={ref}"


def landing_path(code):
    return LANG[code]["path"]


def guide_path(code):
    return f"{LANG[code]['path']}guide/"


def blog_path(code):
    return f"{LANG[code]['path']}blog/"


def article_path(code, topic):
    return f"{blog_path(code)}{BLOG[topic][code]['slug']}/"


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"


# ---------- SVG ----------
SVG_SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
SVG_MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/></svg>'
SVG_GLOBE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'
SVG_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.6 2.3c-.4.3-.6.8-.6 1.4v16.6c0 .6.2 1.1.6 1.4l9.3-9.7-9.3-9.7zm10.4 8.6 2.7-2.8L6.3 1.7l8.7 9.2zm0 2.2-8.7 9.2 11.4-6.4-2.7-2.8zm5.9-3.3-2.3-1.3-3 3.1 3 3.1 2.3-1.3c1.1-.6 1.1-3 0-3.6z"/></svg>'
SVG_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
SVG_PREV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
SVG_NEXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>'
SVG_INSTAGRAM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>'
SVG_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'

THEME_INIT = ("<script>(function(){var d=document.documentElement;d.classList.add('js');"
              "try{var t=localStorage.getItem('theme');if(t)d.setAttribute('data-theme',t)}catch(e){}})()</script>")


# ---------- Umumiy bo'laklar ----------
def head(code, *, title, desc, canonical, alternates, root, page, image=None, jsonld=(), og_type="website"):
    t = T[code]
    lines = [
        "<!doctype html>",
        f'<html lang="{code}" dir="{LANG[code]["dir"]}" data-lang="{code}" data-root="{root}" data-page="{page}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{e(title)}</title>",
        f'<meta name="description" content="{e(desc)}">',
        f'<link rel="canonical" href="{SITE}/{canonical}">',
    ]
    for alt_code, alt_path in alternates:
        lines.append(f'<link rel="alternate" hreflang="{alt_code}" href="{SITE}/{alt_path}">')
    if alternates:
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/{dict(alternates)["en"]}">')
    img = image or f"{SITE}/assets/og.png"
    lines += [
        '<meta name="theme-color" content="#fbfaff">',
        '<meta name="color-scheme" content="light dark">',
        f'<meta property="og:type" content="{og_type}">',
        '<meta property="og:site_name" content="Dotday">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{SITE}/{canonical}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1024">',
        '<meta property="og:image:height" content="500">',
        f'<meta property="og:locale" content="{LANG[code]["og"]}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="google-play-app" content="app-id={PACKAGE}">',
        f'<link rel="icon" href="/favicon.ico" sizes="48x48">',
        f'<link rel="icon" href="{root}assets/icon-96.png" sizes="96x96" type="image/png">',
        f'<link rel="icon" href="{root}assets/icon.svg" type="image/svg+xml">',
        f'<link rel="apple-touch-icon" href="{root}assets/icon-512.png">',
        f'<link rel="manifest" href="{root}site.webmanifest">',
        f'<link rel="preload" href="{root}assets/manrope.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{root}assets/style.css">',
        THEME_INIT,
    ]
    lines += [ld(j) for j in jsonld]
    lines.append("</head>")
    return "\n".join(lines)


def header(code, root, *, page, alternates):
    t = T[code]
    home = root + landing_path(code)
    guide_code = code if code in GUIDES else "en"
    links = [
        f'<a href="{home}#features">{e(t["nav_features"])}</a>',
        f'<a href="{root}{guide_path(guide_code)}">{e(t["nav_guide"])}</a>',
        f'<a href="{home}#faq">{e(t["nav_faq"])}</a>',
    ]
    if code in BLOG_LANGS:
        links.insert(2, f'<a href="{root}{blog_path(code)}">{e(BLOG_UI[code]["nav_blog"])}</a>')
    alt = dict(alternates)
    items = []
    for c in LANG:
        href = root + (alt[c] if c in alt else landing_path(c))
        cur = ' aria-current="page"' if c == code else ""
        items.append(f'<li><a href="{href}" hreflang="{c}" lang="{c}"{cur}>{e(LANG[c]["name"])}</a></li>')
    return f"""<a class="skip" href="#main">{e(t["skip"])}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{home}"><img src="{root}assets/icon.svg" alt="" width="34" height="34">Dotday</a>
    <nav class="nav-links" aria-label="{e(t["nav_label"])}">{"".join(links)}</nav>
    <details class="lang">
      <summary aria-label="{e(t["lang_label"])}">{SVG_GLOBE}{e(code)}</summary>
      <ul>{"".join(items)}</ul>
    </details>
    <button class="icon-btn theme-toggle" type="button" aria-label="{e(t["theme_label"])}" aria-pressed="false">{SVG_SUN}{SVG_MOON}</button>
    <a class="btn btn-primary btn-small header-cta" href="{e(play_url(code, "header"))}">{e(t["nav_get"])}</a>
  </div>
</header>"""


def play_button(code, medium):
    t = T[code]
    return (f'<a class="play-btn" href="{e(play_url(code, medium))}">{SVG_PLAY}'
            f'<span><small>{e(t["play_small"])}</small><b>Google Play</b></span></a>')


def footer(code, root):
    t = T[code]
    home = root + landing_path(code)
    guide_code = code if code in GUIDES else "en"
    langs = "".join(f'<a href="{root}{landing_path(c)}" hreflang="{c}" lang="{c}">{e(LANG[c]["name"])}</a>' for c in LANG)
    blog_li = f'<li><a href="{root}{blog_path(code)}">{e(BLOG_UI[code]["nav_blog"])}</a></li>' if code in BLOG_LANGS else ""
    return f"""<footer>
  <div class="wrap foot">
    <div>
      <a class="brand" href="{home}"><img src="{root}assets/icon.svg" alt="" width="34" height="34">Dotday</a>
      <p>{e(t["foot_tagline"])}</p>
      <p class="social"><a class="icon-btn" href="{INSTAGRAM}" rel="me noopener" target="_blank" aria-label="Instagram @dotday.app">{SVG_INSTAGRAM}</a><a class="icon-btn" href="{e(play_url(code, "footer-icon"))}" aria-label="Google Play">{SVG_PLAY}</a></p>
      <p>© 2026 Dotday</p>
    </div>
    <div>
      <h3>{e(t["foot_app"])}</h3>
      <ul>
        <li><a href="{e(play_url(code, "footer"))}">Google Play</a></li>
        <li><a href="{root}{guide_path(guide_code)}">{e(t["nav_guide"])}</a></li>
        {blog_li}
        <li><a href="{root}{legal("privacy", code)}">{e(t["foot_privacy"])}</a></li>
        <li><a href="{root}{legal("terms", code)}">{e(t["foot_terms"])}</a></li>
        <li><a href="mailto:{EMAIL}">{e(t["foot_contact"])}</a></li>
      </ul>
    </div>
    <div>
      <h3>{e(t["lang_label"])}</h3>
      <div class="langs-list">{langs}</div>
    </div>
  </div>
</footer>
<div class="lang-suggest" role="region" aria-live="polite" hidden><span></span><a class="btn btn-primary btn-small" href="#"></a><button class="icon-btn" type="button" aria-label="{e(t["close"])}">{SVG_CLOSE}</button></div>
<script src="{root}assets/langs.js" defer></script>
<script src="{root}assets/site.js" defer></script>
</body>
</html>
"""


def phone(root, code, light, dark=None, *, alt, size="", eager=False):
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    cls = f"phone {size}".strip()
    src = f"{root}assets/shots/{code}"
    if dark:
        imgs = (f'<img class="shot-light" src="{src}/{light}.webp" alt="{e(alt)}" width="600" height="1233" {loading} decoding="async">'
                f'<img class="shot-dark" src="{src}/{dark}.webp" alt="{e(alt)}" width="600" height="1233" loading="lazy" decoding="async">')
    else:
        imgs = f'<img src="{src}/{light}.webp" alt="{e(alt)}" width="600" height="1233" {loading} decoding="async">'
    return f'<div class="{cls}">{imgs}</div>'


# ---------- Landing ----------
def landing(code):
    t = T[code]
    root = "../" * landing_path(code).count("/")
    canonical = landing_path(code)
    alternates = [(c, landing_path(c)) for c in LANG]
    caps = CAPTIONS[code]

    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": code,
              "mainEntity": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in t["faq"]]}
    app_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Dotday", "url": f"{SITE}/",
             "logo": f"{SITE}/assets/icon-512.png", "email": EMAIL,
             "sameAs": [INSTAGRAM, PLAY]},
            {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Dotday",
             "publisher": {"@id": f"{SITE}/#org"}, "inLanguage": list(LANG)},
            {"@type": "MobileApplication", "@id": f"{SITE}/#app", "name": "Dotday", "alternateName": t["app_name"],
             "description": t["meta_desc"], "url": f"{SITE}/{canonical}", "operatingSystem": "Android",
             "applicationCategory": "HealthApplication", "applicationSubCategory": "Habit tracker",
             "image": f"{SITE}/assets/icon-512.png",
             "screenshot": [f"{SITE}/assets/shots/{code}/{s}.webp" for s in ("01_today", "03_stats", "04_insights")],
             "installUrl": f"https://play.google.com/store/apps/details?id={PACKAGE}",
             "downloadUrl": f"https://play.google.com/store/apps/details?id={PACKAGE}",
             "inLanguage": code, "publisher": {"@id": f"{SITE}/#org"},
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "category": "free"}},
        ],
    }

    out = [head(code, title=t["meta_title"], desc=t["meta_desc"], canonical=canonical, alternates=alternates,
                root=root, page="", jsonld=[app_ld, faq_ld]),
           "<body>", header(code, root, page="", alternates=alternates), '<main id="main">']

    trust = "".join(f"<li>{SVG_CHECK}{e(x)}</li>" for x in t["trust"])
    out.append(f"""<section class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow"><i>🌱</i>{e(t["hero_eyebrow"])}</span>
      <h1>{e(t["hero_h1a"])}<br><span class="grad">{e(t["hero_h1b"])}</span></h1>
      <p class="lead">{e(t["hero_lead"])}</p>
      <div class="hero-actions">{play_button(code, "hero")}<span class="hero-note">{e(t["hero_note"])}</span></div>
      <ul class="trust">{trust}</ul>
    </div>
    <div class="hero-visual">
      <div class="chip chip-1"><i>🔥</i><div>{e(t["chip1_title"])}<small>{e(t["chip1_sub"])}</small></div></div>
      {phone(root, code, "01_today", "06_today_dark", alt=caps[0], eager=True)}
      <div class="chip chip-2"><i>✅</i><div>{e(t["chip2_title"])}<small>{e(t["chip2_sub"])}</small></div></div>
    </div>
  </div>
</section>""")

    shows = []
    for i, s in enumerate(t["showcases"]):
        pts = "".join(f"<li>{e(p)}</li>" for p in s["points"])
        flip = " flip" if i % 2 else ""
        shows.append(f"""<div class="showcase{flip} reveal">
      <div class="showcase-media">{phone(root, code, s["shot"], s.get("shot_dark"), alt=s["title"], size="sm")}</div>
      <div><span class="kicker">{e(s["tag"])}</span><h3>{e(s["title"])}</h3><p>{e(s["body"])}</p><ul class="checks">{pts}</ul></div>
    </div>""")
    out.append(f"""<section id="features" class="alt">
  <div class="wrap">
    <div class="section-head reveal"><span class="kicker">{e(t["features_kicker"])}</span><h2>{e(t["features_title"])}</h2><p>{e(t["features_sub"])}</p></div>
    {"".join(shows)}
  </div>
</section>""")

    cards = "".join(f'<div class="card reveal"><div class="ico" aria-hidden="true">{c["icon"]}</div><h3>{e(c["title"])}</h3><p>{e(c["body"])}</p></div>'
                    for c in t["cards"])
    out.append(f"""<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="kicker">{e(t["more_kicker"])}</span><h2>{e(t["more_title"])}</h2><p>{e(t["more_sub"])}</p></div>
    <div class="grid">{cards}</div>
  </div>
</section>""")

    shots = ["01_today", "02_detail", "03_stats", "04_insights", "05_templates", "06_today_dark", "07_detail_history", "08_stats_dark"]
    gal = "".join(f'<li><figure>{phone(root, code, s, alt=caps[i], size="sm")}<figcaption>{e(caps[i])}</figcaption></figure></li>'
                  for i, s in enumerate(shots))
    out.append(f"""<section class="alt">
  <div class="wrap"><div class="section-head reveal"><span class="kicker">{e(t["gallery_kicker"])}</span><h2>{e(t["gallery_title"])}</h2></div></div>
  <ul class="gallery" tabindex="0" aria-label="{e(t["gallery_title"])}">{gal}</ul>
  <div class="gallery-nav"><button class="icon-btn" type="button" data-scroll="-1" aria-label="{e(t["prev"])}">{SVG_PREV}</button><button class="icon-btn" type="button" data-scroll="1" aria-label="{e(t["next"])}">{SVG_NEXT}</button></div>
</section>""")

    steps = "".join(f'<li class="reveal"><h3>{e(s["title"])}</h3><p>{e(s["body"])}</p></li>' for s in t["steps"])
    guide_code = code if code in GUIDES else "en"
    out.append(f"""<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="kicker">{e(t["steps_kicker"])}</span><h2>{e(t["steps_title"])}</h2><p>{e(t["steps_sub"])} <a href="{root}{guide_path(guide_code)}">{e(t["steps_guide_link"])} →</a></p></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>""")

    pills = "".join(f"<li>{e(p)}</li>" for p in t["privacy_pills"])
    out.append(f"""<section class="alt">
  <div class="wrap">
    <div class="privacy-card reveal">
      <div class="lock" aria-hidden="true">🔒</div>
      <div><h2>{e(t["privacy_title"])}</h2><p>{e(t["privacy_body"])} <a href="{root}{legal("privacy", code)}">{e(t["foot_privacy"])}</a></p><ul class="pills">{pills}</ul></div>
    </div>
  </div>
</section>""")

    pro = "".join(f"<li>{e(p)}</li>" for p in t["pro_list"])
    out.append(f"""<section id="pro">
  <div class="wrap">
    <div class="pro reveal">
      <span class="kicker">Dotday Pro</span>
      <h2>{e(t["pro_title"])}</h2>
      <p>{e(t["pro_body"])}</p>
      <ul>{pro}</ul>
      {play_button(code, "pro")}
      <p class="fine">{e(t["pro_fine"])}</p>
    </div>
  </div>
</section>""")

    faq = "".join(f'<details><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in t["faq"])
    out.append(f"""<section id="faq" class="alt">
  <div class="wrap">
    <div class="section-head reveal"><span class="kicker">FAQ</span><h2>{e(t["faq_title"])}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>""")

    if code in BLOG_LANGS:
        u = BLOG_UI[code]
        cards = "".join(post_card(tp, code, root) for tp in [tp for tp in BLOG if code in BLOG[tp]][:3])
        out.append(f"""<section class="from-blog">
  <div class="wrap">
    <div class="section-head reveal"><span class="kicker">{e(u["nav_blog"])}</span><h2>{e(u["blog_h1"])}</h2><p>{e(u["blog_lead"])}</p></div>
    <div class="post-grid reveal">{cards}</div>
    <p class="from-blog-more"><a class="btn btn-ghost" href="{root}{blog_path(code)}">{e(u["nav_blog"])} →</a></p>
  </div>
</section>""")

    out.append(f"""<section class="final">
  <div class="wrap reveal">
    <img class="icon-big" src="{root}assets/icon.svg" alt="" width="88" height="88" loading="lazy">
    <h2>{e(t["final_title"])}</h2>
    <p>{e(t["final_body"])}</p>
    {play_button(code, "final")}
  </div>
</section>""")
    out.append("</main>")
    out.append(footer(code, root))
    write(canonical + "index.html", "\n".join(out))


# ---------- Yo'riqnoma ----------
def slug_ok(s):
    assert re.fullmatch(r"[a-z0-9-]+", s), s
    return s


def guide(code):
    g = GUIDES[code]
    t = T[code]
    path = guide_path(code)
    root = "../" * path.count("/")
    alternates = [(c, guide_path(c)) for c in GUIDES]
    article_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "TechArticle", "headline": g["h1"], "description": g["meta_desc"], "inLanguage": code,
             "url": f"{SITE}/{path}", "image": f"{SITE}/assets/og.png", "datePublished": "2026-10-06", "dateModified": TODAY,
             "author": {"@type": "Organization", "name": "Dotday", "url": f"{SITE}/"},
             "publisher": {"@type": "Organization", "name": "Dotday", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/icon-512.png"}},
             "about": {"@type": "MobileApplication", "name": "Dotday", "operatingSystem": "Android"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Dotday", "item": f"{SITE}/{landing_path(code)}"},
                {"@type": "ListItem", "position": 2, "name": g["crumb"], "item": f"{SITE}/{path}"}]},
        ],
    }
    out = [head(code, title=g["meta_title"], desc=g["meta_desc"], canonical=path, alternates=alternates,
                root=root, page="guide/", jsonld=[article_ld], og_type="article"),
           "<body>", header(code, root, page="guide/", alternates=alternates), '<main id="main">']
    toc = "".join(f'<li><a href="#{slug_ok(s["id"])}">{s["icon"]} {e(s["title"])}</a></li>' for s in g["sections"])
    secs = []
    for s in g["sections"]:
        body = s["html"]
        if s.get("shot"):
            body = f'<div class="split"><div>{body}</div>{phone(root, code, s["shot"], s.get("shot_dark"), alt=s["title"], size="sm")}</div>'
        secs.append(f'<section id="{s["id"]}"><h2><span class="n" aria-hidden="true">{s["icon"]}</span>{e(s["title"])}</h2>{body}</section>')
    out.append(f"""<div class="wrap">
  <div class="guide-hero">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}{landing_path(code)}">Dotday</a> / {e(g["crumb"])}</nav>
    <h1>{e(g["h1"])}</h1>
    <p>{e(g["lead"])}</p>
  </div>
  <div class="guide-layout">
    <aside class="toc"><h2>{e(g["toc_title"])}</h2><ol>{toc}</ol></aside>
    <article class="article">
      {"".join(secs)}
      <div class="guide-cta"><div><h2>{e(g["cta_title"])}</h2><p>{e(g["cta_body"])}</p></div>{play_button(code, "guide")}</div>
    </article>
  </div>
</div>
</main>""")
    out.append(footer(code, root))
    write(path + "index.html", "\n".join(out))


# ---------- Blog ----------
ALLOWED_TAGS = {"p", "h3", "ul", "ol", "li", "b", "strong", "em", "a", "sup", "blockquote", "aside", "div", "table", "thead", "tbody", "tr", "th", "td", "br", "sub"}


def check_article(topic, code, a):
    where = f"blog/{topic}/{code}.json"
    for k in ("slug", "meta_title", "meta_desc", "h1", "lead", "read_min", "published", "facts", "sections", "faq", "sources", "cta_title", "cta_body"):
        assert k in a, f"{where}: {k} yo'q"
    slug_ok(a["slug"])
    ids = {src["id"] for src in a["sources"]}
    assert sorted(ids) == list(range(1, len(ids) + 1)), f"{where}: manba raqamlari 1..N emas"
    body = "".join(sec["html"] for sec in a["sections"])
    cited = {int(n) for n in re.findall(r'href="#src-(\d+)"', body)}
    assert cited <= ids, f"{where}: mavjud bo'lmagan manbaga havola {cited - ids}"
    assert ids <= cited | {f["src"] for f in a["facts"]}, f"{where}: ishlatilmagan manba {ids - cited}"
    for f in a["facts"]:
        assert f["src"] in ids, f"{where}: fakt manbasi yo'q"
    for sec in a["sections"]:
        slug_ok(sec["id"])
        for tag in re.findall(r"<\s*([a-zA-Z0-9]+)", sec["html"]):
            assert tag.lower() in ALLOWED_TAGS, f"{where}: ruxsat etilmagan teg <{tag}>"
        assert "style=" not in sec["html"] and "<script" not in sec["html"].lower(), where


def blog_alternates(topic):
    return [(c, article_path(c, topic)) for c in LANG if c in BLOG[topic]]


def ref_link(n):
    return f'<sup class="ref"><a href="#src-{n}">{n}</a></sup>'


def time_tag(iso):
    return f'<time datetime="{e(iso)}" data-fmt>{e(iso)}</time>'


def article_page(topic, code):
    a = BLOG[topic][code]
    u = BLOG_UI[code]
    path = article_path(code, topic)
    root = "../" * path.count("/")
    alternates = blog_alternates(topic)
    modified = a.get("updated", a["published"])
    url = f"{SITE}/{path}"
    jsonld = [{
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BlogPosting", "headline": a["h1"], "description": a["meta_desc"], "inLanguage": code,
             "url": url, "mainEntityOfPage": url, "image": f"{SITE}/assets/og.png",
             "datePublished": a["published"], "dateModified": modified, "timeRequired": f"PT{int(a['read_min'])}M",
             "author": {"@type": "Organization", "name": "Dotday", "url": f"{SITE}/"},
             "publisher": {"@type": "Organization", "name": "Dotday", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/icon-512.png"}},
             "citation": [{"@type": "CreativeWork", "name": src["text"], "url": src["url"]} for src in a["sources"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Dotday", "item": f"{SITE}/{landing_path(code)}"},
                {"@type": "ListItem", "position": 2, "name": u["nav_blog"], "item": f"{SITE}/{blog_path(code)}"},
                {"@type": "ListItem", "position": 3, "name": a["h1"], "item": url}]},
        ],
    }, {
        "@context": "https://schema.org", "@type": "FAQPage", "inLanguage": code,
        "mainEntity": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in a["faq"]],
    }]
    out = [head(code, title=a["meta_title"], desc=a["meta_desc"], canonical=path, alternates=alternates,
                root=root, page="", jsonld=jsonld, og_type="article"),
           "<body>", '<div class="read-progress" aria-hidden="true"><span></span></div>',
           header(code, root, page="", alternates=alternates), '<main id="main">']

    facts = "".join(f'<li><b>{e(f["value"])}</b><span>{e(f["label"])}{ref_link(f["src"])}</span></li>' for f in a["facts"])
    toc_items = [(sec["id"], sec["title"]) for sec in a["sections"]] + [("faq", u["faq_title"]), ("sources", u["sources_title"])]
    toc = "".join(f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in toc_items)
    secs = "".join(f'<section id="{sec["id"]}"><h2>{e(sec["title"])}</h2>{sec["html"]}</section>' for sec in a["sections"])
    faq = "".join(f"<details><summary>{e(q['q'])}</summary><p>{e(q['a'])}</p></details>" for q in a["faq"])
    srcs = "".join(f'<li id="src-{src["id"]}">{e(src["text"])} <a href="{e(src["url"])}" rel="noopener" target="_blank">{e(src["url"].replace("https://", ""))}</a></li>'
                   for src in a["sources"])
    related = [t for t in BLOG if t != topic and code in BLOG[t]][:3]
    rel_html = ""
    if related:
        cards = "".join(post_card(t, code, root) for t in related)
        rel_html = f'<section class="related"><h2>{e(u["related_title"])}</h2><div class="post-grid">{cards}</div></section>'

    out.append(f"""<div class="wrap">
  <header class="post-hero">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}{landing_path(code)}">Dotday</a> / <a href="{root}{blog_path(code)}">{e(u["nav_blog"])}</a></nav>
    <h1>{e(a["h1"])}</h1>
    <p class="post-lead">{e(a["lead"])}</p>
    <p class="post-meta"><span>{TOPIC_ICON.get(topic, "📖")} {e(u["min_read"].replace("{n}", str(a["read_min"])))}</span><span>{e(u["updated"])} {time_tag(modified)}</span><span>{e(u["sources_count"].replace("{n}", str(len(a["sources"]))))}</span></p>
  </header>
  <section class="facts" aria-label="{e(u["facts_title"])}"><h2 class="visually-hidden">{e(u["facts_title"])}</h2><ul>{facts}</ul></section>
  <div class="guide-layout post-layout">
    <aside class="toc"><h2>{e(u["toc"])}</h2><ol>{toc}</ol></aside>
    <article class="article post">
      {secs}
      <section id="faq"><h2>{e(u["faq_title"])}</h2><div class="faq">{faq}</div></section>
      <section id="sources" class="sources"><h2>{e(u["sources_title"])}</h2><p class="small">{e(u["sources_note"])}</p><ol>{srcs}</ol><p class="small">{e(u["disclaimer"])}</p></section>
      <div class="guide-cta"><div><h2>{e(a["cta_title"])}</h2><p>{e(a["cta_body"])}</p></div>{play_button(code, "blog-" + topic)}</div>
      {rel_html}
    </article>
  </div>
</div>
</main>""")
    out.append(footer(code, root))
    write(path + "index.html", "\n".join(out))


def post_card(topic, code, root):
    a = BLOG[topic][code]
    u = BLOG_UI[code]
    return (f'<a class="post-card" href="{root}{article_path(code, topic)}"><span class="ico" aria-hidden="true">{TOPIC_ICON.get(topic, "📖")}</span>'
            f'<h3>{e(a["h1"])}</h3><p>{e(a["lead"])}</p>'
            f'<span class="post-card-foot"><span>{e(u["min_read"].replace("{n}", str(a["read_min"])))}</span><span class="more">{e(u["read_more"])} →</span></span></a>')


def blog_index(code):
    u = BLOG_UI[code]
    path = blog_path(code)
    root = "../" * path.count("/")
    alternates = [(c, blog_path(c)) for c in BLOG_LANGS]
    topics = [t for t in BLOG if code in BLOG[t]]
    jsonld = [{"@context": "https://schema.org", "@type": "Blog", "name": u["blog_meta_title"], "description": u["blog_meta_desc"],
               "url": f"{SITE}/{path}", "inLanguage": code,
               "publisher": {"@type": "Organization", "name": "Dotday", "url": f"{SITE}/"},
               "blogPost": [{"@type": "BlogPosting", "headline": BLOG[t][code]["h1"], "url": f"{SITE}/{article_path(code, t)}",
                             "datePublished": BLOG[t][code]["published"]} for t in topics]}]
    out = [head(code, title=u["blog_meta_title"], desc=u["blog_meta_desc"], canonical=path, alternates=alternates,
                root=root, page="blog/", jsonld=jsonld),
           "<body>", header(code, root, page="blog/", alternates=alternates), '<main id="main">']
    cards = "".join(post_card(t, code, root) for t in topics)
    out.append(f"""<div class="wrap">
  <header class="guide-hero blog-hero">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}{landing_path(code)}">Dotday</a> / {e(u["nav_blog"])}</nav>
    <h1>{e(u["blog_h1"])}</h1>
    <p>{e(u["blog_lead"])}</p>
  </header>
  <div class="post-grid blog-grid">{cards}</div>
</div>
</main>""")
    out.append(footer(code, root))
    write(path + "index.html", "\n".join(out))


# ---------- Huquqiy sahifalar (mavjud fayllarni yangilash) ----------
LEGAL_MARK = "<!--dotday-head-->"


def patch_legal():
    for f in sorted(OUT.glob("*.html")):
        m = re.fullmatch(r"(privacy|terms)(?:-([A-Za-z-]+))?\.html", f.name)
        if not m:
            continue
        page, code = m.group(1), m.group(2) or "en"
        if code not in LANG:
            continue
        s = f.read_text("utf-8")
        s = re.sub(r"\s*" + re.escape(LEGAL_MARK) + r".*?" + re.escape(LEGAL_MARK), "", s, flags=re.S)
        alts = "".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}/{legal(page, c)}">' for c in LANG)
        block = (f'{LEGAL_MARK}<link rel="canonical" href="{SITE}/{f.name}">{alts}'
                 f'<link rel="alternate" hreflang="x-default" href="{SITE}/{page}.html">'
                 f'<meta name="color-scheme" content="light dark">{THEME_INIT}{LEGAL_MARK}')
        s = re.sub(r"\s*</head>", "\n" + block.replace("\\", "\\\\") + "\n</head>", s, count=1)
        s = s.replace("manrope.ttf", "manrope.woff2")
        s = re.sub(r'<a class="brand" href="[^"]*">', f'<a class="brand" href="{landing_path(code) or "./"}">', s, count=1)
        f.write_text(s, "utf-8")


# ---------- Qo'shimcha fayllar ----------
def extras():
    langs_js = {c: {"path": landing_path(c), "dir": LANG[c]["dir"], "msg": T[c]["suggest_msg"], "go": T[c]["suggest_go"],
                    "pages": (["guide/"] if c in GUIDES else []) + (["blog/"] if c in BLOG_LANGS else [])} for c in LANG}
    write("assets/langs.js", "window.DOTDAY_LANGS=" + json.dumps(langs_js, ensure_ascii=False, separators=(",", ":")) + ";\n")

    urls = []
    def add(group):
        for loc in group:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{SITE}/{p}"/>' for c, p in group)
            urls.append(f"<url><loc>{SITE}/{loc[1]}</loc><lastmod>{TODAY}</lastmod>{alts}</url>")
    add([(c, landing_path(c)) for c in LANG])
    add([(c, guide_path(c)) for c in GUIDES])
    if BLOG_LANGS:
        add([(c, blog_path(c)) for c in BLOG_LANGS])
    for topic in BLOG:
        add(blog_alternates(topic))
    add([(c, legal("privacy", c)) for c in LANG])
    add([(c, legal("terms", c)) for c in LANG])
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {SITE}/sitemap.xml\n")
    write("site.webmanifest", json.dumps({
        "name": "Dotday", "short_name": "Dotday", "start_url": "/", "display": "standalone",
        "background_color": "#fbfaff", "theme_color": "#4b4fe0",
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/assets/icon.svg", "sizes": "any", "type": "image/svg+xml"}],
        "related_applications": [{"platform": "play", "id": PACKAGE, "url": f"https://play.google.com/store/apps/details?id={PACKAGE}"}],
    }, indent=1) + "\n")

    t = T["en"]
    write("404.html", f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found — Dotday</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
{THEME_INIT}
</head>
<body>
<main class="wrap final" style="min-height:80vh;display:grid;place-content:center;padding:48px 20px">
  <img class="icon-big" src="/assets/icon.svg" alt="" width="88" height="88">
  <h1 style="font-size:clamp(32px,6vw,56px);letter-spacing:-.03em;margin:0 0 10px">404</h1>
  <p>This page doesn’t exist. · Sahifa topilmadi. · Страница не найдена.</p>
  <p><a class="btn btn-primary" href="/">Dotday →</a></p>
</main>
</body>
</html>
""")

    # /get/ — Instagram/Telegram ichki brauzeri play.google.com ni veb-sahifa sifatida ochadi;
    # intent:// va market:// esa Play Store ilovasini to'g'ridan-to'g'ri chaqiradi.
    # Kanal: /get/?s=telegram&m=post&c=kanal_nomi -> Play referrer utm_source/utm_medium/utm_campaign
    # (Play Console -> Store analysis -> UTM). Parametrsiz — Instagram bio.
    ref = "utm_source%3Dinstagram%26utm_medium%3Dbio"
    market = f"market://details?id={PACKAGE}&referrer={ref}"
    web = f"{PLAY}&referrer={ref}"
    redirect = f"""(function(){{
  var q=new URLSearchParams(location.search),c=function(k,d){{return (q.get(k)||d).replace(/[^\\w.-]/g,'').slice(0,40)}};
  var src=c('s','instagram'),ref='utm_source='+src+'&utm_medium='+c('m',src==='instagram'?'bio':'post');
  if(q.get('c'))ref+='&utm_campaign='+c('c','');
  ref=encodeURIComponent(ref);
  var id='{PACKAGE}',web={json.dumps(PLAY)}+'&referrer='+ref,market='market://details?id='+id+'&referrer='+ref;
  var intent='intent://details?id='+id+'&referrer='+ref+'#Intent;scheme=market;package=com.android.vending;S.browser_fallback_url='+encodeURIComponent(web)+';end';
  document.addEventListener('DOMContentLoaded',function(){{document.getElementById('m').href=market;document.getElementById('w').href=web}});
  location.replace(/android/i.test(navigator.userAgent)?intent:web);
}})()"""
    write("get/index.html", f"""<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dotday — Google Play</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
{THEME_INIT}
<script>{redirect}</script>
</head>
<body>
<main class="wrap final" style="min-height:80vh;display:grid;place-content:center;padding:48px 20px">
  <img class="icon-big" src="/assets/icon.svg" alt="" width="88" height="88">
  <h1 style="font-size:clamp(28px,5vw,44px);letter-spacing:-.03em;margin:0 0 10px">Dotday</h1>
  <p>Google Play ochilmasa, tugmani bosing. · Если Google Play не открылся, нажмите кнопку.</p>
  <p><a id="m" class="btn btn-primary" href="{e(market)}">Google Play →</a></p>
  <p><a id="w" href="{e(web)}">play.google.com</a></p>
</main>
</body>
</html>
""")


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, "utf-8")


def check():
    keys = set(T["en"])
    for c, t in T.items():
        missing = keys - set(t)
        assert not missing, f"{c}: {sorted(missing)} yetishmaydi"
        assert len(t["showcases"]) == len(T["en"]["showcases"]) and len(t["faq"]) == len(T["en"]["faq"]), c
        assert len(CAPTIONS[c]) == 8, c
    for c in GUIDES:
        assert c in LANG, c
    for c in BLOG_UI:
        assert set(BLOG_UI[c]) == set(BLOG_UI["en"]), f"blog/ui.json {c}"
    for c in BLOG_LANGS:
        slugs = [BLOG[t][c]["slug"] for t in BLOG if c in BLOG[t]]
        assert len(slugs) == len(set(slugs)), f"blog {c}: takroriy slug"
    for topic, arts in BLOG.items():
        if arts:
            assert "en" in arts, f"blog/{topic}: en.json kerak (x-default)"
        for c, a in arts.items():
            assert c in BLOG_UI, f"blog/ui.json: {c} yo'q"
            check_article(topic, c, a)
            en = arts["en"]
            where = f"blog/{topic}/{c}.json"
            assert a["sources"] == en["sources"], f"{where}: manbalar en.json bilan bir xil emas"
            assert [x["id"] for x in a["sections"]] == [x["id"] for x in en["sections"]], f"{where}: bo'limlar en.json bilan mos emas"
            assert [f["src"] for f in a["facts"]] == [f["src"] for f in en["facts"]], f"{where}: faktlar manbasi mos emas"
            refs = lambda art: [re.findall(r'href="#src-(\d+)"', x["html"]) for x in art["sections"]]
            assert refs(a) == refs(en), f"{where}: matndagi manba havolalari en.json bilan mos emas"
            assert len(a["faq"]) == len(en["faq"]), f"{where}: FAQ soni mos emas"


if __name__ == "__main__":
    check()
    for c in LANG:
        landing(c)
    for c in GUIDES:
        guide(c)
    for c in BLOG_LANGS:
        blog_index(c)
    for topic in BLOG:
        for c in BLOG[topic]:
            article_page(topic, c)
    patch_legal()
    extras()
    print(f"OK: {len(LANG)} landing, {len(GUIDES)} guide, {sum(len(a) for a in BLOG.values())} maqola ({len(BLOG_LANGS)} til)")

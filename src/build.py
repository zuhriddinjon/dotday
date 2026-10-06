#!/usr/bin/env python3
"""Dotday saytini yig'adi: src/i18n/*.json + src/guide/*.json -> statik HTML.

    python3 src/build.py

Natija repo ildiziga yoziladi (GitHub Pages `main` / root dan xizmat qiladi).
Barcha ichki havolalar nisbiy — sayt ham dotday.uz, ham github.io/dotday ostida ishlaydi.
"""
import datetime
import html
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
SITE = "https://dotday.uz"
PACKAGE = "uz.habitly.tracker"
EMAIL = "zuhriddinjonrayimjonov@gmail.com"
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
    return f"""<footer>
  <div class="wrap foot">
    <div>
      <a class="brand" href="{home}"><img src="{root}assets/icon.svg" alt="" width="34" height="34">Dotday</a>
      <p>{e(t["foot_tagline"])}</p>
      <p>© 2026 Dotday</p>
    </div>
    <div>
      <h3>{e(t["foot_app"])}</h3>
      <ul>
        <li><a href="{e(play_url(code, "footer"))}">Google Play</a></li>
        <li><a href="{root}{guide_path(guide_code)}">{e(t["nav_guide"])}</a></li>
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
             "logo": f"{SITE}/assets/icon-512.png", "email": EMAIL},
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
                    "pages": ["guide/"] if c in GUIDES else []} for c in LANG}
    write("assets/langs.js", "window.DOTDAY_LANGS=" + json.dumps(langs_js, ensure_ascii=False, separators=(",", ":")) + ";\n")

    urls = []
    def add(group):
        for loc in group:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{SITE}/{p}"/>' for c, p in group)
            urls.append(f"<url><loc>{SITE}/{loc[1]}</loc><lastmod>{TODAY}</lastmod>{alts}</url>")
    add([(c, landing_path(c)) for c in LANG])
    add([(c, guide_path(c)) for c in GUIDES])
    add([(c, legal("privacy", c)) for c in LANG])
    add([(c, legal("terms", c)) for c in LANG])
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {SITE}/sitemap.xml\n")
    write("site.webmanifest", json.dumps({
        "name": "Dotday", "short_name": "Dotday", "start_url": "/", "display": "standalone",
        "background_color": "#fbfaff", "theme_color": "#4b4fe0",
        "icons": [{"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
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


if __name__ == "__main__":
    check()
    for c in LANG:
        landing(c)
    for c in GUIDES:
        guide(c)
    patch_legal()
    extras()
    print(f"OK: {len(LANG)} landing, {len(GUIDES)} guide")

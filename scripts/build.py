#!/usr/bin/env python3
"""Build the static Sarawak.News hub."""

from __future__ import annotations

import html
import json
import re
import shutil
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DIST = ROOT / "dist"

# Live origin. Pages serves the site at the domain root. SITE_URL overrides this.
DEFAULT_SITE_URL = "https://sarawak.news/"

HEADLINE = "Sarawak, made easy."
DECK = "Explore Sarawak-focused sites, all in one place."
PAGE_TITLE = "Sarawak.News"
PHOTO_LICENCE = "https://creativecommons.org/licenses/by-sa/4.0/"
PHOTO_LICENCE_25 = "https://creativecommons.org/licenses/by-sa/2.5/"
# One line each for a shape that was traced. Other references are proportions only.
DRAWING_CREDITS = (
    (
        "The DUN is traced from a",
        "CEphoto (Uwe Aranas)",
        "https://commons.wikimedia.org/wiki/File:Kuching_Sarawak_Dewan-Undangan-Negeri-Sarawak-01.jpg",
        PHOTO_LICENCE,
        "CC BY-SA 4.0",
    ),
    (
        "The Darul Hana pylons are traced from a",
        "Meandkancil2020",
        "https://commons.wikimedia.org/wiki/File:Jambatan_Darul_Hana,_di_Bandaraya_Kuching.jpg",
        PHOTO_LICENCE,
        "CC BY-SA 4.0",
    ),
    (
        "Gunung Santubong is traced from a",
        "Matthew Anderson Lockhart",
        "https://commons.wikimedia.org/wiki/File:Mount_Santubong_from_Santubong_Bridge.jpg",
        PHOTO_LICENCE_25,
        "CC BY-SA 2.5",
    ),
)

# Published names, copied from design-handoff/favicon-F1/. The handoff folder itself stays unpublished.
FAVICON_FILES = {
    "favicon.ico": "favicon.ico",
    "favicon.svg": "f1.svg",
    "apple-touch-icon.png": "f1-180.png",
    "icon-512.png": "f1-512.png",
}


def site_url() -> str:
    import os

    raw = os.environ.get("SITE_URL", DEFAULT_SITE_URL).strip()
    if not raw:
        return ""
    return raw if raw.endswith("/") else raw + "/"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_sites(path: Path = DATA / "sites.json") -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sites = payload.get("sites")
    if not isinstance(sites, list) or not sites:
        raise SystemExit("data/sites.json needs a non-empty sites list")
    seen: set[str] = set()
    for site in sites:
        site_id = site.get("id")
        if not isinstance(site_id, str) or not re.fullmatch(r"[a-z0-9-]+", site_id):
            raise SystemExit(f"site id must be a lowercase slug, got {site_id!r}")
        if site_id in seen:
            raise SystemExit(f"duplicate site id: {site_id}")
        seen.add(site_id)
        for field in ("name", "url", "tag", "icon", "text"):
            if not isinstance(site.get(field), str) or not site[field].strip():
                raise SystemExit(f"{site_id} is missing {field}")
        icon = SITE / "icons" / f"{site['icon']}.svg"
        if not icon.is_file():
            raise SystemExit(f"{site_id} icon not found: {icon.relative_to(ROOT)}")
    return sites


def domain_of(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or url
    return host.removeprefix("www.")


def icon_inner(name: str, fill_class: str) -> str:
    raw = (SITE / "icons" / f"{name}.svg").read_text(encoding="utf-8").strip()
    return raw.replace('opacity="0.2"', f'class="{fill_class}" opacity="0.2"', 1)


def tile_icon(name: str) -> str:
    return (
        '<span class="group-icon-tile">'
        '<svg class="group-icon" viewBox="0 0 256 256" width="24" height="24" aria-hidden="true" focusable="false" fill="currentColor">'
        f"{icon_inner(name, 'group-icon-fill')}"
        "</svg></span>"
    )


def render_hero() -> str:
    art = (SITE / "hero-art.svg").read_text(encoding="utf-8").strip()
    if 'class="hero-art"' not in art or "aria-hidden" not in art:
        raise SystemExit("site/hero-art.svg is missing the decorative riverfront drawing")
    if "art-boat" in art:
        raise SystemExit("site/hero-art.svg still contains the tambang")
    return f"""<header class="brief">
      <h1>{esc(HEADLINE)}</h1>
      <p class="brief-deck">{esc(DECK)}</p>
      {art}
    </header>"""


def render_card(site: dict) -> str:
    return f"""<article class="hub-card" data-site="{esc(site["id"])}">
        <div class="hub-top">{tile_icon(site["icon"])}<span class="hub-pill">{esc(site["tag"])}</span></div>
        <h2 class="hub-name">{esc(site["name"])}</h2>
        <p class="hub-desc">{esc(site["text"])}</p>
        <p class="hub-foot"><a class="hub-visit" href="{esc(site["url"])}">Visit <span class="hub-arrow" aria-hidden="true">→</span></a></p>
      </article>"""


def theme_boot() -> str:
    return """  <script>
    document.documentElement.classList.add("js");
    try {
      const storedTheme = localStorage.getItem("sarawak-theme");
      if (storedTheme === "dark" || (storedTheme !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
        document.documentElement.dataset.theme = "dark";
      }
    } catch (error) {}
  </script>"""


def render_header(active: str) -> str:
    def link(page: str, href: str, label: str) -> str:
        current = ' aria-current="page"' if active == page else ""
        klass = "site-nav-link is-active" if active == page else "site-nav-link"
        return f'<a class="{klass}" href="{href}"{current}>{label}</a>'

    return f"""  <header class="bar">
    <div class="bar-inner">
    <span class="brand-lockup"><a class="brand" href="index.html">Sarawak.News</a></span>
    <nav class="site-nav" id="primary-navigation" aria-label="Primary">
      {link("sites", "index.html", "Sites")}
      {link("about", "about.html", "About")}
    </nav>
    <span class="bar-rule-tail" aria-hidden="true"></span>
    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="primary-navigation" aria-label="Open navigation" title="Open navigation">
      <span></span><span></span><span></span>
    </button>
    <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode" title="Switch to dark mode">
      <svg class="theme-icon-morph" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24">
        <mask id="theme-toggle-moon-mask"><rect width="24" height="24" fill="#fff"></rect><circle cx="17" cy="7" r="7" fill="#000"></circle></mask>
        <circle class="theme-icon-moon" cx="12" cy="12" r="9" mask="url(#theme-toggle-moon-mask)"></circle>
        <circle class="theme-icon-sun" cx="12" cy="12" r="5"></circle>
        <g class="theme-icon-rays">
          <line x1="12" y1="1.6" x2="12" y2="3.8"></line><line x1="12" y1="20.2" x2="12" y2="22.4"></line>
          <line x1="1.6" y1="12" x2="3.8" y2="12"></line><line x1="20.2" y1="12" x2="22.4" y2="12"></line>
          <line x1="4.6" y1="4.6" x2="6.2" y2="6.2"></line><line x1="17.8" y1="17.8" x2="19.4" y2="19.4"></line>
          <line x1="4.6" y1="19.4" x2="6.2" y2="17.8"></line><line x1="17.8" y1="6.2" x2="19.4" y2="4.6"></line>
        </g>
      </svg>
    </button>
    </div>
  </header>"""


def render_back_to_top() -> str:
    return """  <button class="back-to-top" type="button" data-back-to-top aria-label="Back to top" hidden><span class="back-to-top-label">Back to top</span> <span class="back-to-top-arrow" aria-hidden="true">↑</span></button>"""


def render_footer() -> str:
    return """  <footer class="site-footer">
    <div class="site-footer-bottom">
      <p>Built by <a class="site-footer-link site-footer-credit-link" href="https://hafiy.my">hafiy.my</a>, an independent publication. Not affiliated with the Sarawak Government.</p>
    </div>
  </footer>"""


def render_head(title: str, description: str, canonical: str) -> str:
    canonical_tag = f'\n  <link rel="canonical" href="{esc(canonical)}" />' if canonical else ""
    og_url = f'\n  <meta property="og:url" content="{esc(canonical)}" />' if canonical else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{esc(description)}" />
  <meta name="robots" content="index,follow" />
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:site_name" content="Sarawak.News" />{og_url}
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />{canonical_tag}
  <title>{esc(title)}</title>
  <link rel="icon" href="favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="favicon.ico" sizes="any" />
  <link rel="apple-touch-icon" href="apple-touch-icon.png" />
  <link rel="icon" href="icon-512.png" type="image/png" sizes="512x512" />
  <link rel="preload" href="fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin />
{theme_boot()}
  <link rel="stylesheet" href="style.css" />
  <script src="app.js" defer></script>
</head>"""


def render_home(sites: list[dict] | None = None) -> str:
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = url or ""
    description = DECK
    cards = "\n".join(render_card(site) for site in sites)
    body = f"""<body>
  <a class="skip-link" href="#content">Skip to content</a>
{render_header("sites")}
  <main id="content">
    {render_hero()}
    <section class="hub-grid" aria-label="Sites">
      {cards}
    </section>
  </main>
{render_footer()}
{render_back_to_top()}
</body>"""
    return render_head(PAGE_TITLE, description, canonical) + "\n" + body + "\n</html>\n"


def render_about(sites: list[dict] | None = None) -> str:
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = f"{url}about.html" if url else ""
    title = "About Sarawak.News"
    description = DECK
    sections = []
    for site in sites:
        sections.append(
            f"""    <section class="about-section" aria-labelledby="about-{esc(site["id"])}">
      <h2 id="about-{esc(site["id"])}">{esc(site["name"])}</h2>
      <p>{esc(site["text"])}</p>
      <p><a href="{esc(site["url"])}">{esc(domain_of(site["url"]))}</a></p>
    </section>"""
        )
    body = f"""<body>
  <a class="skip-link" href="#content">Skip to content</a>
{render_header("about")}
  <main id="content" class="about-page">
    <header class="about-hero">
      <h1>About Sarawak.News</h1>
      <p class="about-lede">{esc(HEADLINE)} {esc(DECK)}</p>
    </header>
{chr(10).join(sections)}
    <section class="about-section" aria-labelledby="about-independence">
      <h2 id="about-independence">Independence</h2>
      <p>Built by <a href="https://hafiy.my">hafiy.my</a>, an independent publication. Not affiliated with the Sarawak Government.</p>
    </section>
    <div class="about-credits">
      {"".join(
          f'<p class="about-credit">{esc(lead)} <a href="{esc(photo)}">reference photo</a> by {esc(author)}, <a href="{esc(licence)}">{esc(name)}</a>.</p>'
          for lead, author, photo, licence, name in DRAWING_CREDITS
      )}
    </div>
  </main>
{render_footer()}
{render_back_to_top()}
</body>"""
    return render_head(title, description, canonical) + "\n" + body + "\n</html>\n"


def write_dist(home: str, about: str, dist: Path = DIST) -> None:
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    (dist / "index.html").write_text(home, encoding="utf-8")
    (dist / "about.html").write_text(about, encoding="utf-8")
    shutil.copy2(SITE / "style.css", dist / "style.css")
    shutil.copy2(SITE / "app.js", dist / "app.js")
    fonts = dist / "fonts"
    fonts.mkdir()
    woff = SITE / "fonts" / "Geist-Variable.woff2"
    license_file = SITE / "fonts" / "OFL.txt"
    if not woff.is_file() or not license_file.is_file():
        raise SystemExit("site/fonts must contain Geist-Variable.woff2 and OFL.txt")
    shutil.copy2(woff, fonts / woff.name)
    shutil.copy2(license_file, fonts / license_file.name)
    handoff = ROOT / "design-handoff" / "favicon-F1"
    for dest_name, src_name in FAVICON_FILES.items():
        src = handoff / src_name
        if not src.is_file():
            raise SystemExit(f"missing favicon source {src.relative_to(ROOT)}")
        shutil.copy2(src, dist / dest_name)
    cname = ROOT / "CNAME"
    if not cname.is_file():
        raise SystemExit("CNAME is missing; Pages needs it in the published output")
    (dist / "CNAME").write_text(cname.read_text(encoding="utf-8"), encoding="utf-8")
    url = site_url()
    sitemap_loc = f"Sitemap: {url}sitemap.xml\n" if url else ""
    (dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\n{sitemap_loc}", encoding="utf-8")
    if url:
        entries = "\n".join(
            f"  <url><loc>{esc(loc)}</loc></url>" for loc in (url, f"{url}about.html")
        )
        (dist / "sitemap.xml").write_text(
            "<?xml version='1.0' encoding='UTF-8'?>\n"
            "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
            f"{entries}\n"
            "</urlset>\n",
            encoding="utf-8",
        )


def build() -> None:
    sites = load_sites()
    home = render_home(sites)
    about = render_about(sites)
    for banned in ("PCDS", "pcds2030", "brief-net", "hub-meta"):
        if banned in home or banned in about:
            raise SystemExit(f"Banned marker in build output: {banned}")
    write_dist(home, about)


def main() -> None:
    build()
    print(f"Built {DIST / 'index.html'}")


if __name__ == "__main__":
    main()

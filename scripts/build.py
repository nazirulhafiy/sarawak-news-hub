#!/usr/bin/env python3
"""Build the static Sarawak.News hub.

Counts are fetched from the live sites at build time. A failed fetch keeps the
last known values in data/counts.json and does not fail the build.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DIST = ROOT / "dist"

AI_URL = "https://ai.sarawak.news/"
BANTUAN_URL = "https://bantuan.sarawak.news/"
BANTUAN_SCHEMES_URL = "https://bantuan.sarawak.news/schemes.json"
USER_AGENT = "sarawak-news-hub-build/1.0"
TIMEOUT = 20

# GitHub Pages project URL until Nazirul approves the sarawak.news hostname.
# Override with SITE_URL. Do not write a CNAME.
DEFAULT_SITE_URL = "https://nazirulhafiy.github.io/sarawak-news-hub/"

# Tile centres in the Natural Earth path's viewBox (0 0 614.7 411.1).
# Southwest coast: AI. North coast: Bantuan. Joined by a dotted curve.
AI_TILE = (128.0, 348.0)
BANTUAN_TILE = (424.0, 128.0)
ROUTE_BOW = 26.0

HEADLINE = "Independent Sarawak sites, in one place."
DECK = "Each site links to its sources."

SITES = (
    {
        "key": "ai",
        "name": "AI.Sarawak.News",
        "domain": "ai.sarawak.news",
        "url": "https://ai.sarawak.news/",
        "kind": "News",
        "icon": "brain",
        "desc": "Source-linked coverage across policy, public services, education, workforce, research, infrastructure and business.",
    },
    {
        "key": "bantuan",
        "name": "Bantuan.Sarawak.News",
        "domain": "bantuan.sarawak.news",
        "url": "https://bantuan.sarawak.news/",
        "kind": "Directory",
        "icon": "hand-heart",
        "desc": "An independent directory of Sarawak government assistance. Every scheme links to an official page.",
    },
)


def site_url() -> str:
    import os

    raw = os.environ.get("SITE_URL", DEFAULT_SITE_URL).strip()
    if not raw:
        return ""
    return raw if raw.endswith("/") else raw + "/"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_counts(path: Path = DATA / "counts.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_counts(counts: dict, path: Path = DATA / "counts.json") -> None:
    text = json.dumps(counts, indent=2, ensure_ascii=False) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8")


def http_get(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _updated(page: str) -> str:
    match = re.search(
        r'class="updated"[\s\S]*?<time datetime="(\d{4}-\d{2}-\d{2})"',
        page,
    )
    if not match:
        raise ValueError("updated date not found")
    return match.group(1)


def parse_ai(page: str) -> dict:
    stories = len(re.findall(r"<article\b", page))
    filters = re.findall(r'data-section-filter="([^"]+)"', page)
    categories = [name for name in filters if name != "all"]
    # Preserve order, drop duplicates.
    seen: list[str] = []
    for name in categories:
        if name not in seen:
            seen.append(name)
    badge = re.search(
        r'data-section-filter="all"[\s\S]*?category-filter-count[^>]*>\s*(\d+)',
        page,
    )
    if stories < 1 or not seen:
        raise ValueError("ai.sarawak.news page is missing stories or categories")
    if badge and int(badge.group(1)) != stories:
        raise ValueError(
            f"ai story count {stories} does not match the All badge {badge.group(1)}"
        )
    return {"stories": stories, "categories": len(seen), "updated": _updated(page)}


def parse_bantuan(schemes_payload: str, page: str) -> dict:
    schemes = json.loads(schemes_payload)
    if not isinstance(schemes, list) or not schemes:
        raise ValueError("bantuan schemes.json is empty")
    groups = {item.get("group") for item in schemes if isinstance(item, dict) and item.get("group")}
    if not groups:
        raise ValueError("bantuan schemes.json has no categories")
    return {
        "schemes": len(schemes),
        "categories": len(groups),
        "updated": _updated(page),
    }


def refresh_counts(previous: dict, getter=http_get) -> tuple[dict, list[str]]:
    """Return counts and human-readable notes. Fetch failures keep previous values."""
    counts = json.loads(json.dumps(previous))
    notes: list[str] = []

    try:
        ai = parse_ai(getter(AI_URL))
        counts["ai"] = ai
        notes.append(
            f"ai.sarawak.news: {ai['stories']} stories, {ai['categories']} categories, updated {ai['updated']} (homepage HTML)"
        )
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as error:
        kept = counts["ai"]
        notes.append(
            f"ai.sarawak.news: fetch failed ({error}); keeping {kept['stories']} stories, {kept['categories']} categories, updated {kept['updated']}"
        )

    try:
        bantuan = parse_bantuan(getter(BANTUAN_SCHEMES_URL), getter(BANTUAN_URL))
        counts["bantuan"] = bantuan
        notes.append(
            f"bantuan.sarawak.news: {bantuan['schemes']} schemes, {bantuan['categories']} categories, updated {bantuan['updated']} (schemes.json + homepage HTML)"
        )
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as error:
        kept = counts["bantuan"]
        notes.append(
            f"bantuan.sarawak.news: fetch failed ({error}); keeping {kept['schemes']} schemes, {kept['categories']} categories, updated {kept['updated']}"
        )

    return counts, notes


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def meta_line(counts: dict, key: str) -> str:
    item = counts[key]
    if key == "ai":
        left = _plural(item["stories"], "story", "stories")
    else:
        left = _plural(item["schemes"], "scheme", "schemes")
    right = _plural(item["categories"], "category", "categories")
    return f"{left} · {right}"


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


def hero_route(start: tuple[float, float], end: tuple[float, float]) -> str:
    ax, ay = start
    bx, by = end
    dx, dy = bx - ax, by - ay
    length = (dx * dx + dy * dy) ** 0.5
    # Bow northwest of the chord so the dotted line follows the coast side.
    px, py = dy / length, -dx / length
    cx = (ax + bx) / 2 + px * ROUTE_BOW
    cy = (ay + by) / 2 + py * ROUTE_BOW
    return f"M{ax:.1f} {ay:.1f} Q {cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}"


def hero_node(name: str, centre: tuple[float, float]) -> str:
    x, y = centre
    return (
        f'<g class="hero-node" transform="translate({x:.1f} {y:.1f})">'
        '<rect class="hero-tile" x="-36" y="-36" width="72" height="72" rx="16"/>'
        '<svg class="hero-icon" x="-21" y="-21" width="42" height="42" viewBox="0 0 256 256" fill="currentColor">'
        f"{icon_inner(name, 'hero-icon-fill')}"
        "</svg></g>"
    )


def render_hero() -> str:
    outline = (DATA / "sarawak-path.txt").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[MLZ0-9.\- ]+", outline):
        raise SystemExit("data/sarawak-path.txt is not a plain SVG path")
    route = hero_route(AI_TILE, BANTUAN_TILE)
    return f"""<header class="brief">
      <div class="brief-copy">
        <h1>Independent<br>Sarawak sites,<br>in one place.</h1>
        <p class="brief-deck">{esc(DECK)}</p>
      </div>
      <div class="brief-map">
        <svg class="hero-map" viewBox="0 0 614.7 411.1" role="img" aria-label="Outline of Sarawak, with AI.Sarawak.News and Bantuan.Sarawak.News marked">
          <path class="hero-land" d="{outline}"/>
          <path class="hero-route" d="{route}"/>
          {hero_node("brain", AI_TILE)}
          {hero_node("hand-heart", BANTUAN_TILE)}
        </svg>
      </div>
    </header>"""


def render_card(site: dict, counts: dict) -> str:
    return f"""<article class="hub-card">
        <div class="hub-top">{tile_icon(site["icon"])}<span class="hub-pill">{esc(site["kind"])}</span></div>
        <h2 class="hub-name">{esc(site["name"])}</h2>
        <p class="hub-meta">{esc(meta_line(counts, site["key"]))}</p>
        <p class="hub-desc">{esc(site["desc"])}</p>
        <p class="hub-foot"><span class="hub-domain">{esc(site["domain"])}</span><a class="hub-visit" href="{esc(site["url"])}">Visit <span class="hub-arrow" aria-hidden="true">→</span></a></p>
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
  </header>"""


def render_footer() -> str:
    return """  <footer class="site-footer">
    <div class="site-footer-bottom">
      <p>Built by <a class="site-footer-link site-footer-credit-link" href="https://hafiy.my">hafiy.my</a>, an independent publication. Not affiliated with the Sarawak Government.</p>
      <p class="map-credit">Map: <a href="https://www.naturalearthdata.com/">Natural Earth</a></p>
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
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:site_name" content="Sarawak.News" />{og_url}
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />{canonical_tag}
  <title>{esc(title)}</title>
  <link rel="preload" href="fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin />
{theme_boot()}
  <link rel="stylesheet" href="style.css" />
  <script src="app.js" defer></script>
</head>"""


def render_home(counts: dict) -> str:
    url = site_url()
    canonical = url or ""
    description = "Each site links to its sources."
    cards = "\n".join(render_card(site, counts) for site in SITES)
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
</body>"""
    return render_head(HEADLINE, description, canonical) + "\n" + body + "\n</html>\n"


def render_about() -> str:
    url = site_url()
    canonical = f"{url}about.html" if url else ""
    title = "About Sarawak.News"
    description = f"{HEADLINE} {DECK}"
    sections = []
    for site in SITES:
        sections.append(
            f"""    <section class="about-section" aria-labelledby="about-{esc(site["key"])}">
      <h2 id="about-{esc(site["key"])}">{esc(site["name"])}</h2>
      <p>{esc(site["desc"])}</p>
      <p><a href="{esc(site["url"])}">{esc(site["domain"])}</a></p>
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
  </main>
{render_footer()}
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


def build(fetch: bool = True, getter=http_get) -> list[str]:
    previous = load_counts()
    if fetch:
        counts, notes = refresh_counts(previous, getter)
        save_counts(counts)
    else:
        counts, notes = previous, ["counts: using data/counts.json (fetch skipped)"]
    home = render_home(counts)
    about = render_about()
    for banned in ("PCDS", "pcds2030", "brief-net"):
        if banned in home or banned in about:
            raise SystemExit(f"Banned marker in build output: {banned}")
    write_dist(home, about)
    return notes


def main() -> None:
    for note in build():
        print(note)
    print(f"Built {DIST / 'index.html'}")


if __name__ == "__main__":
    main()

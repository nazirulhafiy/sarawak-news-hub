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
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DIST = ROOT / "dist"

USER_AGENT = "sarawak-news-hub-build/1.0"
TIMEOUT = 20

# Live origin. Pages serves the site at the domain root. SITE_URL overrides this.
DEFAULT_SITE_URL = "https://sarawak.news/"

HEADLINE = "Independent Sarawak sites, in one place."
DECK = "Each site links to its sources."

COUNT_SOURCES = ("html-stories", "schemes-json")


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
        counts = site.get("counts") or {}
        if counts.get("via") not in COUNT_SOURCES:
            raise SystemExit(f"{site_id} counts.via must be one of {', '.join(COUNT_SOURCES)}")
        for noun in ("noun", "groupNoun"):
            pair = counts.get(noun)
            if not (isinstance(pair, list) and len(pair) == 2 and all(isinstance(part, str) for part in pair)):
                raise SystemExit(f"{site_id} counts.{noun} must be [singular, plural]")
        if not isinstance(counts.get("page"), str):
            raise SystemExit(f"{site_id} counts.page is required")
        if counts["via"] == "schemes-json" and not isinstance(counts.get("json"), str):
            raise SystemExit(f"{site_id} counts.json is required for schemes-json")
    return sites


def domain_of(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or url
    return host.removeprefix("www.")


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
    return {"count": stories, "categories": len(seen), "updated": _updated(page)}


def parse_bantuan(schemes_payload: str, page: str) -> dict:
    schemes = json.loads(schemes_payload)
    if not isinstance(schemes, list) or not schemes:
        raise ValueError("schemes.json is empty")
    groups = {item.get("group") for item in schemes if isinstance(item, dict) and item.get("group")}
    if not groups:
        raise ValueError("schemes.json has no categories")
    return {
        "count": len(schemes),
        "categories": len(groups),
        "updated": _updated(page),
    }


def fetch_site_counts(site: dict, getter=http_get) -> dict:
    spec = site["counts"]
    if spec["via"] == "html-stories":
        return parse_ai(getter(spec["page"]))
    if spec["via"] == "schemes-json":
        return parse_bantuan(getter(spec["json"]), getter(spec["page"]))
    raise ValueError(f"unknown counts.via {spec['via']}")


def _count_phrase(site: dict, item: dict) -> str:
    noun = site["counts"]["noun"][1]
    group = site["counts"]["groupNoun"][1]
    return f"{item['count']} {noun}, {item['categories']} {group}, updated {item['updated']}"


def refresh_counts(previous: dict, getter=http_get, sites: list[dict] | None = None) -> tuple[dict, list[str]]:
    """Return counts and notes. A failed fetch keeps that site's last known values."""
    sites = load_sites() if sites is None else sites
    counts: dict = {}
    notes: list[str] = []
    for site in sites:
        site_id = site["id"]
        try:
            fetched = fetch_site_counts(site, getter)
            counts[site_id] = fetched
            notes.append(f"{domain_of(site['url'])}: {_count_phrase(site, fetched)} ({site['counts']['via']})")
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as error:
            if site_id not in previous:
                raise RuntimeError(
                    f"{site_id}: fetch failed ({error}) and data/counts.json has no fallback"
                ) from error
            counts[site_id] = previous[site_id]
            notes.append(
                f"{domain_of(site['url'])}: fetch failed ({error}); keeping {_count_phrase(site, previous[site_id])}"
            )
    return counts, notes


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def meta_line(site: dict, counts: dict) -> str:
    item = counts[site["id"]]
    noun = site["counts"]["noun"]
    group = site["counts"]["groupNoun"]
    left = _plural(item["count"], noun[0], noun[1])
    right = _plural(item["categories"], group[0], group[1])
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


def render_hero() -> str:
    outline = (DATA / "sarawak-path.txt").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[MLZ0-9.\- ]+", outline):
        raise SystemExit("data/sarawak-path.txt is not a plain SVG path")
    return f"""<header class="brief">
      <div class="brief-copy">
        <h1>Independent<br>Sarawak sites,<br>in one place.</h1>
        <p class="brief-deck">{esc(DECK)}</p>
      </div>
      <div class="brief-map">
        <svg class="hero-map" viewBox="0 0 614.7 411.1" aria-hidden="true">
          <path class="hero-land" d="{outline}"/>
        </svg>
      </div>
    </header>"""


def render_card(site: dict, counts: dict) -> str:
    return f"""<article class="hub-card" data-site="{esc(site["id"])}">
        <div class="hub-top">{tile_icon(site["icon"])}<span class="hub-pill">{esc(site["tag"])}</span></div>
        <h2 class="hub-name">{esc(site["name"])}</h2>
        <p class="hub-meta">{esc(meta_line(site, counts))}</p>
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


def render_home(counts: dict, sites: list[dict] | None = None) -> str:
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = url or ""
    description = "Each site links to its sources."
    cards = "\n".join(render_card(site, counts) for site in sites)
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


def render_about(sites: list[dict] | None = None) -> str:
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = f"{url}about.html" if url else ""
    title = "About Sarawak.News"
    description = f"{HEADLINE} {DECK}"
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


def build(fetch: bool = True, getter=http_get) -> list[str]:
    sites = load_sites()
    previous = load_counts()
    if fetch:
        counts, notes = refresh_counts(previous, getter, sites)
        save_counts(counts)
    else:
        counts, notes = previous, ["counts: using data/counts.json (fetch skipped)"]
    home = render_home(counts, sites)
    about = render_about(sites)
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

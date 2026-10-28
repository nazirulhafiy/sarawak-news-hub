#!/usr/bin/env python3
"""Build the static hub at sarawak.news."""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DIST = ROOT / "dist"
SITE_META_PATH = DATA / "site.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kit.python.analytics_loader import (  # noqa: E402
    ANALYTICS_LOADER_ATTR,
    render_analytics_loader as kit_render_analytics_loader,
)
from kit.python.analytics_registry import AnalyticsRegistry, load_analytics  # noqa: E402
from kit.python.asset_urls import versioned_href  # noqa: E402
from kit.python.shell import (  # noqa: E402
    NavItem,
    render_back_to_top,
    render_footer as kit_render_footer,
    render_header as kit_render_header,
)

# Live origin. Pages serves the site at the domain root. SITE_URL overrides this.
DEFAULT_SITE_URL = "https://sarawak.news/"

# Site title, tagline, description, and About lead live only in data/site.json.
SITE_COPY_FIELDS = ("title", "tagline", "description", "about_lead")

# Published names, copied from design-handoff/favicon-F1/. The handoff folder itself stays unpublished.
FAVICON_FILES = {
    "favicon.ico": "favicon.ico",
    "favicon.svg": "favicon.svg",
    "apple-touch-icon.png": "apple-touch-icon.png",
    "icon-192.png": "icon-192.png",
    "icon-512.png": "icon-512.png",
}

def versioned_icon(public_name: str) -> str:
    src_name = FAVICON_FILES[public_name]
    return versioned_href(public_name, ROOT / "design-handoff" / "favicon-F1" / src_name)


def analytics_registry() -> AnalyticsRegistry:
    return load_analytics()


# Resolved once at import for tests that still read module-level names.
_ANALYTICS = analytics_registry()
GA_MEASUREMENT_ID = _ANALYTICS.primary_ga4_id()
CLOUDFLARE_WEB_ANALYTICS_TOKEN = _ANALYTICS.primary_cf_token()
GA_PRODUCTION_HOSTS = _ANALYTICS.hostnames
GA_INTERNAL_COOKIE = _ANALYTICS.internal_cookie


def render_analytics_loader(registry: AnalyticsRegistry | None = None) -> str:
    """Emit the shared kit analytics loader from ``data/analytics.json``."""
    return kit_render_analytics_loader(registry if registry is not None else analytics_registry())

def site_url() -> str:
    import os

    raw = os.environ.get("SITE_URL", DEFAULT_SITE_URL).strip()
    if not raw:
        return ""
    return raw if raw.endswith("/") else raw + "/"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_site(path: Path = SITE_META_PATH) -> dict[str, str]:
    """Load hub title/tagline/description/about_lead from data/site.json."""
    if not path.is_file():
        raise SystemExit(f"missing site copy file: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("data/site.json must be an object")
    site: dict[str, str] = {}
    for field in SITE_COPY_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"data/site.json is missing {field}")
        site[field] = value.strip()
    expected_lead = f"{site['tagline']} {site['description']}"
    if site["about_lead"] != expected_lead:
        raise SystemExit(
            "data/site.json about_lead must equal tagline + space + description"
        )
    return site


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


def ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


def sitemap_lastmod() -> str:
    """YYYY-MM-DD from the newest mtime among hub content JSON files."""
    newest = max(
        (DATA / "site.json").stat().st_mtime,
        (DATA / "sites.json").stat().st_mtime,
    )
    from datetime import datetime, timezone

    return datetime.fromtimestamp(newest, tz=timezone.utc).date().isoformat()


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


def render_hero(site: dict[str, str] | None = None) -> str:
    site = load_site() if site is None else site
    art = (SITE / "hero-art.svg").read_text(encoding="utf-8").strip()
    if 'class="hero-art"' not in art or "aria-hidden" not in art:
        raise SystemExit("site/hero-art.svg is missing the decorative riverfront drawing")
    if "art-boat" in art:
        raise SystemExit("site/hero-art.svg still contains the tambang")
    return f"""<header class="brief">
      <h1>{esc(site["tagline"])}</h1>
      <p class="brief-deck">{esc(site["description"])}</p>
      <p class="brief-about"><a href="about.html">About this hub</a></p>
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


def render_header(active: str, site: dict[str, str] | None = None) -> str:
    site = load_site() if site is None else site
    return kit_render_header(
        brand_title=site["title"],
        brand_href="index.html",
        active=active,
        nav_items=(
            NavItem("sites", "index.html", "Sites"),
            NavItem("about", "about.html", "About"),
        ),
    )


def render_footer(active_page: str, site: dict[str, str] | None = None) -> str:
    site = load_site() if site is None else site
    return kit_render_footer(
        brand_title=site["title"],
        brand_note=site["description"],
        active=active_page,
        explore_items=(
            NavItem("home", "index.html", "Home"),
            NavItem("about", "about.html", "About"),
        ),
        fleet_site="hub",
        layout="column_stacks",
        fleet_section_label="Hub",
    )


def render_head(
    title: str,
    description: str,
    canonical: str,
    site: dict[str, str] | None = None,
) -> str:
    site = load_site() if site is None else site
    canonical_tag = f'\n  <link rel="canonical" href="{esc(canonical)}" />' if canonical else ""
    og_url = f'\n  <meta property="og:url" content="{esc(canonical)}" />' if canonical else ""
    url = site_url()
    image_href = f"{url}og.png" if url else "og.png"
    image = versioned_href(image_href, SITE / "og.png")
    icon_svg = versioned_icon("favicon.svg")
    icon_ico = versioned_icon("favicon.ico")
    icon_apple = versioned_icon("apple-touch-icon.png")
    icon_192 = versioned_icon("icon-192.png")
    icon_512 = versioned_icon("icon-512.png")
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
  <meta property="og:site_name" content="{esc(site["title"])}" />{og_url}
  <meta property="og:image" content="{esc(image)}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{esc(image)}" />{canonical_tag}
  <title>{esc(title)}</title>
  <link rel="icon" href="{esc(icon_svg)}" type="image/svg+xml" />
  <link rel="icon" href="{esc(icon_ico)}" sizes="any" />
  <link rel="apple-touch-icon" href="{esc(icon_apple)}" />
  <link rel="icon" href="{esc(icon_192)}" type="image/png" sizes="192x192" />
  <link rel="icon" href="{esc(icon_512)}" type="image/png" sizes="512x512" />
  <link rel="preload" href="fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin />
{theme_boot()}
  <link rel="stylesheet" href="style.css" />
  <script src="app.js" defer></script>
  {render_analytics_loader()}
</head>"""


def render_home(sites: list[dict] | None = None) -> str:
    copy = load_site()
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = url or ""
    description = copy["description"]
    cards = "\n".join(render_card(site) for site in sites)
    body = f"""<body>
  <a class="skip-link" href="#content">Skip to content</a>
{render_header("sites", copy)}
  <main id="content">
    {render_hero(copy)}
    <section class="hub-grid" aria-label="Sites">
      {cards}
    </section>
  </main>
{render_footer("home", copy)}
{render_back_to_top()}
</body>"""
    return render_head(copy["title"], description, canonical, copy) + "\n" + body + "\n</html>\n"


def render_about(sites: list[dict] | None = None) -> str:
    copy = load_site()
    sites = load_sites() if sites is None else sites
    url = site_url()
    canonical = f"{url}about.html" if url else ""
    title = f"About {copy['title']}"
    description = copy["description"]
    sections = []
    for site in sites:
        home = ensure_trailing_slash(site["url"])
        about = f"{home}about.html"
        sections.append(
            f"""    <section class="about-section" aria-labelledby="about-{esc(site["id"])}">
      <h2 id="about-{esc(site["id"])}">{esc(site["name"])}</h2>
      <p>{esc(site["text"])}</p>
      <p><a href="{esc(home)}">{esc(domain_of(home))}</a> · <a href="{esc(about)}">About</a></p>
    </section>"""
        )
    body = f"""<body>
  <a class="skip-link" href="#content">Skip to content</a>
{render_header("about", copy)}
  <main id="content" class="about-page">
    <header class="about-hero">
      <h1>{esc(title)}</h1>
      <p class="about-lede">{esc(copy["about_lead"])}</p>
    </header>
{chr(10).join(sections)}
    <section class="about-section" aria-labelledby="about-independence">
      <h2 id="about-independence">Independence</h2>
      <p>Built by <a href="https://hafiy.my">hafiy.my</a>, an independent publication. Not affiliated with the Sarawak Government.</p>
    </section>
  </main>
{render_footer("about", copy)}
{render_back_to_top()}
</body>"""
    return render_head(title, description, canonical, copy) + "\n" + body + "\n</html>\n"


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
    icons_dist = dist / "icons"
    icons_dist.mkdir()
    for mark_name in ("nav-mark-transparent.svg", "nav-mark-transparent-dark.svg"):
        mark_src = ROOT / "kit" / "assets" / "icons" / mark_name
        if not mark_src.is_file():
            raise SystemExit(f"missing nav mark {mark_src.relative_to(ROOT)}")
        shutil.copy2(mark_src, icons_dist / mark_name)
    handoff = ROOT / "design-handoff" / "favicon-F1"
    for dest_name, src_name in FAVICON_FILES.items():
        src = handoff / src_name
        if not src.is_file():
            raise SystemExit(f"missing favicon source {src.relative_to(ROOT)}")
        shutil.copy2(src, dist / dest_name)
    og = SITE / "og.png"
    if not og.is_file():
        raise SystemExit("site/og.png is missing")
    shutil.copy2(og, dist / "og.png")
    cname = ROOT / "CNAME"
    if not cname.is_file():
        raise SystemExit("CNAME is missing; Pages needs it in the published output")
    (dist / "CNAME").write_text(cname.read_text(encoding="utf-8"), encoding="utf-8")
    url = site_url()
    sitemap_loc = f"Sitemap: {url}sitemap.xml\n" if url else ""
    (dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\n{sitemap_loc}", encoding="utf-8")
    if url:
        lastmod = sitemap_lastmod()
        entries = "\n".join(
            f"  <url>\n    <loc>{esc(loc)}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>"
            for loc in (url, f"{url}about.html")
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

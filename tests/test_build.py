#!/usr/bin/env python3
"""Build and docs-check tests. No network."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.build as build
import scripts.docs_check_pr as docs_check


def site_copy() -> dict[str, str]:
    return build.load_site()


# Fixture only. Not an entry in data/sites.json.
DUMMY_SITE = {
    "id": "dummy",
    "name": "Dummy.Sarawak.News",
    "url": "https://dummy.example/",
    "tag": "Example",
    "icon": "brain",
    "text": "A fixture site used only by the test.",
}


class RenderTests(unittest.TestCase):
    def test_home_has_two_cards_and_hero(self):
        copy = site_copy()
        home = build.render_home()
        self.assertIn(f"<h1>{copy['tagline']}</h1>", home)
        self.assertNotIn("Sarawak News made easy", home)
        self.assertIn(
            f'<meta name="description" content="{copy["description"]}" />',
            home,
        )
        self.assertIn(
            f'<meta property="og:description" content="{copy["description"]}" />',
            home,
        )
        self.assertIn(
            f'<meta name="twitter:description" content="{copy["description"]}" />',
            home,
        )
        self.assertNotIn("Independent Sarawak sites", home)
        self.assertIn('class="hero-art"', home)
        self.assertIn('aria-hidden="true"', home)
        self.assertIn('class="dun"', home)
        self.assertIn('class="art-sun"', home)
        self.assertIn('class="art-peak"', home)
        self.assertIn('class="art-mast"', home)
        self.assertNotIn("art-boat", home)
        self.assertNotIn("hero-map", home)
        self.assertNotIn("hero-land", home)
        self.assertNotIn("brief-map", home)
        self.assertNotIn("<br>", home)
        self.assertIn(
            f'<p class="brief-deck">{copy["description"]}</p>',
            home,
        )
        self.assertNotIn("Explore Sarawak-focused sites", home)
        self.assertNotIn("Each site links to its sources.", home)
        self.assertIn('class="site-footer-main site-footer-main--column-stacks"', home)
        self.assertIn('<nav aria-label="Hub" class="site-footer-fleet-nav">', home)
        self.assertIn(
            '<nav aria-label="Explore" class="site-footer-nav site-footer-grid-explore">',
            home,
        )
        self.assertIn('<h2>Explore</h2>', home)
        self.assertIn(
            '<a class="site-footer-link" href="index.html" aria-current="page">Home</a>',
            home,
        )
        self.assertIn('<a class="site-footer-link" href="about.html">About</a>', home)
        self.assertIn(
            '<a class="site-footer-link" href="mailto:contact@sarawak.news">Contact</a>',
            home,
        )
        self.assertIn(f"<title>{copy['title']}</title>", home)
        self.assertIn(f'<meta property="og:title" content="{copy["title"]}" />', home)
        self.assertIn(f'<meta name="twitter:title" content="{copy["title"]}" />', home)
        self.assertNotIn("<title>Independent", home)
        # Site cards keep full brand names from data/sites.json.
        self.assertIn("AI.Sarawak.News", home)
        self.assertIn("Bantuan.Sarawak.News", home)
        self.assertIn("Events.Sarawak.News", home)
        # Footer fleet ul uses short labels only.
        fleet_ul = home.split(
            '<nav aria-label="Hub" class="site-footer-fleet-nav">', 1
        )[1].split("</nav>", 1)[0]
        self.assertIn(">AI</a>", fleet_ul)
        self.assertIn(">Events</a>", fleet_ul)
        self.assertIn(">Bantuan</a>", fleet_ul)
        # Hub omits its own fleet entry (label Sarawak lives in JSON for sisters).
        self.assertNotIn("https://sarawak.news/", fleet_ul)
        self.assertNotIn(">Sarawak</a>", fleet_ul)
        # Avoid contiguous hub title string (site-copy gate).
        self.assertNotIn("Sarawak" + ".News", fleet_ul)
        self.assertNotIn("AI.Sarawak.News", fleet_ul)
        self.assertNotIn("Events.Sarawak.News", fleet_ul)
        self.assertNotIn("Bantuan.Sarawak.News", fleet_ul)
        self.assertNotIn("hub-meta", home)
        self.assertNotIn("stories", home)
        self.assertNotIn("schemes", home)
        self.assertNotIn("categories", home)
        self.assertIn('href="https://ai.sarawak.news/"', home)
        self.assertIn('href="https://bantuan.sarawak.news/"', home)
        self.assertIn('href="https://events.sarawak.news/"', home)
        self.assertIn(">Calendar<", home)
        self.assertNotIn('class="hub-domain"', home)
        self.assertEqual(home.count(">Visit <"), 3)
        self.assertNotIn("hero-route", home)
        self.assertNotIn("hero-node", home)
        self.assertNotIn("hero-tile", home)
        self.assertIn("Built by ", home)
        self.assertIn("hafiy.my", home)
        self.assertNotIn("Map:", home)
        self.assertNotIn("Natural Earth", home)
        self.assertNotIn("map-credit", home)
        self.assertIn("fonts/Geist-Variable.woff2", home)
        self.assertIn('rel="preload"', home)
        self.assertNotIn("PCDS", home)
        self.assertNotIn("pcds2030", home)
        self.assertNotIn("brief-net", home)
        self.assertEqual(home.count('class="hub-card"'), 3)
        self.assertEqual(home.count('class="hero-art"'), 1)

    def test_third_site_renders_card_without_map_tile(self):
        listed = (Path(__file__).resolve().parents[1] / "data" / "sites.json").read_text(encoding="utf-8")
        self.assertNotIn("dummy", listed)
        self.assertNotIn("Dummy.Sarawak.News", listed)
        self.assertNotIn('"map"', listed)

        self.assertNotIn('"counts"', listed)
        sites = build.load_sites()
        self.assertEqual([site["id"] for site in sites], ["ai", "bantuan", "events"])
        published = build.render_home(sites)
        self.assertNotIn("Dummy.Sarawak.News", published)
        self.assertNotIn('data-site="dummy"', published)
        self.assertNotIn("hero-node", published)
        self.assertNotIn("hero-route", published)
        self.assertNotIn("hub-meta", published)

        home = build.render_home([*sites, DUMMY_SITE])

        self.assertEqual(home.count('class="hub-card"'), 4)
        self.assertEqual(home.count('class="hero-art"'), 1)
        self.assertNotIn("hero-node", home)
        self.assertNotIn("hero-route", home)
        self.assertNotIn("hero-tile", home)
        self.assertNotIn("hub-meta", home)
        self.assertIn('data-site="dummy"', home)
        self.assertEqual(home.count('data-site="dummy"'), 1)
        self.assertIn("Dummy.Sarawak.News", home)
        self.assertIn("A fixture site used only by the test.", home)
        self.assertIn("https://dummy.example/", home)
        self.assertIn(">Example<", home)
        self.assertEqual(home.count(">Visit <"), 4)

    def test_dist_publishes_root_domain(self):
        previous = os.environ.pop("SITE_URL", None)
        copy = site_copy()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                dist = Path(tmp)
                build.write_dist(build.render_home(), build.render_about(), dist)
                names = sorted(path.name for path in dist.rglob("*"))
                self.assertIn("index.html", names)
                self.assertIn("OFL.txt", names)
                self.assertIn("Geist-Variable.woff2", names)
                self.assertIn("CNAME", names)
                self.assertIn("nav-mark-transparent.svg", names)
                self.assertIn("nav-mark-transparent-dark.svg", names)
                self.assertNotIn("nav-mark-on-black.svg", names)
                icons = Path(__file__).resolve().parents[1] / "site" / "icons"
                self.assertEqual(
                    (dist / "icons" / "nav-mark-transparent.svg").read_bytes(),
                    (icons / "nav-mark-transparent.svg").read_bytes(),
                )
                self.assertEqual(
                    (dist / "icons" / "nav-mark-transparent-dark.svg").read_bytes(),
                    (icons / "nav-mark-transparent-dark.svg").read_bytes(),
                )
                self.assertEqual((dist / "CNAME").read_text(encoding="utf-8").strip(), "sarawak.news")
                self.assertNotIn("design-handoff", names)
                self.assertNotIn("preview-f1.png", names)
                self.assertFalse((dist / "design-handoff").exists())
                handoff = Path(__file__).resolve().parents[1] / "design-handoff" / "favicon-F1"
                for dest_name, src_name in build.FAVICON_FILES.items():
                    published = (dist / dest_name).read_bytes()
                    self.assertEqual(published, (handoff / src_name).read_bytes())
                    self.assertGreater(len(published), 0)
                og = (dist / "og.png").read_bytes()
                self.assertEqual(og, (Path(__file__).resolve().parents[1] / "site" / "og.png").read_bytes())
                self.assertEqual(int.from_bytes(og[16:20], "big"), 1200)
                self.assertEqual(int.from_bytes(og[20:24], "big"), 630)
                self.assertEqual(og[25], 2)
                origin = "https://sarawak.news/"
                home = (dist / "index.html").read_text(encoding="utf-8")
                about = (dist / "about.html").read_text(encoding="utf-8")
                for page in (home, about):
                    self.assertNotIn("github.io", page)
                    self.assertNotIn("/sarawak-news-hub/", page)
                    self.assertIn('href="style.css"', page)
                    self.assertIn('href="fonts/Geist-Variable.woff2"', page)
                    self.assertIn('src="app.js"', page)
                    self.assertIn('href="index.html"', page)
                    self.assertIn('href="about.html"', page)
                    self.assertIn('src="icons/nav-mark-transparent.svg"', page)
                    self.assertIn('src="icons/nav-mark-transparent-dark.svg"', page)
                    self.assertIn(f'class="brand-text">{copy["title"]}</span>', page)
                    self.assertNotIn("nav-mark-on-black", page)
                    self.assertNotIn("nav-mark-on-white", page)
                    self.assertNotIn("final-sheet-origami", page)
                self.assertIn(f'<link rel="canonical" href="{origin}" />', home)
                self.assertIn(f'<meta property="og:url" content="{origin}" />', home)
                self.assertIn(f'<link rel="canonical" href="{origin}about.html" />', about)
                self.assertIn(f'<meta property="og:url" content="{origin}about.html" />', about)
                about_title = f"About {copy['title']}"
                self.assertIn(f"<title>{about_title}</title>", about)
                self.assertIn(
                    f'<meta name="description" content="{copy["description"]}" />',
                    about,
                )
                self.assertIn(
                    f'<meta property="og:description" content="{copy["description"]}" />',
                    about,
                )
                self.assertIn(
                    f'<meta name="twitter:description" content="{copy["description"]}" />',
                    about,
                )
                self.assertIn(copy["about_lead"], about)
                self.assertNotIn("Explore Sarawak-focused sites", about)
                self.assertIn('class="site-footer-main site-footer-main--column-stacks"', about)
                self.assertIn('<nav aria-label="Hub" class="site-footer-fleet-nav">', about)
                self.assertIn(
                    '<nav aria-label="Explore" class="site-footer-nav site-footer-grid-explore">',
                    about,
                )
                self.assertIn('<a class="site-footer-link" href="index.html">Home</a>', about)
                self.assertIn(
                    '<a class="site-footer-link" href="about.html" aria-current="page">About</a>',
                    about,
                )
                self.assertIn(
                    '<a class="site-footer-link" href="mailto:contact@sarawak.news">Contact</a>',
                    about,
                )
                # No doubled full stop after the tagline when composing the About lead.
                self.assertNotIn("..", about.split("about-lede", 1)[-1][:120])
                self.assertNotIn("Each site links to its sources.", about)
                self.assertNotIn("Sarawak News made easy", about)
                self.assertNotIn("about-credits", about)
                self.assertNotIn("about-credit", about)
                self.assertNotIn("The DUN is traced from a", about)
                self.assertNotIn("The Darul Hana pylons are traced from a", about)
                self.assertNotIn("Gunung Santubong is traced from a", about)
                self.assertNotIn("Meandkancil2020", about)
                self.assertNotIn("Matthew Anderson Lockhart", about)
                self.assertNotIn("CEphoto", about)
                self.assertNotIn("Uwe Aranas", about)
                self.assertIn("hafiy.my", about)
                self.assertNotIn("art-boat", about)
                self.assertNotIn("John Mason", about)
                self.assertNotIn("Tnunong", about)
                self.assertNotIn("Bot_tambang", about)
                self.assertNotIn("CEphoto", home)
                self.assertNotIn(".jpg", home)
                self.assertNotIn("commons.wikimedia.org", home)
                self.assertIn(f'<meta property="og:title" content="{about_title}" />', about)
                self.assertIn(f'<meta name="twitter:title" content="{about_title}" />', about)
                og_src = Path(__file__).resolve().parents[1] / "site" / "og.png"
                og_hash = hashlib.sha256(og_src.read_bytes()).hexdigest()[:12]
                og_url = "https://sarawak.news/og.png?v=" + og_hash
                icon_hashes = []
                for page in (home, about):
                    for dest_name, src_name in build.FAVICON_FILES.items():
                        src = handoff / src_name
                        file_hash = hashlib.sha256(src.read_bytes()).hexdigest()[:12]
                        icon_hashes.append(file_hash)
                        stamped = dest_name + "?v=" + file_hash
                        self.assertIn(stamped, page)
                    self.assertNotIn("solid3", page)
                    self.assertIn('<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />', page)
                    self.assertIn('<meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)" />', page)
                    self.assertIn(f'<meta property="og:image" content="{og_url}" />', page)
                    self.assertIn('<meta property="og:image:width" content="1200" />', page)
                    self.assertIn('<meta property="og:image:height" content="630" />', page)
                    self.assertIn('<meta name="twitter:card" content="summary_large_image" />', page)
                    self.assertIn(f'<meta name="twitter:image" content="{og_url}" />', page)
                    self.assertNotIn('<meta name="twitter:card" content="summary" />', page)
                self.assertEqual(len(set(icon_hashes)), len(build.FAVICON_FILES))
                robots = (dist / "robots.txt").read_text(encoding="utf-8")
                sitemap = (dist / "sitemap.xml").read_text(encoding="utf-8")
                self.assertIn(f"Sitemap: {origin}sitemap.xml", robots)
                self.assertIn(f"<loc>{origin}</loc>", sitemap)
                self.assertIn(f"<loc>{origin}about.html</loc>", sitemap)
                self.assertEqual(sitemap.count("<url>"), 2)
                self.assertIn("<lastmod>", sitemap)
                self.assertNotIn("github.io", robots + sitemap)
                self.assertNotIn("pcds2030", home.lower() + about.lower())
                self.assertIn('href="about.html">About this hub</a>', home)
                self.assertIn("https://events.sarawak.news/", home)
                self.assertIn("https://events.sarawak.news/about.html", about)
        finally:
            if previous is not None:
                os.environ["SITE_URL"] = previous


class GaScriptTests(unittest.TestCase):
    def test_analytics_loader_gates_hosts_and_marks_internal(self):
        loader = build.render_analytics_loader()
        self.assertIn(build.ANALYTICS_LOADER_ATTR, loader)
        self.assertEqual(loader.count(build.ANALYTICS_LOADER_ATTR), 1)
        self.assertIn(build.GA_MEASUREMENT_ID, loader)
        self.assertIn(build.CLOUDFLARE_WEB_ANALYTICS_TOKEN, loader)
        self.assertIn('"sarawak.news"', loader)
        self.assertIn('"www.sarawak.news"', loader)
        self.assertIn(build.GA_INTERNAL_COOKIE, loader)
        self.assertIn("traffic_type", loader)
        self.assertIn("'internal'", loader)
        self.assertIn("max-age=31536000", loader)
        self.assertIn("q.get('internal')==='1'", loader)
        self.assertIn("q.get('internal')==='0'", loader)
        self.assertIn("H.indexOf(h)<0", loader)
        self.assertIn("googletagmanager.com/gtag/js?id=", loader)
        self.assertIn("static.cloudflareinsights.com/beacon.min.js", loader)
        self.assertIn("if(internal)return", loader)
        self.assertIn("spa:false", loader)
        # No unconditional remote script tags — load only after the host gate.
        self.assertNotIn('<script async src="https://www.googletagmanager.com/gtag/js', loader)
        self.assertNotIn(
            '<script defer src="https://static.cloudflareinsights.com/beacon.min.js"',
            loader,
        )

    def test_pages_include_one_analytics_loader(self):
        home = build.render_home()
        about = build.render_about()
        for page in (home, about):
            self.assertEqual(page.count(build.ANALYTICS_LOADER_ATTR), 1)
            self.assertIn(build.GA_MEASUREMENT_ID, page)
            self.assertIn("traffic_type", page)
            self.assertIn(build.GA_INTERNAL_COOKIE, page)
            self.assertIn("static.cloudflareinsights.com/beacon.min.js", page)
            self.assertIn("if(internal)return", page)
            self.assertIn("spa:false", page)


class DocsCheckTests(unittest.TestCase):
    def test_watch_patterns(self):
        self.assertTrue(docs_check.matches_watch("site/style.css"))
        self.assertTrue(docs_check.matches_watch("site/fonts/OFL.txt"))
        self.assertTrue(docs_check.matches_watch("kit/python/shell.py"))
        self.assertTrue(docs_check.matches_watch("kit/css/back-to-top.css"))
        self.assertTrue(docs_check.matches_watch("scripts/build.py"))
        self.assertTrue(docs_check.matches_watch("scripts/analytics_registry.py"))
        self.assertTrue(docs_check.matches_watch("scripts/check_analytics_dist.py"))
        self.assertTrue(docs_check.matches_watch(".github/workflows/build.yml"))
        self.assertFalse(docs_check.matches_watch("data/sarawak-path.txt"))
        self.assertFalse(docs_check.matches_watch("data/sarawak-proj.json"))
        self.assertTrue(docs_check.matches_watch("data/sites.json"))
        self.assertTrue(docs_check.matches_watch("data/site.json"))
        self.assertTrue(docs_check.matches_watch("data/analytics.json"))
        self.assertFalse(docs_check.matches_watch("README.md"))

    def test_label_skips_requirement(self):
        self.assertTrue(docs_check.has_label("bug, no-docs-needed", "no-docs-needed"))
        self.assertFalse(docs_check.has_label("docs", "no-docs-needed"))
        self.assertTrue(docs_check.touches_docs("docs/design.md"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Build and docs-check tests. No network."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.build as build
import scripts.docs_check_pr as docs_check


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
        home = build.render_home()
        self.assertIn("<h1>Sarawak, made easy.</h1>", home)
        self.assertNotIn("Sarawak News made easy", home)
        self.assertIn(
            '<meta name="description" content="Aggregating key information, all in one place." />',
            home,
        )
        self.assertIn(
            '<meta property="og:description" content="Aggregating key information, all in one place." />',
            home,
        )
        self.assertIn(
            '<meta name="twitter:description" content="Aggregating key information, all in one place." />',
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
            '<p class="brief-deck">Aggregating key information, all in one place.</p>',
            home,
        )
        self.assertNotIn("Explore Sarawak-focused sites", home)
        self.assertNotIn("Each site links to its sources.", home)
        self.assertIn("<title>Sarawak.News</title>", home)
        self.assertIn('<meta property="og:title" content="Sarawak.News" />', home)
        self.assertIn('<meta name="twitter:title" content="Sarawak.News" />', home)
        self.assertNotIn("<title>Independent", home)
        self.assertIn("AI.Sarawak.News", home)
        self.assertIn("Bantuan.Sarawak.News", home)
        self.assertIn("Events.Sarawak.News", home)
        self.assertNotIn("hub-meta", home)
        self.assertNotIn("stories", home)
        self.assertNotIn("schemes", home)
        self.assertNotIn("categories", home)
        self.assertIn('href="https://ai.sarawak.news/"', home)
        self.assertIn('href="https://bantuan.sarawak.news/"', home)
        self.assertIn('href="https://events.sarawak.news"', home)
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
        try:
            with tempfile.TemporaryDirectory() as tmp:
                dist = Path(tmp)
                build.write_dist(build.render_home(), build.render_about(), dist)
                names = sorted(path.name for path in dist.rglob("*"))
                self.assertIn("index.html", names)
                self.assertIn("OFL.txt", names)
                self.assertIn("Geist-Variable.woff2", names)
                self.assertIn("CNAME", names)
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
                self.assertIn(f'<link rel="canonical" href="{origin}" />', home)
                self.assertIn(f'<meta property="og:url" content="{origin}" />', home)
                self.assertIn(f'<link rel="canonical" href="{origin}about.html" />', about)
                self.assertIn(f'<meta property="og:url" content="{origin}about.html" />', about)
                self.assertIn("<title>About Sarawak.News</title>", about)
                self.assertIn(
                    '<meta name="description" content="Aggregating key information, all in one place." />',
                    about,
                )
                self.assertIn(
                    '<meta property="og:description" content="Aggregating key information, all in one place." />',
                    about,
                )
                self.assertIn(
                    '<meta name="twitter:description" content="Aggregating key information, all in one place." />',
                    about,
                )
                self.assertIn(
                    "Sarawak, made easy. Aggregating key information, all in one place.",
                    about,
                )
                self.assertNotIn("Explore Sarawak-focused sites", about)
                self.assertNotIn("Sarawak, made easy..", about)
                self.assertNotIn("Each site links to its sources.", about)
                self.assertNotIn("Sarawak News made easy", about)
                self.assertEqual(about.count('class="about-credit"'), 3)
                for _lead, author, photo, licence, name in build.DRAWING_CREDITS:
                    self.assertIn(author, about)
                    self.assertIn(photo, about)
                    self.assertIn(licence, about)
                    self.assertIn(name, about)
                self.assertNotIn("art-boat", about)
                self.assertNotIn("John Mason", about)
                self.assertNotIn("Tnunong", about)
                self.assertNotIn("Bot_tambang", about)
                self.assertNotIn("CEphoto", home)
                self.assertNotIn(".jpg", home)
                self.assertNotIn("commons.wikimedia.org", home)
                self.assertIn('<meta property="og:title" content="About Sarawak.News" />', about)
                self.assertIn('<meta name="twitter:title" content="About Sarawak.News" />', about)
                for page in (home, about):
                    self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml" />', page)
                    self.assertIn('<link rel="icon" href="favicon.ico" sizes="any" />', page)
                    self.assertIn('<link rel="apple-touch-icon" href="apple-touch-icon.png" />', page)
                    self.assertIn('<link rel="icon" href="icon-192.png" type="image/png" sizes="192x192" />', page)
                    self.assertIn('<link rel="icon" href="icon-512.png" type="image/png" sizes="512x512" />', page)
                    self.assertIn('<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />', page)
                    self.assertIn('<meta name="theme-color" content="#0f1115" media="(prefers-color-scheme: dark)" />', page)
                    self.assertIn('<meta property="og:image" content="https://sarawak.news/og.png" />', page)
                    self.assertIn('<meta property="og:image:width" content="1200" />', page)
                    self.assertIn('<meta property="og:image:height" content="630" />', page)
                    self.assertIn('<meta name="twitter:card" content="summary_large_image" />', page)
                    self.assertIn('<meta name="twitter:image" content="https://sarawak.news/og.png" />', page)
                    self.assertNotIn('<meta name="twitter:card" content="summary" />', page)
                robots = (dist / "robots.txt").read_text(encoding="utf-8")
                sitemap = (dist / "sitemap.xml").read_text(encoding="utf-8")
                self.assertIn(f"Sitemap: {origin}sitemap.xml", robots)
                self.assertIn(f"<loc>{origin}</loc>", sitemap)
                self.assertIn(f"<loc>{origin}about.html</loc>", sitemap)
                self.assertNotIn("github.io", robots + sitemap)
        finally:
            if previous is not None:
                os.environ["SITE_URL"] = previous


class GaScriptTests(unittest.TestCase):
    def test_ga_script_gates_hosts_and_marks_internal(self):
        ga = build.render_ga_script()
        self.assertIn(build.GA_MEASUREMENT_ID, ga)
        self.assertIn('"sarawak.news"', ga)
        self.assertIn('"www.sarawak.news"', ga)
        self.assertIn(build.GA_INTERNAL_COOKIE, ga)
        self.assertIn("traffic_type", ga)
        self.assertIn("'internal'", ga)
        self.assertIn("max-age=31536000", ga)
        self.assertIn("q.get('internal')==='1'", ga)
        self.assertIn("q.get('internal')==='0'", ga)
        self.assertIn("H.indexOf(h)<0", ga)
        self.assertIn("googletagmanager.com/gtag/js?id=", ga)
        # No unconditional remote script tag — load only after the host gate.
        self.assertNotIn('<script async src="https://www.googletagmanager.com/gtag/js', ga)

    def test_cf_beacon_skips_when_internal(self):
        cf = build.render_cf_beacon()
        self.assertIn(build.CLOUDFLARE_WEB_ANALYTICS_TOKEN, cf)
        self.assertIn('"sarawak.news"', cf)
        self.assertIn(build.GA_INTERNAL_COOKIE, cf)
        self.assertIn("if(internal)return", cf)
        self.assertIn("static.cloudflareinsights.com/beacon.min.js", cf)
        self.assertIn("H.indexOf(h)<0", cf)
        # No unconditional beacon tag — load only after host + cookie gates.
        self.assertNotIn(
            '<script defer src="https://static.cloudflareinsights.com/beacon.min.js"',
            cf,
        )

    def test_pages_include_ga_script(self):
        home = build.render_home()
        about = build.render_about()
        for page in (home, about):
            self.assertIn(build.GA_MEASUREMENT_ID, page)
            self.assertIn("traffic_type", page)
            self.assertIn(build.GA_INTERNAL_COOKIE, page)
            self.assertIn("static.cloudflareinsights.com/beacon.min.js", page)
            self.assertIn("if(internal)return", page)


class DocsCheckTests(unittest.TestCase):
    def test_watch_patterns(self):
        self.assertTrue(docs_check.matches_watch("site/style.css"))
        self.assertTrue(docs_check.matches_watch("site/fonts/OFL.txt"))
        self.assertTrue(docs_check.matches_watch("scripts/build.py"))
        self.assertTrue(docs_check.matches_watch(".github/workflows/build.yml"))
        self.assertFalse(docs_check.matches_watch("data/sarawak-path.txt"))
        self.assertFalse(docs_check.matches_watch("data/sarawak-proj.json"))
        self.assertTrue(docs_check.matches_watch("data/sites.json"))
        self.assertFalse(docs_check.matches_watch("README.md"))

    def test_label_skips_requirement(self):
        self.assertTrue(docs_check.has_label("bug, no-docs-needed", "no-docs-needed"))
        self.assertFalse(docs_check.has_label("docs", "no-docs-needed"))
        self.assertTrue(docs_check.touches_docs("docs/design.md"))


if __name__ == "__main__":
    unittest.main()

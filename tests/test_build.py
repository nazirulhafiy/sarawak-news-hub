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
        self.assertIn("Independent<br>Sarawak sites,<br>in one place.", home)
        self.assertIn("Each site links to its sources.", home)
        self.assertIn("AI.Sarawak.News", home)
        self.assertIn("Bantuan.Sarawak.News", home)
        self.assertNotIn("hub-meta", home)
        self.assertNotIn("stories", home)
        self.assertNotIn("schemes", home)
        self.assertNotIn("categories", home)
        self.assertIn('href="https://ai.sarawak.news/"', home)
        self.assertIn('href="https://bantuan.sarawak.news/"', home)
        self.assertNotIn('class="hub-domain"', home)
        self.assertEqual(home.count(">Visit <"), 2)
        self.assertIn('class="hero-land"', home)
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
        self.assertEqual(home.count('class="hub-card"'), 2)
        self.assertEqual(home.count('class="hero-land"'), 1)

    def test_third_site_renders_card_without_map_tile(self):
        listed = (Path(__file__).resolve().parents[1] / "data" / "sites.json").read_text(encoding="utf-8")
        self.assertNotIn("dummy", listed)
        self.assertNotIn("Dummy.Sarawak.News", listed)
        self.assertNotIn('"map"', listed)

        self.assertNotIn('"counts"', listed)
        sites = build.load_sites()
        self.assertEqual([site["id"] for site in sites], ["ai", "bantuan"])
        published = build.render_home(sites)
        self.assertNotIn("Dummy.Sarawak.News", published)
        self.assertNotIn('data-site="dummy"', published)
        self.assertNotIn("hero-node", published)
        self.assertNotIn("hero-route", published)
        self.assertNotIn("hub-meta", published)

        home = build.render_home([*sites, DUMMY_SITE])

        self.assertEqual(home.count('class="hub-card"'), 3)
        self.assertEqual(home.count('class="hero-land"'), 1)
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
        self.assertEqual(home.count(">Visit <"), 3)

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
                self.assertFalse((dist / "design-handoff").exists())
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
                robots = (dist / "robots.txt").read_text(encoding="utf-8")
                sitemap = (dist / "sitemap.xml").read_text(encoding="utf-8")
                self.assertIn(f"Sitemap: {origin}sitemap.xml", robots)
                self.assertIn(f"<loc>{origin}</loc>", sitemap)
                self.assertIn(f"<loc>{origin}about.html</loc>", sitemap)
                self.assertNotIn("github.io", robots + sitemap)
        finally:
            if previous is not None:
                os.environ["SITE_URL"] = previous


class DocsCheckTests(unittest.TestCase):
    def test_watch_patterns(self):
        self.assertTrue(docs_check.matches_watch("site/style.css"))
        self.assertTrue(docs_check.matches_watch("site/fonts/OFL.txt"))
        self.assertTrue(docs_check.matches_watch("scripts/build.py"))
        self.assertTrue(docs_check.matches_watch(".github/workflows/build.yml"))
        self.assertTrue(docs_check.matches_watch("data/sarawak-path.txt"))
        self.assertTrue(docs_check.matches_watch("data/sites.json"))
        self.assertFalse(docs_check.matches_watch("README.md"))

    def test_label_skips_requirement(self):
        self.assertTrue(docs_check.has_label("bug, no-docs-needed", "no-docs-needed"))
        self.assertFalse(docs_check.has_label("docs", "no-docs-needed"))
        self.assertTrue(docs_check.touches_docs("docs/design.md"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Build and docs-check tests. No network."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.build as build
import scripts.docs_check_pr as docs_check


AI_PAGE = """
<p class="updated"><span class="updated-label">Last updated</span><time datetime="2026-10-08">THURSDAY, 8 OCT 2026</time></p>
<button data-section-filter="all">All <span class="category-filter-count">2</span></button>
<button data-section-filter="policy">Policy <span class="category-filter-count">1</span></button>
<button data-section-filter="business">Business <span class="category-filter-count">1</span></button>
<article class="story-card"></article>
<article class="story-card"></article>
"""

BANTUAN_PAGE = """
<p class="updated"><span class="updated-label">Last updated</span> <time datetime="2026-10-06">TUESDAY, 6 OCT 2026</time></p>
"""

BANTUAN_SCHEMES = json.dumps(
    [
        {"id": "a", "group": "household"},
        {"id": "b", "group": "student"},
        {"id": "c", "group": "student"},
    ]
)

PREVIOUS = {
    "ai": {"stories": 81, "categories": 7, "updated": "2026-10-08"},
    "bantuan": {"schemes": 24, "categories": 7, "updated": "2026-10-06"},
}


class ParseTests(unittest.TestCase):
    def test_parse_ai(self):
        parsed = build.parse_ai(AI_PAGE)
        self.assertEqual(parsed, {"stories": 2, "categories": 2, "updated": "2026-10-08"})

    def test_ai_badge_mismatch_is_a_failure(self):
        page = AI_PAGE.replace(">2</span>", ">9</span>", 1)
        with self.assertRaises(ValueError):
            build.parse_ai(page)

    def test_parse_bantuan(self):
        parsed = build.parse_bantuan(BANTUAN_SCHEMES, BANTUAN_PAGE)
        self.assertEqual(parsed, {"schemes": 3, "categories": 2, "updated": "2026-10-06"})

    def test_failed_fetch_keeps_last_known(self):
        def getter(url: str) -> str:
            raise TimeoutError(url)

        counts, notes = build.refresh_counts(PREVIOUS, getter)
        self.assertEqual(counts, PREVIOUS)
        self.assertTrue(any("keeping" in note for note in notes))

    def test_partial_failure_keeps_only_the_failed_site(self):
        def getter(url: str) -> str:
            if "schemes.json" in url or url.rstrip("/").endswith("bantuan.sarawak.news"):
                raise OSError("down")
            return AI_PAGE

        counts, notes = build.refresh_counts(PREVIOUS, getter)
        self.assertEqual(counts["ai"]["stories"], 2)
        self.assertEqual(counts["bantuan"], PREVIOUS["bantuan"])
        self.assertTrue(any("bantuan" in note and "keeping" in note for note in notes))


class RenderTests(unittest.TestCase):
    def test_home_has_two_cards_hero_and_map_credit(self):
        home = build.render_home(PREVIOUS)
        self.assertIn("Independent<br>Sarawak sites,<br>in one place.", home)
        self.assertIn("Each site links to its sources.", home)
        self.assertIn("AI.Sarawak.News", home)
        self.assertIn("Bantuan.Sarawak.News", home)
        self.assertIn("81 stories · 7 categories", home)
        self.assertIn("24 schemes · 7 categories", home)
        self.assertIn("https://ai.sarawak.news/", home)
        self.assertIn("https://bantuan.sarawak.news/", home)
        self.assertIn('class="hero-land"', home)
        self.assertIn('class="hero-route"', home)
        self.assertIn("Map: ", home)
        self.assertIn("Natural Earth", home)
        self.assertIn("fonts/Geist-Variable.woff2", home)
        self.assertIn('rel="preload"', home)
        self.assertNotIn("PCDS", home)
        self.assertNotIn("pcds2030", home)
        self.assertNotIn("brief-net", home)
        self.assertEqual(home.count('class="hub-card"'), 2)

    def test_dist_omits_handoff_and_cname(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            build.write_dist(build.render_home(PREVIOUS), build.render_about(), dist)
            names = sorted(path.name for path in dist.rglob("*"))
            self.assertIn("index.html", names)
            self.assertIn("OFL.txt", names)
            self.assertIn("Geist-Variable.woff2", names)
            self.assertNotIn("CNAME", names)
            self.assertNotIn("design-handoff", names)
            self.assertFalse((dist / "design-handoff").exists())


class DocsCheckTests(unittest.TestCase):
    def test_watch_patterns(self):
        self.assertTrue(docs_check.matches_watch("site/style.css"))
        self.assertTrue(docs_check.matches_watch("site/fonts/OFL.txt"))
        self.assertTrue(docs_check.matches_watch("scripts/build.py"))
        self.assertTrue(docs_check.matches_watch(".github/workflows/build.yml"))
        self.assertTrue(docs_check.matches_watch("data/sarawak-path.txt"))
        self.assertFalse(docs_check.matches_watch("data/counts.json"))
        self.assertFalse(docs_check.matches_watch("README.md"))

    def test_label_skips_requirement(self):
        self.assertTrue(docs_check.has_label("bug, no-docs-needed", "no-docs-needed"))
        self.assertFalse(docs_check.has_label("docs", "no-docs-needed"))
        self.assertTrue(docs_check.touches_docs("docs/design.md"))


if __name__ == "__main__":
    unittest.main()

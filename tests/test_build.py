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
    "ai": {"count": 81, "categories": 7, "updated": "2026-10-08"},
    "bantuan": {"count": 24, "categories": 7, "updated": "2026-10-06"},
}

# Fixture only. Not an entry in data/sites.json.
DUMMY_SITE = {
    "id": "dummy",
    "name": "Dummy.Sarawak.News",
    "url": "https://dummy.example/",
    "tag": "Example",
    "icon": "brain",
    "text": "A fixture site used only by the test.",
    "map": {"x": 300, "y": 260},
    "counts": {
        "via": "html-stories",
        "page": "https://dummy.example/",
        "noun": ["item", "items"],
        "groupNoun": ["group", "groups"],
    },
}


class ParseTests(unittest.TestCase):
    def test_parse_ai(self):
        parsed = build.parse_ai(AI_PAGE)
        self.assertEqual(parsed, {"count": 2, "categories": 2, "updated": "2026-10-08"})

    def test_ai_badge_mismatch_is_a_failure(self):
        page = AI_PAGE.replace(">2</span>", ">9</span>", 1)
        with self.assertRaises(ValueError):
            build.parse_ai(page)

    def test_parse_bantuan(self):
        parsed = build.parse_bantuan(BANTUAN_SCHEMES, BANTUAN_PAGE)
        self.assertEqual(parsed, {"count": 3, "categories": 2, "updated": "2026-10-06"})

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
        self.assertEqual(counts["ai"]["count"], 2)
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
        self.assertEqual(home.count('class="hero-node"'), 2)

    def test_third_site_renders_card_and_map_tile(self):
        listed = (Path(__file__).resolve().parents[1] / "data" / "sites.json").read_text(encoding="utf-8")
        self.assertNotIn("dummy", listed)
        self.assertNotIn("Dummy.Sarawak.News", listed)

        sites = build.load_sites()
        self.assertEqual([site["id"] for site in sites], ["ai", "bantuan"])
        published = build.render_home(PREVIOUS, sites)
        self.assertNotIn("Dummy.Sarawak.News", published)
        self.assertNotIn('data-site="dummy"', published)

        extra = [*sites, DUMMY_SITE]
        counts = dict(PREVIOUS)
        counts["dummy"] = {"count": 3, "categories": 1, "updated": "2026-10-01"}
        home = build.render_home(counts, extra)

        self.assertEqual(home.count('class="hub-card"'), 3)
        self.assertEqual(home.count('class="hero-node"'), 3)
        self.assertIn('data-site="dummy"', home)
        self.assertEqual(home.count('data-site="dummy"'), 2)
        self.assertIn("Dummy.Sarawak.News", home)
        self.assertIn("A fixture site used only by the test.", home)
        self.assertIn("https://dummy.example/", home)
        self.assertIn('transform="translate(300.0 260.0)"', home)
        self.assertIn(">Example<", home)

        polygon = build.outline_points()
        centre = build.site_point(DUMMY_SITE)
        self.assertTrue(build.point_in_outline(*centre, polygon))
        inset = build.TILE_SIZE / 2 - 2
        for dx in (-inset, inset):
            for dy in (-inset, inset):
                self.assertTrue(
                    build.point_in_outline(centre[0] + dx, centre[1] + dy, polygon),
                    f"tile corner {(centre[0] + dx, centre[1] + dy)} is outside the outline",
                )
        for other in sites:
            self.assertFalse(build.tiles_overlap(centre, build.site_point(other)))

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
        self.assertTrue(docs_check.matches_watch("data/sites.json"))
        self.assertFalse(docs_check.matches_watch("data/counts.json"))
        self.assertFalse(docs_check.matches_watch("README.md"))

    def test_label_skips_requirement(self):
        self.assertTrue(docs_check.has_label("bug, no-docs-needed", "no-docs-needed"))
        self.assertFalse(docs_check.has_label("docs", "no-docs-needed"))
        self.assertTrue(docs_check.touches_docs("docs/design.md"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Shared kit sync checks."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KitSyncTests(unittest.TestCase):
    def test_hub_check_passes(self):
        result = subprocess.run(
            ["python3", "kit/sync.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("OK kit sync", result.stdout)

    def test_hand_edited_back_to_top_fails(self):
        target = ROOT / "kit" / "js" / "back-to-top.js"
        original = target.read_text(encoding="utf-8")
        try:
            target.write_text(original + "\n/* drift */\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", "kit/sync.py", "--check"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FAIL kit sync", result.stderr)
        finally:
            target.write_text(original, encoding="utf-8")

    def test_missing_contact_invariant_fails(self):
        target = ROOT / "kit" / "python" / "shell.py"
        original = target.read_text(encoding="utf-8")
        try:
            target.write_text(
                original.replace("mailto:contact@sarawak.news", "mailto:nobody@example.com"),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", "kit/sync.py", "--check"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("footer-contact", result.stderr)
        finally:
            target.write_text(original, encoding="utf-8")

    def test_sister_pin_check_against_this_hub(self):
        pin = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        with tempfile.TemporaryDirectory() as tmp:
            sister = Path(tmp)
            tracked = subprocess.run(
                ["git", "ls-files", "kit/MANIFEST.json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if not tracked.stdout.strip():
                self.skipTest("kit/ not committed yet")
            archive = sister / "kit.tar"
            with archive.open("wb") as fh:
                subprocess.check_call(
                    ["git", "archive", pin, "kit"],
                    cwd=ROOT,
                    stdout=fh,
                )
            subprocess.check_call(["tar", "-xf", "kit.tar"], cwd=sister)
            (sister / "kit" / "PIN").write_text(pin + "\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", "kit/sync.py", "--check", "--hub-path", str(ROOT)],
                cwd=sister,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            btt = sister / "kit" / "js" / "back-to-top.js"
            btt.write_text(btt.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            btt.write_text(btt.read_text(encoding="utf-8") + "// edited\n", encoding="utf-8")
            bad = subprocess.run(
                ["python3", "kit/sync.py", "--check", "--hub-path", str(ROOT)],
                cwd=sister,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("local edit or stale vendor", bad.stderr)

    def test_hub_sync_leaves_mirrors_unchanged(self):
        paths = [
            ROOT / "site" / "style.css",
            ROOT / "site" / "app.js",
            ROOT / "site" / "icons" / "nav-mark-transparent.svg",
            ROOT / "site" / "icons" / "nav-mark-transparent-dark.svg",
        ]
        before = {path: path.read_bytes() for path in paths}
        result = subprocess.run(
            ["python3", "kit/sync.py", "--sync"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        after = {path: path.read_bytes() for path in paths}
        self.assertEqual(before, after)

    def test_pages_emit_contact_back_to_top_and_loader(self):
        import scripts.build as build

        for page in (build.render_home(), build.render_about()):
            self.assertIn(
                '<a class="site-footer-link" href="mailto:contact@sarawak.news">Contact</a>',
                page,
            )
            self.assertIn("data-back-to-top", page)
            self.assertIn("back-to-top-label", page)
            self.assertIn("back-to-top-arrow", page)
            self.assertEqual(page.count("data-sn-analytics-loader"), 1)
            self.assertIn("sn_internal", page)
            # Hub uses a single brand_note; no mid-note break.
            self.assertNotIn("site-footer-note-break", page)

    def test_footer_fleet_cross_links_are_plain_hrefs_without_nofollow(self):
        from kit.python.shell import render_footer

        html = render_footer(
            brand_title="Events.Sarawak.News",
            brand_note="Note.",
            active="home",
            explore_items=(),
            fleet_site="events",
        )
        self.assertNotIn('<div class="site-footer-fleet">', html)
        self.assertIn('<nav aria-label="Sarawak News" class="site-footer-fleet-nav">', html)
        summary_slice = html.split('<div class="site-footer-summary">', 1)[1].split(
            '<nav aria-label="Explore"', 1
        )[0]
        self.assertIn("https://sarawak.news/", summary_slice)
        self.assertIn('<a class="site-footer-link" href="https://ai.sarawak.news/">', html)
        self.assertIn(
            '<a class="site-footer-link" href="https://bantuan.sarawak.news/">',
            html,
        )
        self.assertNotIn("https://events.sarawak.news/", html)
        self.assertNotIn("nofollow", html)
        explore_slice = html.split('<nav aria-label="Explore"', 1)[1].split(
            '<div class="site-footer-bottom">', 1
        )[0]
        self.assertIn("Contact</a></li>", explore_slice)
        self.assertNotIn("https://sarawak.news/", explore_slice)

    def test_footer_note_parts_emit_kit_break(self):
        from kit.python.shell import FOOTER_NOTE_BREAK, NavItem, render_footer

        html = render_footer(
            brand_title="AI.Sarawak.News",
            active="home",
            explore_items=(NavItem("home", "/", "Home"),),
            brand_note_parts=(
                "First sentence.",
                "Second sentence.",
            ),
        )
        self.assertIn(FOOTER_NOTE_BREAK, html)
        self.assertIn(
            f'<p class="site-footer-note">First sentence.{FOOTER_NOTE_BREAK}Second sentence.</p>',
            html,
        )

    def test_render_footer_column_stacks_markup(self):
        from kit.python.shell import NavItem, render_footer

        categories = (
            '<h2 class="site-footer-categories-title">Categories</h2>'
            "<ul><li><a class=\"site-footer-link\" href=\"/?type=x\">X</a></li></ul>"
        )
        html = render_footer(
            brand_title="Events.Sarawak.News",
            brand_note="Note.",
            active="home",
            explore_items=(NavItem("home", "/", "Home"),),
            fleet_site="events",
            layout="column_stacks",
            extra_nav_right=categories,
        )
        self.assertIn('class="site-footer-main site-footer-main--column-stacks"', html)
        self.assertIn("site-footer-grid-stack-left", html)
        self.assertIn("site-footer-grid-brand-cell", html)
        self.assertIn("site-footer-grid-fleet", html)
        self.assertIn("site-footer-grid-stack-right", html)
        self.assertIn("site-footer-grid-explore", html)
        self.assertIn('<hr class="site-footer-grid-explore-divider" />', html)
        self.assertIn("site-footer-grid-categories", html)
        self.assertNotIn(
            '<div class="site-footer-summary">\n        <p class="site-footer-brand">',
            html,
        )
        self.assertIn('<nav aria-label="Sarawak News" class="site-footer-fleet-nav">', html)

    def test_render_footer_fleet_section_label_override(self):
        from kit.python.shell import render_footer

        html = render_footer(
            brand_title="Events.Sarawak.News",
            brand_note="Note.",
            active="home",
            explore_items=(),
            fleet_site="events",
            layout="column_stacks",
            fleet_section_label="Hub",
        )
        self.assertIn('<nav aria-label="Hub" class="site-footer-fleet-nav">', html)
        self.assertIn("<h2>Hub</h2>", html)
        self.assertNotIn('aria-label="Sarawak News"', html)

    def test_render_footer_classic_default_unchanged(self):
        from kit.python.shell import render_footer

        html = render_footer(
            brand_title="Example Hub",
            brand_note="Deck.",
            active="home",
            explore_items=(),
            fleet_site="hub",
        )
        self.assertIn('<div class="site-footer-main">', html)
        self.assertNotIn("site-footer-main--column-stacks", html)
        self.assertIn('<div class="site-footer-summary">', html)
        self.assertIn('<nav aria-label="Sarawak News" class="site-footer-fleet-nav">', html)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Generated doc blocks match site copy, analytics, hosting, and CSS tokens."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kit.python.docs_facts import BLOCK_IDS, check, generate, render_block  # noqa: E402

_ANALYTICS = {
    "version": 1,
    "internal_cookie": "test_cookie",
    "spa": False,
    "hosts": {
        "example.test": {
            "ga4_measurement_id": "G-TEST1234",
            "cf_beacon_token": "0123456789abcdef0123456789abcdef",
            "aliases": ["www.example.test"],
            "legacy_internal_cookies": ["test_cookie"],
        }
    },
}

_CSS = textwrap.dedent(
    """\
    :root {
      color-scheme: light;
      --canvas: #ffffff;
      --ink: #111827;
    }
    html[data-theme="dark"] {
      color-scheme: dark;
      --canvas: #0f1115;
      --only-dark: #abc;
    }
    html[data-theme="dark"] a {
      --decoy: #fff;
      color: red;
    }
    @media (max-width: 560px) {
      :root { --canvas: #000000; }
    }
    """
)

_DESIGN = textwrap.dedent(
    """\
    # Design

    <!-- BEGIN GENERATED: site-copy -->
    <!-- END GENERATED: site-copy -->

    <!-- BEGIN GENERATED: analytics -->
    <!-- END GENERATED: analytics -->

    <!-- BEGIN GENERATED: hosting -->
    <!-- END GENERATED: hosting -->

    <!-- BEGIN GENERATED: design-tokens -->
    <!-- END GENERATED: design-tokens -->
    """
)

_README = textwrap.dedent(
    """\
    # Readme

    <!-- BEGIN GENERATED: site-copy -->
    <!-- END GENERATED: site-copy -->

    <!-- BEGIN GENERATED: analytics -->
    <!-- END GENERATED: analytics -->

    <!-- BEGIN GENERATED: hosting -->
    <!-- END GENERATED: hosting -->
    """
)


def _write_fixture(root: Path, *, title: str = "Example Hub") -> None:
    (root / "data").mkdir()
    (root / "docs").mkdir()
    (root / "site").mkdir()
    (root / "data" / "site.json").write_text(
        json.dumps(
            {
                "title": title,
                "tagline": "Short line.",
                "description": "A longer line.",
                "about_lead": "Short line. A longer line.",
            }
        ),
        encoding="utf-8",
    )
    (root / "data" / "analytics.json").write_text(
        json.dumps(_ANALYTICS),
        encoding="utf-8",
    )
    (root / "CNAME").write_text("from-cname.example\n", encoding="utf-8")
    (root / "site" / "style.css").write_text(_CSS, encoding="utf-8")
    (root / "docs" / "design.md").write_text(_DESIGN, encoding="utf-8")
    (root / "README.md").write_text(_README, encoding="utf-8")


class DocsFactsTests(unittest.TestCase):
    def test_block_ids(self):
        self.assertEqual(BLOCK_IDS, ("site-copy", "analytics", "hosting", "design-tokens"))

    def test_generate_then_check_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture(root)
            self.assertEqual(generate(root), 0)
            design = (root / "docs" / "design.md").read_text(encoding="utf-8")
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("| `title` | Example Hub |", design)
            self.assertIn("| `title` | Example Hub |", readme)
            self.assertIn("`G-TEST1234`", design)
            self.assertIn("`example.test`, `www.example.test`", readme)
            self.assertIn("| `hostname` | `from-cname.example` |", design)
            self.assertIn("| `target` | GitHub Pages |", readme)
            self.assertIn("| `--canvas` | #ffffff | #0f1115 |", design)
            self.assertIn("| `--only-dark` |  | #abc |", design)
            self.assertNotIn("#000000", design)
            self.assertNotIn("decoy", design)
            self.assertNotIn("design-tokens", readme)
            self.assertEqual(check(root), 0)
            again = generate(root)
            self.assertEqual(again, 0)
            self.assertEqual((root / "docs" / "design.md").read_text(encoding="utf-8"), design)

    def test_seeded_title_fails_until_regenerate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture(root)
            self.assertEqual(generate(root), 0)
            design_path = root / "docs" / "design.md"
            design_path.write_text(
                design_path.read_text(encoding="utf-8").replace("Example Hub", "Wrong Title", 1),
                encoding="utf-8",
            )
            self.assertEqual(check(root), 1)
            self.assertEqual(generate(root), 0)
            self.assertIn("Example Hub", design_path.read_text(encoding="utf-8"))
            self.assertNotIn("Wrong Title", design_path.read_text(encoding="utf-8"))
            self.assertEqual(check(root), 0)

    def test_hosting_json_overrides_cname(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture(root)
            (root / "data" / "hosting.json").write_text(
                json.dumps({"target": "Cloudflare Pages", "hostname": "override.example"}),
                encoding="utf-8",
            )
            text = render_block(root, "hosting")
            self.assertIn("`override.example`", text)
            self.assertIn("Cloudflare Pages", text)
            self.assertNotIn("from-cname.example", text)
            self.assertNotIn("GitHub Pages", text)

    def test_missing_markers_fail_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture(root)
            (root / "README.md").write_text("# Readme\n\nNo markers.\n", encoding="utf-8")
            self.assertEqual(check(root), 1)
            self.assertEqual(generate(root), 1)

    def test_cli_check_on_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture(root)
            script = ROOT / "kit" / "generate_docs.py"
            write = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(write.returncode, 0, write.stderr + write.stdout)
            passed = subprocess.run(
                [sys.executable, str(script), "--check", "--root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(passed.returncode, 0, passed.stderr + passed.stdout)
            self.assertIn("OK generate_docs", passed.stdout)

    def test_hub_tokens_include_canvas_and_skip_later_rules(self):
        text = render_block(ROOT, "design-tokens")
        self.assertIn("| `--canvas` | #ffffff | #0f1115 |", text)
        self.assertIn("| `--page-gutter` | 20px |  |", text)
        self.assertNotIn("| `--page-gutter` | 15px |", text)
        self.assertNotIn("prefers-color-scheme", text)

    def test_hub_docs_match_sources(self):
        self.assertEqual(check(ROOT), 0)


if __name__ == "__main__":
    unittest.main()

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
        target = ROOT / "kit" / "shell.py"
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
            # Vendor current kit tree + PIN (simulates sister at this commit).
            # Use working tree copy; pin check compares to git show, so files
            # must match HEAD. Skip if kit is not yet committed.
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
            # Hand-edit like the 18 Oct / BTT incident
            btt = sister / "kit" / "js" / "back-to-top.js"
            btt.write_text(btt.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            # ensure real drift: append comment
            btt.write_text(btt.read_text(encoding="utf-8") + "// edited\n", encoding="utf-8")
            bad = subprocess.run(
                ["python3", "kit/sync.py", "--check", "--hub-path", str(ROOT)],
                cwd=sister,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("local edit or stale vendor", bad.stderr)


if __name__ == "__main__":
    unittest.main()

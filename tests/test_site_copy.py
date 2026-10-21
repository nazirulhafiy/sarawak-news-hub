#!/usr/bin/env python3
"""Fail when hub title/tagline/description are hand-typed outside data/site.json.

Generated blocks are not hand-typed. ``kit/generate_docs.py`` writes them from
``data/site.json``, and this test skips the marker interiors.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_JSON = ROOT / "data" / "site.json"
SKIP_FILES = {
    SITE_JSON.resolve(),
    (ROOT / "kit" / "fleet-cross-links.json").resolve(),
}

# Production and project text only. Design explorations and build output are out of scope.
SKIP_DIR_NAMES = {
    ".git",
    "dist",
    "design-handoff",
    "__pycache__",
    ".venv",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".pdf",
    ".pyc",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".json",
    ".html",
    ".css",
    ".js",
    ".txt",
    ".yml",
    ".yaml",
    ".svg",
    ".toml",
    ".cfg",
    ".ini",
    "",  # extensionless (e.g. CNAME, AGENTS.md has .md)
}


def load_copy() -> dict[str, str]:
    payload = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    required = ("title", "tagline", "description", "about_lead")
    missing = [key for key in required if not isinstance(payload.get(key), str) or not payload[key].strip()]
    if missing:
        raise AssertionError(f"data/site.json missing fields: {', '.join(missing)}")
    return {key: payload[key].strip() for key in required}


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.resolve() in SKIP_FILES:
            continue
        suffix = path.suffix.lower()
        if suffix in SKIP_SUFFIXES:
            continue
        if suffix not in TEXT_SUFFIXES and path.name not in {"CNAME", "Makefile", "Dockerfile"}:
            # Skip unknown binaries; still scan common text names without a suffix.
            try:
                path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
        files.append(path)
    return sorted(files)


def title_pattern(title: str) -> re.Pattern[str]:
    """Match hub title, not sister brands like AI.Sarawak.News."""
    escaped = re.escape(title)
    return re.compile(rf"(?<![A-Za-z0-9.-]){escaped}(?![A-Za-z0-9.-])")


def iter_checked_lines(text: str):
    """Yield source lines, skipping generated-block interiors."""
    skipping = False
    begin = "<!-- BEGIN GENERATED:"
    end = "<!-- END GENERATED:"
    for line_no, line in enumerate(text.splitlines(), start=1):
        if skipping:
            if end in line:
                skipping = False
            continue
        if begin in line:
            skipping = end not in line
            continue
        yield line_no, line


def find_hand_typed(path: Path, copy: dict[str, str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    rel = path.relative_to(ROOT).as_posix()
    hits: list[str] = []
    checks: list[tuple[str, re.Pattern[str]]] = [
        ("title", title_pattern(copy["title"])),
        ("tagline", re.compile(re.escape(copy["tagline"]))),
        ("description", re.compile(re.escape(copy["description"]))),
    ]
    # about_lead is composed from tagline + description; flag it too if pasted.
    if copy["about_lead"] not in (copy["tagline"], copy["description"]):
        checks.append(("about_lead", re.compile(re.escape(copy["about_lead"]))))

    for line_no, line in iter_checked_lines(text):
        for label, pattern in checks:
            if pattern.search(line):
                hits.append(f"{rel}:{line_no}: hand-typed {label}: {line.strip()}")
    return hits


class SiteCopySourceOfTruthTests(unittest.TestCase):
    def test_site_json_owns_copy_fields(self):
        copy = load_copy()
        self.assertEqual(
            copy["about_lead"],
            f"{copy['tagline']} {copy['description']}",
        )

    def test_no_hand_typed_site_copy_outside_site_json(self):
        copy = load_copy()
        violations: list[str] = []
        for path in iter_source_files():
            violations.extend(find_hand_typed(path, copy))
        if violations:
            sample = "\n".join(violations[:40])
            more = "" if len(violations) <= 40 else f"\n... and {len(violations) - 40} more"
            self.fail(
                "Site title/tagline/description must live only in data/site.json.\n"
                f"Found {len(violations)} hand-typed occurrence(s):\n{sample}{more}"
            )


if __name__ == "__main__":
    unittest.main()

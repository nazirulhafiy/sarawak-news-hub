#!/usr/bin/env python3
"""Favicon contact sheet is a 16, 32, and 48 pixel PNG."""

from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kit.favicon_sheet import (  # noqa: E402
    SHEET_HEIGHT,
    SHEET_WIDTH,
    SIZES,
    read_png,
    render_favicon_sheet,
    write_png,
)


def _ihdr(path: Path) -> tuple[int, int, int]:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    length = struct.unpack(">I", data[8:12])[0]
    assert data[12:16] == b"IHDR"
    assert length == 13
    width, height, bit, color, comp, filt, inter = struct.unpack(">IIBBBBB", data[16:29])
    assert bit == 8 and comp == 0 and filt == 0 and inter == 0
    return width, height, color


class FaviconSheetTests(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(SIZES, (16, 32, 48))
        self.assertEqual(SHEET_WIDTH, 96)
        self.assertEqual(SHEET_HEIGHT, 48)

    def test_png_round_trip(self):
        pixels = [
            [(10, 20, 30, 255), (0, 0, 0, 0)],
            [(1, 2, 3, 4), (255, 255, 255, 128)],
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.png"
            write_png(path, 2, 2, pixels)
            width, height, got = read_png(path)
            self.assertEqual((width, height), (2, 2))
            self.assertEqual(got, pixels)
            self.assertEqual(_ihdr(path), (2, 2, 6))

    def test_apple_touch_sheet_layout(self):
        src = ROOT / "design-handoff" / "favicon-F1" / "apple-touch-icon.png"
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "sheet.png"
            render_favicon_sheet(src, dest)
            self.assertEqual(_ihdr(dest), (SHEET_WIDTH, SHEET_HEIGHT, 6))
            _width, _height, pixels = read_png(dest)
            # 16px and 32px tiles are vertically centered, so the top row is empty there.
            self.assertEqual(pixels[0][8][3], 0)
            self.assertEqual(pixels[0][32][3], 0)
            self.assertGreater(pixels[24][8][3], 200)
            self.assertGreater(pixels[24][32][3], 200)
            self.assertGreater(pixels[24][72][3], 200)


if __name__ == "__main__":
    unittest.main()

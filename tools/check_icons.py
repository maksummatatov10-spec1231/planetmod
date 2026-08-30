#!/usr/bin/env python3
"""PNG integrity and size checks for Cataclysm graphics.

Verifies that every image under graphics/:
  * loads as RGBA,
  * is square,
  * matches the expected size for its path/name,
  * has a non-empty alpha coverage (nothing fully transparent),
  * is not a single solid color (i.e. drawing actually happened).

Usage: python3 tools/check_icons.py
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHICS = os.path.join(ROOT, "graphics")

failures = []


def fail(what):
    failures.append(what)
    print("FAIL:", what)


def expected_size(rel_path, name):
    parts = rel_path.split(os.sep)
    if name == "thumbnail.png":
        return 144
    if name == "starmap-cataclysm.png":
        return 512
    if parts[0] == "technology" or parts[0] == "achievement":
        return 128
    if parts[0] == "entity":
        if parts[1] in ("stormite-ore", "astrite-ore"):
            return 1024
        return 128
    if parts[0] == "icons":
        if name == "cataclysm.png":
            return 128
        return 64
    return None  # unknown -> only integrity checks


def main():
    for root, _dirs, files in os.walk(GRAPHICS):
        for f in sorted(files):
            if not f.endswith(".png"):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, GRAPHICS)
            try:
                im = Image.open(path)
                im.load()
            except Exception as exc:
                fail("%s: cannot open: %s" % (rel, exc))
                continue
            if im.mode != "RGBA":
                fail("%s: mode %s, expected RGBA" % (rel, im.mode))
            w, h = im.size
            if w != h:
                fail("%s: not square (%dx%d)" % (rel, w, h))
            exp = expected_size(rel, f)
            if exp is not None and w != exp:
                fail("%s: size %d, expected %d" % (rel, w, exp))
            alpha = im.getchannel("A")
            bbox = alpha.getbbox()
            if bbox is None:
                fail("%s: fully transparent" % rel)
            elif bbox[0] < 2 or bbox[2] > w - 2 or bbox[1] < 2 or bbox[3] > h - 2:
                # content touching the very edge is suspicious but not fatal
                print("WARN %s: content touches edge" % rel)
            # fraction of non-transparent pixels
            coverage = alpha.getextrema()[1]
            if coverage == 0:
                fail("%s: no opaque pixels" % rel)
            # not solid: count distinct colors after quantization
            quantized = im.convert("RGB").quantize(colors=16, method=Image.MEDIANCUT)
            if len(quantized.getcolors()) <= 1:
                fail("%s: appears to be a single solid color" % rel)
            print("OK  %-58s %dx%d" % (rel, w, h))

    print()
    if failures:
        print("%d FAILURE(S)" % len(failures))
        sys.exit(1)
    print("ALL ICON CHECKS PASSED")


if __name__ == "__main__":
    main()

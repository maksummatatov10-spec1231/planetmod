#!/usr/bin/env python3
"""Build release zip archives for the Cataclysm mod.

Produces release/<mod-name>_<version>.zip with info.json at the zip root
(the layout Factorio expects for mod zips placed into the mods/ directory).

Only distribution files are included: scripts, prototypes, locale, graphics,
migrations (if any), docs. Dev-only folders (tools/, docs/, .git, release/)
are excluded.

Usage: python3 tools/make_release.py [--check]
  --check   also verify the produced zip (required files, info.json at root)
"""

import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_DIR = os.path.join(ROOT, "release")

INCLUDE = [
    "info.json",
    "data.lua",
    "data-updates.lua",
    "data-final-fixes.lua",
    "control.lua",
    "settings.lua",
    "changelog.txt",
    "LICENSE.md",
    "README.md",
    "prototypes",
    "locale",
    "graphics",
    "migrations",
]

EXCLUDE_DIRS = {"__pycache__", ".git"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".pyj")


def collect_files():
    """Yield (absolute_path, arcname) for every distribution file."""
    for item in INCLUDE:
        path = os.path.join(ROOT, item)
        if not os.path.exists(path):
            continue  # migrations/ may not exist yet
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for name in sorted(files):
                    if name.endswith(EXCLUDE_SUFFIXES):
                        continue
                    full = os.path.join(root, name)
                    arc = os.path.relpath(full, ROOT).replace(os.sep, "/")
                    yield full, arc
        else:
            yield path, item


def build():
    with open(os.path.join(ROOT, "info.json"), "r", encoding="utf-8") as fh:
        info = json.load(fh)
    name = info["name"]
    version = info["version"]
    os.makedirs(RELEASE_DIR, exist_ok=True)
    out = os.path.join(RELEASE_DIR, "%s_%s.zip" % (name, version))

    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, arc in collect_files():
            zf.write(full, arc)
            count += 1

    size = os.path.getsize(out)
    print("built %s (%d files, %.1f KiB)" % (os.path.relpath(out, ROOT), count, size / 1024.0))
    return out


def check(out):
    required = [
        "info.json", "data.lua", "data-updates.lua", "data-final-fixes.lua",
        "control.lua", "settings.lua", "prototypes/planet.lua",
        "prototypes/map-gen.lua", "locale/en/cataclysm.cfg",
        "locale/ru/cataclysm.cfg", "locale/de/cataclysm.cfg",
        "graphics/thumbnail.png", "graphics/icons/cataclysm.png",
    ]
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
        for r in required:
            if r not in names:
                print("FAIL: missing %s" % r)
                sys.exit(1)
        with zf.open("info.json") as fh:
            info = json.load(fh)
        print("check: info.json at root OK (name=%s version=%s)"
              % (info["name"], info["version"]))
    # no path traversal / absolute paths
    for n in names:
        if n.startswith("/") or ".." in n:
            print("FAIL: suspicious path: %s" % n)
            sys.exit(1)
    print("check: %d entries, no suspicious paths" % len(names))
    print("ALL RELEASE CHECKS PASSED")


def main():
    out = build()
    if "--check" in sys.argv:
        check(out)


if __name__ == "__main__":
    main()

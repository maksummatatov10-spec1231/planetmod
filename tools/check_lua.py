#!/usr/bin/env python3
"""Static consistency checks for the Cataclysm mod.

Checks (no Factorio needed):
  1. Lua syntax of every .lua file (via luaparser).
  2. Every `__cataclysm__/graphics/...` reference points to an existing file.
  3. Locale key parity between en/ru/de (mod + prototypes + messages).
  4. Every recipe is unlocked by at least one technology effect.
  5. Every technology icon and achievement icon file exists.

Usage: python3 tools/check_lua.py
"""

import os
import re
import sys

from luaparser import ast
from luaparser import astnodes
from luaparser.astnodes import Chunk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LUA_DIRS = ["", "prototypes", "tools"]
LOCALE_DIR = os.path.join(ROOT, "locale")

GRAPHICS_RE = re.compile(r"__cataclysm__/(graphics/[A-Za-z0-9_\-./]+)")
GRAPHICS_SUBDIR_RE = re.compile(
    r"__cataclysm__/graphics/(icons|technology|achievement|entity)/([A-Za-z0-9_\-]+)\.png"
)

failures = []


def fail(what):
    failures.append(what)
    print("FAIL:", what)


def all_lua_files():
    for root, _dirs, files in os.walk(ROOT):
        if ".git" in root:
            continue
        for f in sorted(files):
            if f.endswith(".lua"):
                yield os.path.join(root, f)


def check_syntax():
    for path in all_lua_files():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                source = fh.read()
            parsed = ast.parse(source)
            if not isinstance(parsed, Chunk):
                raise RuntimeError("parse produced %r" % type(parsed))
        except Exception as exc:  # LuaSyntaxError or IOError
            fail("%s: syntax error: %s" % (os.path.relpath(path, ROOT), exc))
        else:
            print("OK  syntax:", os.path.relpath(path, ROOT))


def check_graphics_refs():
    for path in all_lua_files():
        rel = os.path.relpath(path, ROOT)
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        for match in GRAPHICS_RE.finditer(source):
            target = os.path.join(ROOT, match.group(1).replace("/", os.sep))
            if not os.path.exists(target):
                fail("%s: missing graphics file: %s" % (rel, match.group(1)))


def parse_locale(lang):
    path = os.path.join(LOCALE_DIR, lang, "cataclysm.cfg")
    if not os.path.exists(path):
        fail("missing locale file: %s" % path)
        return {}
    keys = set()
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("["):
                continue
            key = line.split("=", 1)[0].strip()
            if key:
                keys.add(key)
    return keys


def check_locale_parity():
    en = parse_locale("en")
    for lang in ("ru", "de"):
        keys = parse_locale(lang)
        missing = en - keys
        extra = keys - en
        if missing:
            fail("locale %s missing keys: %s" % (lang, sorted(missing)))
        if extra:
            fail("locale %s has keys not in en: %s" % (lang, sorted(extra)))


def check_recipe_unlock_coverage():
    recipes_path = os.path.join(ROOT, "prototypes", "recipes.lua")
    techs_path = os.path.join(ROOT, "prototypes", "technologies.lua")
    with open(recipes_path, "r", encoding="utf-8") as fh:
        recipes_src = fh.read()
    with open(techs_path, "r", encoding="utf-8") as fh:
        techs_src = fh.read()

    recipe_names = set(re.findall(r"type\s*=\s*\"recipe\",\s*\n\s*name\s*=\s*\"([A-Za-z0-9_\-]+)\"", recipes_src))
    unlocked = set(re.findall(r"unlock\(\s*\"([A-Za-z0-9_\-]+)\"\s*\)", techs_src))
    unlocked |= set(re.findall(r"type\s*=\s*\"unlock-recipe\",\s*\n?\s*recipe\s*=\s*\"([A-Za-z0-9_\-]+)\"", techs_src))
    for name in sorted(recipe_names):
        if name not in unlocked:
            fail("recipe not unlocked by any technology: %s" % name)
    print("OK   recipes:", len(recipe_names), "unlocked:", len(unlocked))


def check_icon_files():
    for path in all_lua_files():
        rel = os.path.relpath(path, ROOT)
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        for subdir, name in GRAPHICS_SUBDIR_RE.findall(source):
            target = os.path.join(ROOT, "graphics", subdir, name + ".png")
            if not os.path.exists(target) and subdir == "entity":
                # machines/items use icons/; only ore sheets live in entity/
                target = os.path.join(ROOT, "graphics", "icons", name + ".png")
            if not os.path.exists(target):
                fail("%s: referenced png not found: graphics/%s/%s.png"
                     % (rel, subdir, name))


def check_recipe_categories():
    """Recipes must use `categories = { ... }` (table), not the pre-2.0
    `category = "..."` field. Factorio 2.x merged category +
    additional_categories into categories; using `category` crashes loading
    with 'In RecipePrototype, category and additional_categories got merged
    into categories table'."""
    recipes_path = os.path.join(ROOT, "prototypes", "recipes.lua")
    with open(recipes_path, "r", encoding="utf-8") as fh:
        source = fh.read()
    tree = ast.parse(source)

    def field_value(table_node, key_name):
        for field in table_node.fields:
            key = field.key
            if isinstance(key, astnodes.Name) and key.id == key_name:
                return field.value
        return None

    def str_val(node):
        if isinstance(node, astnodes.String):
            v = node.s
            if isinstance(v, bytes):
                v = v.decode("utf-8")
            return v
        return None

    checked = 0
    for node in ast.walk(tree):
        if not isinstance(node, astnodes.Table):
            continue
        type_field = field_value(node, "type")
        if type_field is None or str_val(type_field) != "recipe":
            continue
        checked += 1
        if field_value(node, "category") is not None:
            fail("recipe %s: uses legacy `category` field; use `categories = {...}`"
                 % _recipe_name(node, str_val))
        if field_value(node, "categories") is None:
            fail("recipe %s: missing `categories = {...}` (required in 2.x)"
                 % _recipe_name(node, str_val))
    print("OK   recipes categories checked:", checked)


def _recipe_name(recipe_table, str_val):
    name_field = None
    for field in recipe_table.fields:
        key = field.key
        if isinstance(key, astnodes.Name) and key.id == "name":
            name_field = str_val(field.value)
            break
    return name_field or "<unnamed>"


def main():
    check_syntax()
    check_graphics_refs()
    check_locale_parity()
    check_recipe_unlock_coverage()
    check_recipe_categories()
    check_icon_files()
    print()
    if failures:
        print("%d FAILURE(S)" % len(failures))
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()

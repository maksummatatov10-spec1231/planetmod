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
    changes_path = os.path.join(ROOT, "prototypes", "vanilla-changes.lua")
    with open(recipes_path, "r", encoding="utf-8") as fh:
        recipes_src = fh.read()
    with open(techs_path, "r", encoding="utf-8") as fh:
        techs_src = fh.read()
    with open(changes_path, "r", encoding="utf-8") as fh:
        changes_src = fh.read()

    recipe_names = set(re.findall(r"type\s*=\s*\"recipe\",\s*\n\s*name\s*=\s*\"([A-Za-z0-9_\-]+)\"", recipes_src))
    unlocked = set(re.findall(r"unlock\(\s*\"([A-Za-z0-9_\-]+)\"\s*\)", techs_src))
    unlocked |= set(re.findall(r"type\s*=\s*\"unlock-recipe\",\s*\n?\s*recipe\s*=\s*\"([A-Za-z0-9_\-]+)\"", techs_src))
    # recipes granted by data-final-fixes vanilla technology patches
    unlocked |= set(re.findall(r"type\s*=\s*\"unlock-recipe\",\s*\n?\s*recipe\s*=\s*\"([A-Za-z0-9_\-]+)\"", changes_src))
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


def check_achievements():
    """Achievement prototypes must match the Factorio 2.x fields:
      * build-entity-achievement requires `to_build` (the pre-2.0 `entity`
        field is gone and crashes loading).
      * deplete-resource-achievement has no `resource` field in 2.x — using it
        with `resource` silently loses the target; mod uses scripted unlock.
      * change-surface-achievement requires `surface`.
      * research-with-science-pack-achievement requires `science_pack`.
      * produce-achievement requires `item_product`, `amount` AND
        `limited_to_one_game` (required by ProduceAchievementPrototype in
        2.1.17; the engine fails to load without it).
      * produce-per-hour-achievement requires `item_product` and `amount`
        and must NOT have `limited_to_one_game` (no such field on
        ProducePerHourAchievementPrototype)."""
    path = os.path.join(ROOT, "prototypes", "achievements.lua")
    with open(path, "r", encoding="utf-8") as fh:
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

    def has_key(table_node, key_name):
        for field in table_node.fields:
            key = field.key
            if isinstance(key, astnodes.Name) and key.id == key_name:
                return True
        return False

    checked = 0
    for node in ast.walk(tree):
        if not isinstance(node, astnodes.Table):
            continue
        t = str_val(field_value(node, "type"))
        if not t or not t.endswith("achievement"):
            continue
        checked += 1
        name = str_val(field_value(node, "name")) or "<unnamed>"
        if has_key(node, "entity"):
            fail("achievement %s: legacy `entity` field; build-entity-achievement uses `to_build`" % name)
        if t == "build-entity-achievement":
            if field_value(node, "to_build") is None:
                fail("achievement %s: build-entity-achievement requires `to_build`" % name)
        elif t == "deplete-resource-achievement":
            fail("achievement %s: deplete-resource-achievement has no `resource` field in 2.x; use scripted unlock" % name)
        elif t == "change-surface-achievement":
            if field_value(node, "surface") is None:
                fail("achievement %s: change-surface-achievement requires `surface`" % name)
        elif t == "research-with-science-pack-achievement":
            if field_value(node, "science_pack") is None:
                fail("achievement %s: research-with-science-pack-achievement requires `science_pack`" % name)
        elif t == "produce-achievement":
            if field_value(node, "item_product") is None:
                fail("achievement %s: produce-achievement requires `item_product`" % name)
            if field_value(node, "amount") is None:
                fail("achievement %s: produce-achievement requires `amount`" % name)
            if field_value(node, "limited_to_one_game") is None:
                fail("achievement %s: produce-achievement requires `limited_to_one_game` (engine fails to load without it)" % name)
        elif t == "produce-per-hour-achievement":
            if field_value(node, "item_product") is None:
                fail("achievement %s: produce-per-hour-achievement requires `item_product`" % name)
            if field_value(node, "amount") is None:
                fail("achievement %s: produce-per-hour-achievement requires `amount`" % name)
            if has_key(node, "limited_to_one_game"):
                fail("achievement %s: produce-per-hour-achievement has no `limited_to_one_game` field" % name)
    print("OK   achievements checked:", checked)


# ---------------------------------------------------------------------------
# Prototype field allowlists.
#
# Every top-level key of every prototype the mod defines in data stage must
# be a documented field of that prototype type (lua-api.factorio.com/latest,
# version 2.1.17). Sources: docs/API-AUDIT.md. Deep-copies (entities.lua,
# tiles.lua, lightning.lua) inherit validity from the vanilla prototype and
# are validated by the audit doc instead of statically.
# ---------------------------------------------------------------------------

# Generic fields: PrototypeBase + Prototype (valid on every prototype type).
_BASE = {
    "type", "name", "order",
    "localised_name", "localised_description", "factoriopedia_description",
    "subgroup", "hidden", "hidden_in_factoriopedia", "parameter",
    "icons", "icon", "icon_size",
    "factoriopedia_alternative", "custom_tooltip_fields", "factoriopedia_simulation",
}

# EntityPrototype fields shared by entities defined from scratch.
_ENTITY = _BASE | {
    "flags", "minable", "max_health", "collision_box", "collision_mask",
    "selection_box", "render_layer", "autoplace", "map_color",
}

# Fields shared by ItemPrototype and its children (ToolPrototype etc.).
_ITEM_FIELDS = _BASE | {
    "stack_size", "weight", "durability", "durability_description_key",
    "durability_description_value", "place_result",
    "place_as_equipment_result", "fuel_category", "burnt_result",
    "spoil_result", "spoil_quality_min", "spoil_quality_max",
    "spoil_quality_change", "dark_background_icons", "dark_background_icon",
    "dark_background_icon_size", "rocket_launch_products",
}

# {prototype type: allowed top-level fields}. Only types the mod defines in
# data stage with an explicit `type =` field are checked.
PROTO_FIELDS = {
    "item": _ITEM_FIELDS,
    "tool": _ITEM_FIELDS,
    "fluid": _BASE | {
        "default_temperature", "max_temperature", "heat_capacity",
        "base_color", "flow_color", "visualization_color",
        "pressure_to_speed_ratio", "flow_to_energy_ratio", "gas_temperature",
        "fuel_value", "emissions_multiplier", "draw_as_glow", "auto_barrel",
        "spent_fluid", "hidden_in_factoriopedia",
    },
    "recipe": _BASE | {
        "categories", "ingredients", "results", "main_product",
        "energy_required", "enabled", "allow_productivity",
        "maximum_productivity", "emissions_multiplier",
        "requester_paste_multiplier", "overload_multiplier",
        "allow_inserter_overload", "hide_from_stats",
        "hide_from_player_crafting", "hide_from_bonus_gui",
        "allow_decomposition", "allow_as_intermediate",
        "always_show_products", "always_show_ingredients",
        "crafting_machine_tint", "ignore_productivity",
        "show_in_recipe_book", "hidden_from_recipe_book",
    },
    "recipe-category": _BASE,
    "technology": _BASE | {
        "unit", "research_trigger", "prerequisites", "effects", "max_level",
        "upgrade", "enabled", "essential", "visible_when_disabled",
        "ignore_tech_cost_multiplier", "allows_productivity",
        "show_levels_info",
    },
    "item-group": _BASE | {"order_in_recipe"},
    "item-subgroup": _BASE | {"group"},
    "autoplace-control": _BASE | {
        "category", "richness", "can_be_disabled",
        "related_to_fight_achievements",
    },
    "resource": _ENTITY | {
        "stages", "stage_counts", "infinite", "highlight",
        "randomize_visual_position", "map_grid", "minimum", "normal",
        "infinite_depletion_amount", "resource_patch_search_radius",
        "category", "walking_sound", "driving_sound", "stages_effect",
        "effect_animation_period", "effect_animation_period_deviation",
        "effect_darkness_multiplier", "min_effect_alpha", "max_effect_alpha",
        "tree_removal_probability", "tree_removal_max_distance",
        "mining_visualisation_tint",
    },
    "simple-entity": _ENTITY | {
        "count_as_rock_for_filtered_deconstruction", "secondary_draw_order",
        "random_animation_offset", "random_variation_on_create",
        "shuffled_variation_on_chunk_generated", "pictures", "picture",
        "animations", "lower_render_layer", "lower_pictures",
        "stateless_visualisation_variations", "healing_per_tick",
        "repair_speed_modifier", "dying_explosion", "dying_trigger_effect",
        "damaged_trigger_effect", "loot", "order",
    },
    "sound": _BASE | {
        "category", "priority", "aggregation", "allow_random_repeat",
        "audible_distance_modifier", "game_controller_vibration_data",
        "advanced_volume_control", "speed_smoothing_window_size",
        "variations", "filename", "volume", "min_volume", "max_volume",
        "preload", "speed", "min_speed", "max_speed", "modifiers",
    },
    "planet": _BASE | {
        "map_gen_settings", "pollutant_type", "persistent_ambient_sounds",
        "surface_render_parameters", "player_effects",
        "ticks_between_player_effects", "surface_properties",
        "lightning_properties", "map_seed_offset", "entities_require_heating",
        "gravity_pull", "distance", "orientation", "magnitude",
        "parked_platforms_orientation", "label_orientation", "draw_orbit",
        "solar_power_in_space", "asteroid_spawn_influence", "fly_condition",
        "auto_save_on_first_trip", "procession_graphic_catalogue",
        "procession_audio_catalogue", "platform_procession_set",
        "planet_procession_set", "starmap_icons", "starmap_icon",
        "starmap_icon_size", "starmap_icon_orientation",
        "asteroid_spawn_definitions", "platform_surface_render_parameters",
    },
    "space-connection": _BASE | {
        "from", "to", "length", "asteroid_spawn_definitions",
    },
    "noise-expression": _BASE | {"expression", "local_expressions"},
    "noise-function": _BASE | {"parameters", "expression"},
    "build-entity-achievement": _BASE | {
        "to_build", "amount", "limited_to_one_game", "within",
    },
    "produce-achievement": _BASE | {
        "amount", "limited_to_one_game", "item_product", "fluid_product",
    },
    "produce-per-hour-achievement": _BASE | {
        "amount", "item_product", "fluid_product",
    },
    "research-with-science-pack-achievement": _BASE | {"science_pack", "amount"},
    "change-surface-achievement": _BASE | {"surface"},
    "int-setting": _BASE | {
        "setting_type", "default_value", "minimum_value", "maximum_value",
        "allowed_values",
    },
    "bool-setting": _BASE | {"setting_type", "default_value"},
}

# ---------------------------------------------------------------------------
# REQUIRED fields per prototype type.
#
# A field is REQUIRED when the lua-api docs list it without the "optional"
# marker (or when the engine demands it, as proven by a load error), and the
# vanilla data always sets it. Missing required keys crash the game load with
# 'Key "..." not found in property tree at ROOT.<type>.<name>'.
#
# History (both caught by this table now):
#   * produce-achievement without `limited_to_one_game` (0.2.1 crash);
#   * tool (science pack) without `durability` (0.2.2 crash).
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = {
    "item": {"stack_size"},
    "tool": {"durability"},
    "fluid": {"default_temperature", "base_color", "flow_color"},
    "recipe": {"categories", "results"},
    "planet": {"distance", "orientation"},
    "resource": {"stage_counts", "minable"},
    "autoplace-control": {"category"},
    "item-subgroup": {"group"},
    "space-connection": {"from", "to"},
    "noise-expression": {"expression"},
    "noise-function": {"expression"},
    "int-setting": {"setting_type", "default_value"},
    "bool-setting": {"setting_type", "default_value"},
}

# At least one field of each tuple must be present.
OR_REQUIRED_FIELDS = {
    "technology": [("unit", "research_trigger")],
    "simple-entity": [("picture", "animations", "pictures")],
}


def _table_type_str(field_value):
    if isinstance(field_value, astnodes.String):
        v = field_value.s
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        return v
    return None


def _extend_entries(tree):
    """Yield the Table nodes that are direct entries of a `data:extend({...})`
    call — i.e. actual data-stage prototypes. Nested tables (products,
    ingredients, effects, rules) are not prototypes and must not be checked."""
    for node in ast.walk(tree):
        is_extend = False
        if isinstance(node, astnodes.Invoke):  # data:extend({...})
            is_extend = (isinstance(node.source, astnodes.Name)
                         and node.source.id == "data"
                         and isinstance(node.func, astnodes.Name)
                         and node.func.id == "extend")
            args = node.args
        elif isinstance(node, astnodes.Call):  # data.extend({...})
            func = node.func
            is_extend = (isinstance(func, astnodes.Index)
                         and isinstance(func.value, astnodes.Name)
                         and func.value.id == "data"
                         and func.idx is not None
                         and getattr(func.idx, "id", None) == "extend")
            args = node.args
        else:
            continue
        if not is_extend:
            continue
        if not args or not isinstance(args[0], astnodes.Table):
            continue
        for entry in args[0].fields:
            if isinstance(entry.value, astnodes.Table):
                yield entry.value


def _entry_has_field(entry, key_name):
    for field in entry.fields:
        key = field.key
        if isinstance(key, astnodes.Name) and key.id == key_name:
            return True
    return False


def check_prototype_fields():
    """Every data-stage prototype the mod defines with an explicit `type`
    must (a) only use documented fields for that prototype type (allowlists
    above, derived from lua-api 2.1.17 — see docs/API-AUDIT.md) and
    (b) include every REQUIRED field of that type (missing required keys
    crash loading with 'Key ... not found in property tree')."""
    checked = 0
    for path in all_lua_files():
        rel = os.path.relpath(path, ROOT)
        if not rel.endswith(".lua") or rel.startswith("release") or rel.startswith("tools"):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        try:
            tree = ast.parse(source)
        except Exception:
            continue  # syntax errors are reported by check_syntax
        for entry in _extend_entries(tree):
            type_field = None
            for field in entry.fields:
                key = field.key
                if isinstance(key, astnodes.Name) and key.id == "type":
                    type_field = field.value
                    break
            if type_field is None:
                continue
            t = _table_type_str(type_field)
            if t is None or t not in PROTO_FIELDS:
                continue
            name = _proto_name(entry)
            allowed = PROTO_FIELDS[t]
            for field in entry.fields:
                key = field.key
                if not isinstance(key, astnodes.Name):
                    continue
                if key.id not in allowed:
                    fail("%s: %s '%s' has undocumented field `%s` "
                         "(lua-api 2.1.17, see docs/API-AUDIT.md)"
                         % (rel, t, name, key.id))
            for required in REQUIRED_FIELDS.get(t, ()):
                if not _entry_has_field(entry, required):
                    fail("%s: %s '%s' missing REQUIRED field `%s` "
                         "(engine: 'Key ... not found in property tree')"
                         % (rel, t, name, required))
            for group in OR_REQUIRED_FIELDS.get(t, ()):
                if not any(_entry_has_field(entry, k) for k in group):
                    fail("%s: %s '%s' needs at least one of %s"
                         % (rel, t, name, ", ".join(group)))
            checked += 1
    print("OK   prototype fields checked:", checked)


def _proto_name(table_node):
    for field in table_node.fields:
        key = field.key
        if isinstance(key, astnodes.Name) and key.id == "name":
            if isinstance(field.value, astnodes.String):
                v = field.value.s
                if isinstance(v, bytes):
                    v = v.decode("utf-8")
                return v
    return "<unnamed>"


def main():
    check_syntax()
    check_graphics_refs()
    check_locale_parity()
    check_recipe_unlock_coverage()
    check_recipe_categories()
    check_achievements()
    check_icon_files()
    check_prototype_fields()
    print()
    if failures:
        print("%d FAILURE(S)" % len(failures))
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()

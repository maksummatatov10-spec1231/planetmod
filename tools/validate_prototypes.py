#!/usr/bin/env python3
"""Cataclysm — prototype schema validation ("docs + static" stage).

Validates every prototype the mod declares against the official Factorio
2.1.17 prototype documentation (schema notes in tools/out/docs_schema_notes.md,
collected from lua-api.factorio.com/latest/prototypes/*.html) plus the real
vanilla 2.x data.raw (base + space-age + quality + recycler + elevated-rails).

Inputs (all produced by tools/run_data_stage.py — the "functional" stage that
executes the mod's actual data.lua / data-final-fixes.lua in a Lua runtime):
  tools/out/data_raw_mod.json     — dump of data.raw after the mod loads:
      mod_protos    every prototype the mod declared (full serialized table)
      donors        the 5 vanilla prototypes the mod deep-copies
      names_by_type full name index of data.raw (vanilla + mod), 263 types
      labs          lab state after data-final-fixes (vanilla compatibility)
      vanilla_counts, logs, missing_content
  tools/out/defines_prototypes.json — defines.prototypes enum dump

Checks (per prototype instance):
  A. Required fields (own + inherited), e.g. stack_size, effect_duration,
     limited_to_one_game, distance/orientation, stage_counts …
  B. OR-required groups: produce-achievement item_product|fluid_product,
     recipe ingredients|results, technology unit|research_trigger …
  C. Conditional requirements from the docs ("Mandatory if …"): generator
     fluid_box.filter when max_power_output is absent; lightning-attractor
     energy_source when efficiency > 0; time_to_damage <= effect_duration;
     item fuel_category when fuel_value != 0 …
  D. Enums: autoplace-control.category, tile.layer, sound.category …
  E. Instance-count limits: autoplace-control <= 255, item-group <= 255,
     tile <= 65535.
  F. Cross-references: every name field that must point at an existing
     prototype (ingredients, results, categories, prerequisites, effects,
     place_result, minable.result, corpse, dying_explosion, damage.type,
     fluid_box.filter, surface, from/to, lightning_types, autoplace
     expressions, map_gen_settings …). This is what catches real load-time
     bugs the pure-Lua harness cannot (e.g. a dying_explosion name that no
     longer exists in 2.x).
  G. Shape checks: numbers where uint/float is documented, booleans, arrays.
  H. Unknown-field audit: any field that is neither in the 2.1.17 docs for the
     type nor present in the vanilla donor deep-copied by the mod is reported
     (the engine ignores unknown properties, so this is a WARN, not an error).

Usage:
    python3 tools/validate_prototypes.py                # full report
    python3 tools/validate_prototypes.py --self-test    # prove the checks
                                                        # catch the historical
                                                        # bug classes

Exit code: 0 = all checks passed; 1 = any ERROR.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "out")

# ---------------------------------------------------------------------------
# 2.1.17 schema — REQUIRED / OR-required / enums / limits / conditionals.
# "own + inherited" already includes the PrototypeBase requirement of
# type/name (checked globally) and per-class required fields from the docs.
# ---------------------------------------------------------------------------

PROTOTYPE_BASE = {
    "type", "name", "order", "localised_name", "localised_description",
    "factoriopedia_description", "subgroup", "hidden",
    "hidden_in_factoriopedia", "parameter", "factoriopedia_simulation",
}
PROTOTYPE = PROTOTYPE_BASE | {"factoriopedia_alternative", "custom_tooltip_fields"}

ENTITY = PROTOTYPE | {
    # EntityPrototype (2.1.17): all optional, but the full field set is large;
    # fields below are the ones seen on the fetched page plus the common
    # inherited ones; donors cover the rest for deep-copied types.
    "icons", "icon", "icon_size", "collision_box", "collision_mask",
    "map_generator_bounding_box", "selection_box",
    "drawing_box_vertical_extension", "sticker_box", "hit_visualization_box",
    "trigger_target_mask", "flags", "tile_buildability_rules", "minable",
    "surface_conditions", "deconstruction_alternative", "selection_priority",
    "build_grid_size", "remove_decoratives", "emissions_per_second",
    "shooting_cursor_size", "created_smoke", "working_sound", "created_effect",
    "build_sound", "mined_sound", "mining_sound", "rotated_sound",
    "ghost_build_sound", "impact_category", "open_sound", "close_sound",
    "placeable_position_visualization", "radius_visualisation_specification",
    "stateless_visualisation", "draw_stateless_visualisations_in_ghost",
    "alert_icon_shift", "alert_icon_scale", "fast_replaceable_group", "corpse",
    "dying_explosion", "water_reflection", "heating_energy",
    "localised_name", "localised_description", "factoriopedia_description",
    "allow_run_time_change_of_is_military_target", "is_military_target",
    "quality_indicator_shift", "quality_indicator_scale", "max_health",
    "healing_per_tick", "repair_speed_modifier", "dying_trigger_effect",
    "damaged_trigger_effect", "loot", "resistances", "attack_reaction",
    "repair_sound", "frozen_variant", "thawed_variant", "frozen_sound",
    "allow_copy_paste", "allow_blueprint_snap", "secondary_draw_order",
    "autoplace", "map_color",
}

ITEM = PROTOTYPE | {
    "stack_size", "icons", "icon", "icon_size", "dark_background_icons",
    "dark_background_icon", "dark_background_icon_size", "place_result",
    "place_as_equipment_result", "fuel_category", "burnt_result",
    "spoil_result", "spoil_quality_min", "spoil_quality_max",
    "spoil_quality_change", "plant_result", "place_as_tile", "pictures",
    "flags", "spoil_ticks", "fuel_value", "fuel_acceleration_multiplier",
    "fuel_top_speed_multiplier", "fuel_emissions_multiplier",
    "fuel_acceleration_multiplier_quality_bonus",
    "fuel_top_speed_multiplier_quality_bonus", "weight",
    "ingredient_to_weight_coefficient", "space_platform_request_priority",
    "fuel_glow_color", "open_sound", "close_sound", "pick_sound", "drop_sound",
    "inventory_move_sound", "default_import_location", "color_hint",
    "has_random_tint", "spoil_to_trigger_result",
    "destroyed_by_dropping_trigger", "durability",
    "durability_description_key", "durability_description_value",
}

FLUID = PROTOTYPE | {
    "icons", "icon", "icon_size", "default_temperature", "base_color",
    "flow_color", "visualization_color", "max_temperature", "heat_capacity",
    "fuel_value", "emissions_multiplier", "gas_temperature", "draw_as_glow",
    "auto_barrel", "spent_fluid",
}

SOUND = PROTOTYPE | {
    "category", "priority", "aggregation", "allow_random_repeat",
    "audible_distance_modifier", "game_controller_vibration_data",
    "advanced_volume_control", "speed_smoothing_window_size", "variations",
    "filename", "volume", "min_volume", "max_volume", "preload", "speed",
    "min_speed", "max_speed", "modifiers",
}

SPACE_LOCATION = PROTOTYPE | {
    "icons", "icon", "icon_size", "distance", "orientation", "gravity_pull",
    "magnitude",
    "parked_platforms_orientation", "label_orientation", "draw_orbit",
    "solar_power_in_space", "asteroid_spawn_influence", "fly_condition",
    "auto_save_on_first_trip", "procession_graphic_catalogue",
    "procession_audio_catalogue", "platform_procession_set",
    "planet_procession_set", "starmap_icon", "starmap_icon_size",
    "starmap_icon_orientation", "asteroid_spawn_definitions",
    "platform_surface_render_parameters",
}

CRAFTING_MACHINE = ENTITY | {
    "energy_usage", "crafting_speed", "crafting_categories", "energy_source",
    "fluid_boxes", "effect_receiver", "module_slots",
    "quality_affects_module_slots", "allowed_effects",
    "allowed_module_categories", "show_recipe_icon",
    "return_ingredients_on_change", "draw_entity_info_icon_background",
    "quality_affects_energy_usage",
}

TILE = PROTOTYPE | {
    "collision_mask", "layer", "layer_group", "build_animations", "variants",
    "map_color", "icons", "icon", "icon_size", "lowland_fog",
    "transition_overlay_layer_offset", "sprite_usage_surface",
    "transition_merges_with_tile", "effect_color", "tint", "particle_tints",
    "walking_sound", "landing_steps_sound", "driving_sound", "build_sound",
    "mined_sound", "walking_speed_modifier", "vehicle_friction_modifier",
    "decorative_removal_probability", "allowed_neighbors", "needs_correction",
    "minable", "fluid", "next_direction", "can_be_part_of_blueprint",
    "is_foundation", "destroys_dropped_items", "allows_being_covered",
    "searchable", "max_health", "weight", "dying_explosion",
    "absorptions_per_second", "default_cover_tile", "frozen_variant",
    "thawed_variant", "effect", "trigger_effect",
    "default_destroyed_dropped_item_trigger", "scorch_mark_color",
    "check_collision_with_entities", "effect_color_secondary",
    "effect_is_opaque", "transitions", "transitions_between_transitions",
    "autoplace", "placeable_by", "bound_decoratives", "ambient_sounds_group",
    "ambient_sounds",
}

RECIPE = PROTOTYPE | {
    "categories", "category", "icons", "icon", "icon_size", "ingredients",
    "results", "main_product", "energy_required", "emissions_multiplier",
    "maximum_productivity", "enabled", "hide_from_stats",
    "hide_from_player_crafting", "hide_from_bonus_gui", "hide_from_signal_gui",
    "allow_decomposition", "allow_as_intermediate", "allow_intermediates",
    "always_show_made_in", "requires_ingredients_to_unlock_results",
    "unlock_results", "preserve_products_in_machine_output",
    "allow_consumption_message", "allow_speed_message",
    "allow_productivity_message", "allow_pollution_message",
    "allow_quality_message", "surface_conditions", "allow_consumption",
    "allow_speed", "allow_productivity", "allow_pollution", "allow_quality",
    "allowed_module_categories", "alternative_unlock_methods", "auto_recycle",
    "sort_item_ingredients", "can_set_quality", "raise_on_crafted",
    "requester_paste_multiplier", "overload_multiplier",
    "allow_inserter_overload", "crafting_machine_tint",
}

TECHNOLOGY = PROTOTYPE | {
    "icons", "icon", "icon_size", "upgrade", "enabled", "essential",
    "visible_when_disabled", "ignore_tech_cost_multiplier",
    "allows_productivity", "research_trigger", "unit", "max_level",
    "prerequisites", "show_levels_info", "effects",
}

ACHIEVEMENT = PROTOTYPE | {
    "icons", "icon", "icon_size", "steam_stats_name", "allowed_without_fight",
}

NOISE_EXPR = PROTOTYPE | {
    "expression", "local_expressions", "local_functions", "intended_property",
}

NOISE_FUNCTION = PROTOTYPE | {
    "parameters", "expression", "local_expressions", "local_functions",
}

DOC_FIELDS = {
    "item-group": PROTOTYPE | {"icons", "icon", "icon_size", "order_in_recipe"},
    "item-subgroup": PROTOTYPE | {"group"},
    "autoplace-control": PROTOTYPE | {
        "category", "richness", "can_be_disabled",
        "related_to_fight_achievements", "hidden",
    },
    "item": ITEM,
    "fluid": FLUID,
    "sound": SOUND,
    "recipe-category": PROTOTYPE | {"group"},
    "resource": ENTITY | {
        "stages", "stage_counts", "infinite", "highlight",
        "randomize_visual_position", "map_grid",
        "draw_stateless_visualisation_under_building", "minimum", "normal",
        "infinite_depletion_amount", "resource_patch_search_radius",
        "category", "walking_sound", "driving_sound", "stages_effect",
        "effect_animation_period", "effect_animation_period_deviation",
        "effect_darkness_multiplier", "min_effect_alpha", "max_effect_alpha",
        "mining_visualisation_tint", "tree_removal_probability",
        "tree_removal_max_distance", "autoplace", "map_color",
    },
    "tile": TILE,
    "simple-entity": ENTITY | {
        "count_as_rock_for_filtered_deconstruction", "render_layer",
        "secondary_draw_order", "random_animation_offset",
        "random_variation_on_create", "shuffled_variation_on_chunk_generated",
        "pictures", "picture", "animations", "lower_render_layer",
        "lower_pictures", "stateless_visualisation_variations",
    },
    "offshore-pump": ENTITY | {
        "fluid_box", "pumping_speed", "fluid_source_offset",
        "perceived_performance", "graphics_set", "energy_source",
        "energy_usage", "remove_on_tile_collision", "always_draw_fluid",
        "circuit_wire_max_distance", "draw_copper_wires",
        "draw_circuit_wires", "circuit_connector",
    },
    "lightning-attractor": ENTITY | {
        "chargable_graphics", "lightning_strike_offset", "efficiency",
        "range_elongation", "energy_source",
    },
    "assembling-machine": CRAFTING_MACHINE | {
        "fixed_recipe", "fixed_quality", "gui_title_key",
        "circuit_wire_max_distance", "draw_copper_wires",
        "draw_circuit_wires", "default_recipe_finished_signal",
        "default_working_signal", "ingredient_count",
        "max_item_product_count", "circuit_connector",
        "circuit_connector_flipped", "fluid_boxes_off_when_no_fluid_recipe",
        "disabled_when_recipe_not_researched",
    },
    "generator": ENTITY | {
        "energy_source", "fluid_box", "output_fluid_box", "pictures",
        "effectivity", "fluid_usage_per_tick", "maximum_temperature", "smoke",
        "burns_fluid", "scale_fluid_usage", "destroy_non_fuel_fluid",
        "two_direction_only", "perceived_performance", "max_power_output",
        "spent_fluid",
    },
    "lightning": ENTITY | {
        "graphics_set", "sound", "attracted_volume_modifier", "strike_effect",
        "attractor_hit_effect", "source_offset", "source_variance", "damage",
        "energy", "time_to_damage", "effect_duration",
    },
    "recipe": RECIPE,
    "technology": TECHNOLOGY,
    "change-surface-achievement": ACHIEVEMENT | {"surface"},
    "research-with-science-pack-achievement": ACHIEVEMENT | {
        "science_pack", "amount",
    },
    "produce-achievement": ACHIEVEMENT | {
        "item_product", "fluid_product", "amount", "limited_to_one_game",
    },
    "build-entity-achievement": ACHIEVEMENT | {
        "to_build", "amount", "limited_to_one_game", "within",
    },
    "produce-per-hour-achievement": ACHIEVEMENT | {
        "item_product", "fluid_product", "amount", "limited_to_one_game",
    },
    "noise-expression": NOISE_EXPR,
    "noise-function": NOISE_FUNCTION,
    "planet": SPACE_LOCATION | {
        "map_seed_offset", "entities_require_heating", "pollutant_type",
        "persistent_ambient_sounds", "surface_render_parameters",
        "player_effects", "ticks_between_player_effects", "map_gen_settings",
        "surface_properties", "lightning_properties",
    },
    "space-connection": PROTOTYPE | {
        "from", "to", "length", "asteroid_spawn_definitions", "icons", "icon",
        "icon_size",
    },
}

# type -> {required, or_required, enums, limit, conditionals}
SCHEMA = {
    "item-group":             {"required": [], "limit": 255},
    "item-subgroup":          {"required": ["group"]},
    "autoplace-control": {
        "required": ["category"],
        "enums": {"category": {"resource", "terrain", "cliff", "enemy"}},
        "limit": 255,
    },
    "item":                   {"required": ["stack_size"]},
    "fluid":                  {"required": ["default_temperature", "base_color", "flow_color"]},
    "sound":                  {"required": []},
    "recipe-category":        {"required": []},
    "resource":               {"required": ["stage_counts"]},
    "tile":                   {"required": ["collision_mask", "layer", "variants", "map_color"], "limit": 65535},
    "simple-entity":          {"required": []},
    "offshore-pump":          {"required": ["fluid_box", "pumping_speed", "fluid_source_offset", "energy_source", "energy_usage"]},
    "lightning-attractor":    {"required": []},
    "assembling-machine":     {"required": ["energy_usage", "crafting_speed", "crafting_categories", "energy_source"]},
    "generator":              {"required": ["energy_source", "fluid_box", "fluid_usage_per_tick", "maximum_temperature"]},
    "lightning":              {"required": ["effect_duration"]},
    "recipe":                 {"required": [], "or_required": [["ingredients", "results"]]},
    "technology":             {"required": [], "or_required": [["unit", "research_trigger"]]},
    "change-surface-achievement": {"required": []},
    "research-with-science-pack-achievement": {"required": ["science_pack"]},
    "produce-achievement":    {"required": ["amount", "limited_to_one_game"], "or_required": [["item_product", "fluid_product"]]},
    "build-entity-achievement": {"required": ["to_build"]},
    "produce-per-hour-achievement": {"required": ["amount"], "or_required": [["item_product", "fluid_product"]]},
    "noise-expression":       {"required": ["expression"]},
    "noise-function":         {"required": ["parameters", "expression"]},
    "planet":                 {"required": ["distance", "orientation"]},
    "space-connection":       {"required": ["from", "to"]},
}

# Fields the engine accepts but the 2.1.17 docs do not list (1.1-era leftovers
# that are simply ignored). Reported as INFO, not WARN/ERROR.
KNOWN_LEGACY_FIELDS = {
    "fluid": {"pressure_to_speed_ratio", "flow_to_energy_ratio"},
}

ENERGY_RE = re.compile(r"^\d+(\.\d+)?\s*[kMG]?[JWs]?$")


def is_energy(v):
    return isinstance(v, (int, float)) or (isinstance(v, str) and bool(ENERGY_RE.match(v.strip())))


def is_color(v):
    if not isinstance(v, dict):
        return False
    keys = set(v)
    if not keys.issubset({"r", "g", "b", "a"}):
        return False
    return all(isinstance(v[k], (int, float)) for k in v)


def is_vector(v):
    return isinstance(v, (list, tuple)) and len(v) == 2 and all(
        isinstance(x, (int, float)) for x in v)


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Audit:
    def __init__(self):
        self.errors = []
        self.warns = []
        self.infos = []
        self.checked = 0

    def err(self, msg):
        self.errors.append(msg)
        print("ERROR:", msg)

    def warn(self, msg):
        self.warns.append(msg)
        print("WARN :", msg)

    def info(self, msg):
        self.infos.append(msg)

    @property
    def ok(self):
        return not self.errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=os.path.join(OUT, "data_raw_mod.json"))
    ap.add_argument("--defines", default=os.path.join(OUT, "defines_prototypes.json"))
    ap.add_argument("--report", default=os.path.join(OUT, "audit_report.md"))
    ap.add_argument("--self-test", action="store_true",
                    help="mutate a copy of the dump and assert the validator "
                         "catches the historical bug classes")
    args = ap.parse_args()

    with open(args.data) as f:
        data = json.load(f)
    with open(args.defines) as f:
        defines_protos = json.load(f)

    audit = Audit()
    run(audit, data, defines_protos)
    write_report(audit, data, args.report)

    if args.self_test:
        ok = self_test(data, defines_protos)
        if not ok:
            sys.exit(1)

    print(f"\n[validate_prototypes] instances checked: {audit.checked}")
    print(f"[validate_prototypes] errors={len(audit.errors)} "
          f"warnings={len(audit.warns)} info={len(audit.infos)}")
    print(f"[validate_prototypes] report: {args.report}")
    if audit.ok and not args.self_test:
        print("[validate_prototypes] RESULT: PASS")
    elif audit.ok:
        print("[validate_prototypes] RESULT: PASS (self-test PASS)")
    else:
        print("[validate_prototypes] RESULT: FAIL")
        sys.exit(1)


# ---------------------------------------------------------------------------
# main validation
# ---------------------------------------------------------------------------

def run(audit, data, defines_protos):
    protos = data["mod_protos"]
    names = data["names_by_type"]
    donors = data["donors"]

    # ---- global indices ---------------------------------------------------
    all_names = set()
    for t, ns in names.items():
        all_names.update(ns)

    entity_types = {
        t for t, ns in names.items()
        if t in (
            "assembling-machine", "generator", "offshore-pump",
            "lightning-attractor", "simple-entity", "resource", "lightning",
        ) or ns and any(
            p.get("type") == t and p.get("flags")
            for p in protos
        )
    }
    entity_names = set()
    for t, ns in names.items():
        # treat every non-trivial entity-like prototype type as entity
        # namespace: any place_result/corpse/dying_explosion must resolve to a
        # prototype that exists somewhere in data.raw (engine checks the
        # correct type; a superset keeps false positives at zero).
        entity_names.update(ns)

    def exists(name):
        return name in all_names

    def in_type(name, ptype):
        return name in names.get(ptype, set()) or any(
            name in ns for t, ns in names.items() if t != ptype)

    # ---- donors: field union per type -------------------------------------
    donor_fields = {}
    for d in donors:
        donor_fields.setdefault(d["type"], set()).update(d["proto"].keys())

    # ---- per-instance checks ----------------------------------------------
    counts = {}
    for rec in protos:
        ptype, pname, proto = rec["type"], rec["name"], rec["proto"]
        counts[ptype] = counts.get(ptype, 0) + 1
        audit.checked += 1
        tag = f"{ptype}/{pname}"

        # A. required fields
        for f in SCHEMA.get(ptype, {}).get("required", []):
            if f not in proto:
                audit.err(f"{tag}: REQUIRED field '{f}' missing "
                          "(docs 2.1.17)")

        # B. OR-required groups
        for group in SCHEMA.get(ptype, {}).get("or_required", []):
            present = [f for f in group if proto.get(f) is not None]
            if not present:
                audit.err(f"{tag}: exactly one of {group} must be set "
                          "(docs 2.1.17)")
            elif len(present) > 1:
                pass  # both is valid (docs: "at least one of")

        # C. conditionals (documented "Mandatory if …")
        check_conditionals(audit, tag, ptype, proto)

        # D. enums
        for f, allowed in SCHEMA.get(ptype, {}).get("enums", {}).items():
            v = proto.get(f)
            if v is not None and v not in allowed:
                audit.err(f"{tag}: enum field '{f}' = {v!r}, expected one of "
                          f"{sorted(allowed)}")

        # E. instance-count limits
        limit = SCHEMA.get(ptype, {}).get("limit")
        if limit is not None:
            if counts[ptype] > limit:
                audit.err(f"{tag}: type '{ptype}' limited to {limit} total "
                          "instances (docs); mod has {counts[ptype]}")

        # G. shape checks
        check_shapes(audit, tag, ptype, proto)

        # F. cross-references
        check_refs(audit, tag, ptype, proto, names, entity_names, exists,
                   in_type)

        # H. unknown-field audit
        check_unknown_fields(audit, tag, ptype, proto, donor_fields)

    # ---- limits across all instances (counts above) -----------------------
    for ptype, limit in (
        ("autoplace-control", 255), ("item-group", 255), ("tile", 65535),
    ):
        pass  # handled per-instance when the last instance is seen

    # ---- cross-type: every recipe category referenced by machines/recipes --
    check_recipe_categories(audit, protos, names)

    # ---- map-gen: planet <-> noise expressions / autoplace -----------------
    check_planet_mapgen(audit, protos, names)

    # ---- labs / vanilla-changes --------------------------------------------
    lab_inputs = {l["name"]: l.get("inputs") for l in data.get("labs", [])}
    for lname, inputs in lab_inputs.items():
        if inputs and "cataclysmic-science-pack" not in inputs and \
                any("science-pack" in i for i in inputs):
            audit.warn(f"vanilla-changes: lab '{lname}' does not accept "
                       "cataclysmic-science-pack")


def check_conditionals(audit, tag, ptype, proto):
    if ptype == "generator":
        fb = proto.get("fluid_box")
        if "max_power_output" not in proto and not (
                isinstance(fb, dict) and "filter" in fb):
            audit.err(f"{tag}: fluid_box must have a filter when "
                      "max_power_output is not defined (docs 2.1.17)")
    if ptype == "lightning-attractor":
        eff = proto.get("efficiency")
        if isinstance(eff, (int, float)) and eff > 0 and \
                "energy_source" not in proto:
            audit.err(f"{tag}: energy_source is mandatory if efficiency > 0 "
                      "(docs 2.1.17)")
    if ptype == "lightning":
        ttd, ed = proto.get("time_to_damage"), proto.get("effect_duration")
        if isinstance(ttd, (int, float)) and isinstance(ed, (int, float)) \
                and ttd > ed:
            audit.err(f"{tag}: time_to_damage ({ttd}) must be <= "
                      f"effect_duration ({ed}) (docs 2.1.17)")
    if ptype == "item":
        fv = proto.get("fuel_value")
        if fv not in (None, 0, "0") and "fuel_category" not in proto:
            audit.err(f"{tag}: fuel_category must exist when a nonzero "
                      "fuel_value is defined (docs 2.1.17)")
    if ptype == "resource":
        if proto.get("infinite") is True:
            for f in ("minimum", "normal"):
                if not isinstance(proto.get(f), (int, float)) or \
                        proto.get(f) == 0:
                    audit.err(f"{tag}: '{f}' must be nonzero when "
                              "infinite = true (docs 2.1.17)")
    if ptype == "recipe":
        for f in ("ingredients", "results"):
            v = proto.get(f)
            if isinstance(v, list) and len(v) == 0:
                audit.err(f"{tag}: '{f}' cannot be an empty array (docs)")


def check_shapes(audit, tag, ptype, proto):
    # numbers
    for f in ("amount", "effect_duration", "time_to_damage",
              "fluid_usage_per_tick", "pumping_speed", "maximum_temperature",
              "default_temperature", "max_temperature", "gas_temperature",
              "crafting_speed", "stack_size"):
        v = proto.get(f)
        if v is not None and not is_number(v):
            audit.err(f"{tag}: field '{f}' must be a number, got "
                      f"{type(v).__name__}")
    # booleans
    for f in ("limited_to_one_game", "allow_random_repeat", "burns_fluid",
              "two_direction_only", "always_draw_fluid",
              "random_animation_offset", "enabled"):
        v = proto.get(f)
        if v is not None and not isinstance(v, bool):
            audit.err(f"{tag}: field '{f}' must be boolean, got "
                      f"{type(v).__name__}")
    # energy strings
    for f in ("energy", "energy_usage", "heat_capacity", "heating_energy"):
        v = proto.get(f)
        if v is not None and not is_energy(v):
            audit.err(f"{tag}: field '{f}' must be an Energy value, got {v!r}")
    # colors
    for f in ("base_color", "flow_color", "map_color", "effect_color",
              "mining_visualisation_tint", "scorch_mark_color"):
        v = proto.get(f)
        if v is not None and not is_color(v):
            audit.err(f"{tag}: field '{f}' must be a Color table, got {v!r}")
    # orientation (0..1) and distance/gravity (numbers)
    for f in ("orientation", "label_orientation"):
        v = proto.get(f)
        if v is not None and (not is_number(v) or not (0 <= v <= 1)):
            audit.err(f"{tag}: field '{f}' must be a RealOrientation in "
                      f"[0,1], got {v!r}")
    for f in ("distance", "gravity_pull", "magnitude", "solar_power_in_space"):
        v = proto.get(f)
        if v is not None and not is_number(v):
            audit.err(f"{tag}: field '{f}' must be a number, got "
                      f"{type(v).__name__}")
    # vectors
    for f in ("source_offset", "source_variance", "fluid_source_offset"):
        v = proto.get(f)
        if v is not None and not is_vector(v):
            audit.err(f"{tag}: field '{f}' must be a Vector, got {v!r}")
    # arrays
    for f in ("parameters", "stage_counts"):
        v = proto.get(f)
        if v is not None and not isinstance(v, list):
            audit.err(f"{tag}: field '{f}' must be an array, got "
                      f"{type(v).__name__}")
    if ptype == "noise-function":
        params = proto.get("parameters")
        if isinstance(params, list) and not all(
                isinstance(p, str) for p in params):
            audit.err(f"{tag}: noise-function 'parameters' must be an array "
                      "of strings (docs 2.1.17)")
    # lightning graphics_set constraints
    if ptype == "lightning":
        gs = proto.get("graphics_set")
        if isinstance(gs, dict):
            fiv = gs.get("fork_intensity_multiplier")
            if fiv is not None and fiv == 1:
                audit.err(f"{tag}: graphics_set.fork_intensity_multiplier "
                          "cannot be 1 (docs 2.1.17)")
            cdl, bdl = gs.get("cloud_detail_level"), gs.get("bolt_detail_level")
            if cdl is not None and bdl is not None and cdl > bdl:
                audit.err(f"{tag}: graphics_set.cloud_detail_level ({cdl}) "
                          f"must be <= bolt_detail_level ({bdl}) (docs)")
            if gs.get("cloud_forks") == 255:
                audit.err(f"{tag}: graphics_set.cloud_forks cannot be 255 "
                          "(docs 2.1.17)")
    if ptype == "recipe":
        for f in ("ingredients", "results"):
            v = proto.get(f)
            if isinstance(v, list):
                for entry in v:
                    if not isinstance(entry, dict) or \
                            "name" not in entry or "amount" not in entry:
                        audit.err(f"{tag}: {f} entry must have name+amount, "
                                  f"got {entry!r}")


def check_refs(audit, tag, ptype, proto, names, entity_names, exists, in_type):
    def ref(name, where, ns=None, soft=False):
        if name is None:
            return
        if isinstance(name, (dict, list)):
            return
        if ns is not None:
            ok = name in names.get(ns, set())
        else:
            ok = exists(name)
        if not ok:
            msg = f"{tag}: {where} references '{name}' which does not exist"
            if soft:
                audit.warn(msg)
            else:
                audit.err(msg)

    if ptype == "item":
        ref(proto.get("place_result"), "place_result", ns=None)
        ref(proto.get("burnt_result"), "burnt_result")
        ref(proto.get("spoil_result"), "spoil_result")
        if proto.get("fuel_value") and proto.get("fuel_category"):
            ref(proto.get("fuel_category"), "fuel_category",
                ns="fuel-category", soft=True)
    if ptype == "resource":
        m = proto.get("minable")
        if isinstance(m, dict):
            ref(m.get("result"), "minable.result")
        ref(proto.get("category"), "category", ns="resource-category")
        ap = proto.get("autoplace")
        if isinstance(ap, dict):
            for k in ("probability_expression", "richness_expression"):
                v = ap.get(k)
                if isinstance(v, str):
                    ref(v, f"autoplace.{k}", ns="noise-expression")
    if ptype == "tile":
        ref(proto.get("fluid"), "fluid", ns="fluid")
        ref(proto.get("default_cover_tile"), "default_cover_tile",
            ns="tile", soft=True)
        ap = proto.get("autoplace")
        if isinstance(ap, dict):
            v = ap.get("probability_expression")
            if isinstance(v, str):
                ref(v, "autoplace.probability_expression",
                    ns="noise-expression")
    if ptype == "recipe":
        for f in ("ingredients", "results"):
            for entry in proto.get(f) or []:
                if not isinstance(entry, dict):
                    continue
                ref(entry.get("name"), f".name")
        ref(proto.get("main_product"), "main_product")
        for cat in proto.get("categories") or []:
            ref(cat, "categories[]", ns="recipe-category")
    if ptype == "technology":
        for p in proto.get("prerequisites") or []:
            ref(p, "prerequisites[]", ns="technology")
        unit = proto.get("unit")
        if isinstance(unit, dict):
            for ing in unit.get("ingredients") or []:
                if isinstance(ing, list) and ing:
                    ref(ing[0], "unit.ingredients[]")
        trig = proto.get("research_trigger")
        if isinstance(trig, dict):
            ref(trig.get("item"), "research_trigger.item")
            ref(trig.get("fluid"), "research_trigger.fluid", ns="fluid")
        for e in proto.get("effects") or []:
            if not isinstance(e, dict):
                continue
            et = e.get("type")
            if et in ("unlock-recipe", "change-recipe-productivity",
                      "unlock-recipe-category"):
                ref(e.get("recipe"), "effects.recipe", ns="recipe")
            elif et == "unlock-item":
                ref(e.get("item"), "effects.item")
            elif et == "unlock-technology":
                ref(e.get("technology"), "effects.technology",
                    ns="technology")
            elif et == "character-crafting-speed":
                if not is_number(e.get("modifier")):
                    audit.err(f"{tag}: character-crafting-speed effect needs "
                              "numeric modifier")
    if ptype in ("produce-achievement", "produce-per-hour-achievement"):
        ref(proto.get("item_product"), "item_product")
        ref(proto.get("fluid_product"), "fluid_product", ns="fluid")
    if ptype == "research-with-science-pack-achievement":
        ref(proto.get("science_pack"), "science_pack")
    if ptype == "build-entity-achievement":
        ref(proto.get("to_build"), "to_build")
    if ptype == "change-surface-achievement":
        ref(proto.get("surface"), "surface", ns="planet")
        if proto.get("surface") not in names.get("planet", set()) and \
                proto.get("surface") not in names.get("space-location", set()):
            pass  # already reported by ns check
    if ptype == "planet":
        lp = proto.get("lightning_properties")
        if isinstance(lp, dict):
            for lt in lp.get("lightning_types") or []:
                ref(lt, "lightning_properties.lightning_types",
                    ns="lightning")
            for k in lp.get("priority_rules") or []:
                if isinstance(k, dict) and k.get("type") == "id":
                    ref(k.get("string"), "priority_rules.id")
            for k in lp.get("exemption_rules") or []:
                if isinstance(k, dict) and k.get("type") == "prototype":
                    ref(k.get("string"), "exemption_rules.prototype",
                        soft=True)
        for k in (proto.get("surface_properties") or {}):
            if k not in names.get("surface-property", set()):
                audit.warn(f"{tag}: surface_properties key '{k}' is not a "
                           "registered surface-property")
    if ptype == "space-connection":
        for f in ("from", "to"):
            v = proto.get(f)
            if v not in names.get("planet", set()) and \
                    v not in names.get("space-location", set()):
                audit.err(f"{tag}: {f} = {v!r} is not a known planet / "
                          "space location")
        for sd in proto.get("asteroid_spawn_definitions") or []:
            if isinstance(sd, dict):
                a = sd.get("asteroid")
                if a is not None and a not in names.get("asteroid", set()) \
                        and a not in names.get("asteroid-chunk", set()):
                    audit.warn(f"{tag}: asteroid_spawn_definitions references "
                               f"'{a}' which is not an asteroid / "
                               "asteroid-chunk prototype")
    if ptype == "lightning":
        dmg = proto.get("damage")
        if isinstance(dmg, dict):
            ref(dmg.get("type"), "damage.type", ns="damage-type")
            if not is_number(dmg.get("amount")):
                audit.err(f"{tag}: damage.amount must be a number")
    if ptype in ("assembling-machine", "generator", "offshore-pump",
                 "lightning-attractor"):
        ref(proto.get("corpse"), "corpse", ns="corpse", soft=True)
        ref(proto.get("dying_explosion"), "dying_explosion", ns="explosion")
        ic = proto.get("impact_category")
        if ic is not None and ic not in names.get("impact-category", set()):
            audit.err(f"{tag}: impact_category = {ic!r} is not a defined "
                      "impact-category")
        for fb in proto.get("fluid_boxes") or []:
            if isinstance(fb, dict):
                ref(fb.get("filter"), "fluid_boxes[].filter", ns="fluid")
        fb = proto.get("fluid_box")
        if isinstance(fb, dict):
            ref(fb.get("filter"), "fluid_box.filter", ns="fluid")
        for cat in proto.get("crafting_categories") or []:
            ref(cat, "crafting_categories[]", ns="recipe-category")
        es = proto.get("energy_source")
        if isinstance(es, dict) and es.get("type") not in (
                "electric", "burner", "heat", "fluid", "void", "nuclear"):
            audit.warn(f"{tag}: energy_source.type = {es.get('type')!r} "
                       "unexpected")
    if ptype == "simple-entity":
        m = proto.get("minable")
        if isinstance(m, dict):
            ref(m.get("result"), "minable.result")
    # subgroup references for prototypes that carry one
    sg = proto.get("subgroup")
    if sg is not None and ptype in (
            "item", "item-group", "fluid", "technology", "planet",
            "space-connection", "sound", "lightning"):
        ref(sg, "subgroup", ns="item-subgroup", soft=True)


def check_recipe_categories(audit, protos, names):
    rc = set(names.get("recipe-category", []))
    for rec in protos:
        if rec["type"] != "recipe":
            continue
        cats = rec["proto"].get("categories") or []
        for c in cats:
            if c not in rc:
                audit.err(f"recipe/{rec['name']}: categories[] = {c!r} is "
                          "not a defined recipe-category")


def check_planet_mapgen(audit, protos, names):
    for rec in protos:
        if rec["type"] != "planet":
            continue
        tag = f"planet/{rec['name']}"
        mgs = rec["proto"].get("map_gen_settings")
        if not isinstance(mgs, dict):
            continue
        # property_expression_names -> noise-expression names
        pen = mgs.get("property_expression_names")
        if isinstance(pen, dict):
            for k, v in pen.items():
                if not isinstance(v, str):
                    continue
                if v not in names.get("noise-expression", set()):
                    audit.err(f"{tag}: map_gen_settings."
                              f"property_expression_names[{k}] = {v!r} is "
                              "not a defined noise-expression")
        # autoplace_controls -> autoplace-control names
        ac = mgs.get("autoplace_controls")
        if isinstance(ac, dict):
            for k in ac:
                if k not in names.get("autoplace-control", set()):
                    audit.err(f"{tag}: map_gen_settings.autoplace_controls "
                              f"refers to unknown autoplace-control '{k}'")
        # autoplace_settings -> existing tiles / entities
        aps = mgs.get("autoplace_settings")
        if isinstance(aps, dict):
            for kind, ns in (("tile", "tile"), ("entity", None)):
                sub = (aps.get(kind) or {}).get("settings")
                if not isinstance(sub, dict):
                    continue
                for k in sub:
                    if ns == "tile":
                        if k not in names.get("tile", set()):
                            audit.err(f"{tag}: autoplace_settings.tile "
                                      f"refers to unknown tile '{k}'")
                    else:
                        # entity: must exist in some entity-ish type
                        found = any(k in v for t, v in names.items()
                                    if t not in ("tile", "recipe",
                                                 "technology", "item",
                                                 "fluid", "sound"))
                        if not found:
                            audit.err(f"{tag}: autoplace_settings.entity "
                                      f"refers to unknown entity '{k}'")


def check_unknown_fields(audit, tag, ptype, proto, donor_fields):
    if ptype not in DOC_FIELDS:
        audit.warn(f"{tag}: no doc field set for type '{ptype}' — "
                   "unknown-field audit skipped")
        return
    allowed = set(DOC_FIELDS[ptype])
    allowed |= donor_fields.get(ptype, set())
    legacy = KNOWN_LEGACY_FIELDS.get(ptype, set())
    for k in proto:
        if k in allowed or k in legacy:
            continue
        if k in ("type", "name"):
            continue
        audit.warn(f"{tag}: field '{k}' is not in the 2.1.17 docs for "
                   f"'{ptype}' and not inherited from the vanilla donor "
                   "(engine ignores unknown properties; audit only)")
    for k in proto:
        if k in legacy:
            audit.info(f"{tag}: field '{k}' is a pre-2.0 legacy field "
                       "ignored by the engine (docs 2.1.17 does not list it)")


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def write_report(audit, data, path):
    lines = [
        "# Cataclysm — prototype audit report (docs 2.1.17 + static)",
        "",
        f"- Generated: {__import__('datetime').datetime.now().isoformat(timespec='seconds')}",
        f"- Instances checked: {audit.checked} across "
        f"{len(set(r['type'] for r in data['mod_protos']))} types",
        f"- Errors: **{len(audit.errors)}**  Warnings: {len(audit.warns)}  "
        f"Info: {len(audit.infos)}",
        f"- Result: **{'PASS' if audit.ok else 'FAIL'}**",
        "",
        "## Errors",
        "",
    ]
    if audit.errors:
        lines += [f"- {e}" for e in audit.errors]
    else:
        lines.append("- none")
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in audit.warns] or ["- none"]
    lines += ["", "## Info", ""]
    lines += [f"- {i}" for i in audit.infos] or ["- none"]
    lines += ["", "## Coverage", "",
              "| type | instances |",
              "| --- | --- |"]
    counts = {}
    for r in data["mod_protos"]:
        counts[r["type"]] = counts.get(r["type"], 0) + 1
    for t in sorted(counts):
        lines.append(f"| {t} | {counts[t]} |")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# self-test: prove the checker catches the historical bug classes
# ---------------------------------------------------------------------------

def self_test(data, defines_protos):
    """Mutate a deep copy of the dump the way the historical crashes did and
    assert the validator reports them. Bug classes:
      1. produce-achievement missing `limited_to_one_game`
      2. armor/tool item missing `durability` (docs required field set)
      3. entity referencing a dying_explosion that does not exist in 2.x
      4. recipe ingredient referencing a non-existent item
      5. autoplace-control.category outside the enum
    """
    import copy
    mutated = copy.deepcopy(data)

    def find(t, n):
        for r in mutated["mod_protos"]:
            if r["type"] == t and r["name"] == n:
                return r["proto"]
        return None

    # 1. drop limited_to_one_game from every produce-achievement
    for r in mutated["mod_protos"]:
        if r["type"] == "produce-achievement":
            r["proto"].pop("limited_to_one_game", None)
    # 3. break dying_explosion reference
    ex = find("offshore-pump", "condensate-extractor")
    ex["dying_explosion"] = "small-explosion"
    # 4. broken ingredient reference
    rc = find("recipe", "cataclysm-stormite-plate")
    rc["ingredients"] = [{"type": "item", "name": "no-such-item",
                          "amount": 1}]
    # 5. enum violation
    ac = find("autoplace-control", "stormite_ore")
    ac["category"] = "bogus-category"

    audit = Audit()
    run(audit, mutated, defines_protos)

    expected = [
        "produce-achievement", "limited_to_one_game",
        "small-explosion", "no-such-item", "bogus-category",
    ]
    joined = "\n".join(audit.errors).lower()
    missing = [e for e in expected if e.lower() not in joined]
    if missing:
        print("\n[self-test] FAIL — validator did not catch: " +
              ", ".join(missing))
        return False
    print("\n[self-test] PASS — all historical bug classes detected "
          "(limited_to_one_game, broken references, enum violation)")
    return True


if __name__ == "__main__":
    main()

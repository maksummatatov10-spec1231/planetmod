-- Cataclysm — resource entities (stormite ore, astrite ore).
-- Autoplace is driven by noise expressions defined in map-gen.lua
-- (probability/richness per resource), mirroring the Aquilo pattern.

local base_tile_sounds = require("__base__.prototypes.tile.tile-sounds")

local function resource(name, order, mining_time, map_color, tint, subgroup)
  return {
    type = "resource",
    name = name,
    icon = "__cataclysm__/graphics/icons/" .. name .. ".png",
    icon_size = 128,
    flags = { "placeable-neutral" },
    order = "a-b-" .. order,
    tree_removal_probability = 0.8,
    tree_removal_max_distance = 32 * 32,
    minable = {
      mining_time = mining_time,
      result = name
    },
    category = "basic-solid",
    subgroup = subgroup,
    walking_sound = base_tile_sounds.walking.ore,
    collision_box = { { -0.1, -0.1 }, { 0.1, 0.1 } },
    selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } },
    autoplace = {
      order = order,
      probability_expression = "cataclysm_" .. order .. "_probability",
      richness_expression = "cataclysm_" .. order .. "_richness"
    },
    stage_counts = { 15000, 9500, 5500, 2900, 1300, 400, 150, 80 },
    stages = {
      sheet = {
        filename = "__cataclysm__/graphics/entity/" .. name .. "/" .. name .. ".png",
        priority = "extra-high",
        size = 128,
        frame_count = 8,
        variation_count = 8,
        scale = 0.5
      }
    },
    map_color = map_color,
    mining_visualisation_tint = tint
  }
end

data:extend({
  resource(
    "stormite-ore",
    "stormite_ore",
    3,
    { r = 0.55, g = 0.42, b = 0.85, a = 1 },
    { r = 0.65, g = 0.5, b = 1.0, a = 1 },
    "cataclysm-resources"
  ),
  resource(
    "astrite-ore",
    "astrite_ore",
    5,
    { r = 0.75, g = 0.82, b = 0.9, a = 1 },
    { r = 0.9, g = 0.95, b = 1.0, a = 1 },
    "cataclysm-resources"
  )
})

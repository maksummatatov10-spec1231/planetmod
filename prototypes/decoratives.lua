-- Cataclysm — decorative entities (flora & geology).
-- All are simple-entity with generated HD art (256x256 frames, rendered at
-- scale 0.5 -> 128 on-screen px = 2 tiles, bottom-anchored to the tile grid);
-- placement uses the autoplace expressions defined in map-gen.lua.
-- The vent and the crystal tree are animated (animation grid 512x512 = 2x2
-- frames of 256x256, line_length=2).

local util = require("util")

local function simple_entity(name, collision, max_health, autoplace_expression, anim)
  local e = {
    type = "simple-entity",
    name = name,
    icon = "__cataclysm__/graphics/icons/cataclysm.png",
    icon_size = 128,
    flags = { "placeable-neutral", "placeable-player" },
    minable = { mining_time = 0.5 },
    max_health = max_health,
    collision_box = collision,
    collision_mask = { layers = { object = true } },
    selection_box = collision,
    render_layer = "decorative",
    autoplace = autoplace_expression
      and { probability_expression = autoplace_expression }
      or nil
  }
  local sprite = {
    filename = "__cataclysm__/graphics/entity/" .. name .. "/" .. name .. ".png",
    priority = "medium",
    width = 256,
    height = 256,
    scale = 0.5,
    shift = util.by_pixel(0, 0)
  }
  if anim then
    e.animations = { {
      filename = sprite.filename,
      priority = "medium",
      width = 256,
      height = 256,
      frame_count = anim.frame_count,
      line_length = 2,
      animation_speed = anim.animation_speed,
      scale = 0.5,
      shift = util.by_pixel(0, 0)
    } }
    e.random_animation_offset = true
  else
    e.picture = sprite
  end
  return e
end

data:extend({
  simple_entity("cataclysm-crystal-tree", { { -0.4, -0.4 }, { 0.4, 0.4 } }, 60, "cataclysm_trees",
    { frame_count = 3, animation_speed = 0.04 }),
  simple_entity("cataclysm-rock", { { -0.5, -0.5 }, { 0.5, 0.5 } }, 150, "cataclysm_rocks"),
  simple_entity("cataclysm-vent", { { -0.5, -0.5 }, { 0.5, 0.5 } }, 200, "cataclysm_vents",
    { frame_count = 4, animation_speed = 0.06 })
})

-- Ancient spire: rare ruin, scripted achievement target ("what-was-here").
local spire = simple_entity("cataclysm-ancient-spire", { { -0.8, -0.8 }, { 0.8, 0.8 } }, 1000)
spire.autoplace = { probability_expression = "cataclysm_spires" }
spire.collision_mask = { layers = { object = true } }
spire.flags = { "placeable-neutral", "placeable-player", "not-deconstructable" }
spire.order = "z-cataclysm-spire"
data:extend({ spire })

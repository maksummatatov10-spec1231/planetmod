-- Cataclysm — decorative entities (flora & geology).
-- All are simple-entity placeholders with generated art; placement uses the
-- autoplace expressions defined in map-gen.lua.

local util = require("util")

local function simple_entity(name, picture, collision, max_health, autoplace_expression)
  return {
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
    picture = {
      filename = "__cataclysm__/graphics/entity/" .. name .. "/" .. name .. ".png",
      priority = "medium",
      width = 128,
      height = 128,
      shift = util.by_pixel(0, 0)
    },
    autoplace = autoplace_expression
      and { probability_expression = autoplace_expression }
      or nil
  }
end

data:extend({
  simple_entity("cataclysm-crystal-tree", "tree", { { -0.4, -0.4 }, { 0.4, 0.4 } }, 60, "cataclysm_trees"),
  simple_entity("cataclysm-rock", "rock", { { -0.5, -0.5 }, { 0.5, 0.5 } }, 150, "cataclysm_rocks"),
  simple_entity("cataclysm-vent", "vent", { { -0.5, -0.5 }, { 0.5, 0.5 } }, 200, "cataclysm_vents")
})

-- Ancient spire: rare ruin, scripted achievement target ("what-was-here").
local spire = simple_entity("cataclysm-ancient-spire", "spire", { { -0.8, -0.8 }, { 0.8, 0.8 } }, 1000)
spire.autoplace = { probability_expression = "cataclysm_spires" }
spire.collision_mask = { layers = { object = true } }
spire.flags = { "placeable-neutral", "placeable-player", "not-deconstructable" }
spire.order = "z-cataclysm-spire"
data:extend({ spire })

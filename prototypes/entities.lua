-- Cataclysm — machines.
--
-- V1 strategy: every machine is a renamed deep-copy of a battle-tested vanilla
-- prototype (graphics, sounds, circuit definitions are inherited). This keeps
-- the mod stable and save-safe; custom art is planned as polish later.
--
-- `surface_conditions` is cleared on every copy: vanilla planet-specific
-- buildings (lightning collector etc.) carry build restrictions tied to their
-- home planet's surface properties, which must not leak onto Cataclysm.

local function clear_surface_conditions(e)
  e.surface_conditions = nil
  return e
end

data:extend({
  -- Condensate extractor: pumps storm condensate from cataclysm lake tiles.
  -- Modeled on the vanilla offshore-pump. In 2.x the offshore pump derives
  -- its output fluid from the tile it stands on (cataclysm-lake / -deep have
  -- fluid = "cataclysm-storm-condensate"); the fluid_box filter additionally
  -- enforces the fluid (OffshorePumpPrototype has no top-level `fluid`
  -- field — verified against lua-api 2.1.17, docs/API-AUDIT.md).
  clear_surface_conditions((function()
    local e = table.deepcopy(data.raw["offshore-pump"]["offshore-pump"])
    e.name = "condensate-extractor"
    e.icon = "__cataclysm__/graphics/icons/condensate-extractor.png"
    e.minable = { mining_time = 0.1, result = "condensate-extractor" }
    e.fast_replaceable_group = "condensate-extractor"
    e.fluid_box = table.deepcopy(e.fluid_box)
    e.fluid_box.filter = "cataclysm-storm-condensate"
    e.dying_explosion = "small-explosion-hit"
    return e
  end)()),

  -- Storm siphon: attracts lightning (priority in planet lightning_properties)
  -- and converts strikes into electrical energy stored in its buffer.
  -- Modeled on the vanilla lightning-collector.
  clear_surface_conditions((function()
    local e = table.deepcopy(data.raw["lightning-attractor"]["lightning-collector"])
    e.name = "storm-siphon"
    e.icon = "__cataclysm__/graphics/icons/storm-siphon.png"
    e.minable = { mining_time = 0.3, result = "storm-siphon" }
    e.fast_replaceable_group = "storm-siphon"
    if e.energy_source then
      e.energy_source = table.deepcopy(e.energy_source)
      -- Buffer matches the 2GJ strike energy (vanilla collector: 1GJ buffer
      -- vs 1GJ strikes), so a single strike fully charges the siphon.
      e.energy_source.buffer_capacity = "2GJ"
    end
    return e
  end)()),

  -- Storm foundry: smelts stormite and charges condensate.
  -- Modeled on the space-age foundry (fluid-capable smelting machine).
  clear_surface_conditions((function()
    local e = table.deepcopy(data.raw["assembling-machine"]["foundry"])
    e.name = "storm-foundry"
    e.icon = "__cataclysm__/graphics/icons/storm-foundry.png"
    e.minable = { mining_time = 0.2, result = "storm-foundry" }
    e.fast_replaceable_group = "storm-foundry"
    e.crafting_categories = { "cataclysm-smelting", "cataclysm-charging" }
    e.crafting_speed = 2
    e.energy_usage = "2MW"
    return e
  end)()),

  -- Storm fabricator: assembles lattices, science packs and machines.
  -- Modeled on the electromagnetic-plant (module slots, productivity bonus).
  clear_surface_conditions((function()
    local e = table.deepcopy(data.raw["assembling-machine"]["electromagnetic-plant"])
    e.name = "storm-fabricator"
    e.icon = "__cataclysm__/graphics/icons/storm-fabricator.png"
    e.minable = { mining_time = 0.2, result = "storm-fabricator" }
    e.fast_replaceable_group = "storm-fabricator"
    e.crafting_categories = { "cataclysm-crafting" }
    return e
  end)()),

  -- Storm generator: burns charged condensate into electricity.
  -- Modeled on the steam turbine.
  clear_surface_conditions((function()
    local e = table.deepcopy(data.raw["generator"]["steam-turbine"])
    e.name = "storm-generator"
    e.icon = "__cataclysm__/graphics/icons/storm-generator.png"
    e.minable = { mining_time = 0.2, result = "storm-generator" }
    e.fast_replaceable_group = "storm-generator"
    e.maximum_temperature = 1000
    e.fluid_usage_per_tick = 1
    e.fluid_box = table.deepcopy(e.fluid_box)
    e.fluid_box.filter = "cataclysm-charged-condensate"
    return e
  end)())
})

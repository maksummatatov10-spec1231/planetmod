-- Cataclysm — technologies.
--
-- Progression:
--   1. cataclysm-planet-discovery opens the route to the planet; it is paid
--      in the new cataclysm-survey-pack (crafted before the flight, on
--      Aquilo / the space platform — NOT cryogenic science).
--   2. On the planet the first production steps are learned by doing:
--      mining and crafting trigger the research (stormite processing,
--      storm siphons, astrite refining, voltaic lattice).
--   3. Deeper technologies are paid in the cataclysmic science pack
--      produced on the planet itself.

local function tech(name, icon, order, prerequisites, unit, effects)
  return {
    type = "technology",
    name = name,
    icon = "__cataclysm__/graphics/technology/" .. icon .. ".png",
    icon_size = 128,
    order = order,
    prerequisites = prerequisites,
    unit = unit,
    effects = effects
  }
end

local function trigger_tech(name, icon, order, prerequisites, trigger, effects)
  return {
    type = "technology",
    name = name,
    icon = "__cataclysm__/graphics/technology/" .. icon .. ".png",
    icon_size = 128,
    order = order,
    prerequisites = prerequisites,
    research_trigger = trigger,
    effects = effects
  }
end

local function pack_unit(count, time, packs)
  local ingredients = {}
  for _, p in ipairs(packs) do
    table.insert(ingredients, { p, 1 })
  end
  return { count = count, ingredients = ingredients, time = time }
end

-- research triggers for the "learn by doing" tier
local function mine_entity(entity)
  return { type = "mine-entity", entities = { entity } }
end

local function craft_item(item)
  return { type = "craft-item", item = item, amount = 1 }
end

-- recipes unlocked by more than one tech are referenced here for brevity
local unlock = function(recipe)
  return { type = "unlock-recipe", recipe = recipe }
end

data:extend({
  -- Tier 0: discovery of the planet ------------------------------------------
  {
    type = "technology",
    name = "cataclysm-planet-discovery",
    icon = "__cataclysm__/graphics/icons/cataclysm.png",
    icon_size = 128,
    order = "f[cataclysm]-a",
    essential = true,
    prerequisites = { "space-platform-thruster" },
    unit = pack_unit(150, 30, { "cataclysm-survey-pack", "space-science-pack" }),
    effects = {
      {
        type = "unlock-space-location",
        space_location = "cataclysm",
        use_icon_overlay_constant = true
      },
      {
        type = "unlock-travel-to-space-platforms",
        modifier = true
      }
    }
  },
  -- Tier 1: arrival -----------------------------------------------------------
  tech(
    "cataclysm-condensate-extraction",
    "condensate-extraction",
    "f[cataclysm]-b",
    { "cataclysm-planet-discovery" },
    pack_unit(100, 30, { "cataclysm-survey-pack", "space-science-pack" }),
    { unlock("condensate-extractor") }
  ),
  -- Tier 2: learn by doing (mining / crafting triggers) ------------------------
  trigger_tech(
    "cataclysm-stormite-processing",
    "stormite-processing",
    "f[cataclysm]-c",
    { "cataclysm-condensate-extraction" },
    mine_entity("stormite-ore"),
    { unlock("cataclysm-stormite-plate"), unlock("storm-foundry") }
  ),
  trigger_tech(
    "cataclysm-storm-siphon",
    "storm-siphon",
    "f[cataclysm]-d",
    { "cataclysm-stormite-processing" },
    craft_item("storm-foundry"),
    {
      unlock("storm-siphon"),
      unlock("cataclysm-charge-condensate"),
      unlock("cataclysm-discharge-condensate")
    }
  ),
  trigger_tech(
    "cataclysm-astrite-refining",
    "astrite-refining",
    "f[cataclysm]-e",
    { "cataclysm-stormite-processing" },
    craft_item("stormite-plate"),
    { unlock("cataclysm-astrite-crystal") }
  ),
  trigger_tech(
    "cataclysm-voltaic-lattice",
    "voltaic-lattice",
    "f[cataclysm]-f",
    { "cataclysm-astrite-refining", "cataclysm-storm-siphon" },
    craft_item("astrite-crystal"),
    { unlock("cataclysm-voltaic-lattice"), unlock("storm-fabricator") }
  ),
  -- Science pack ----------------------------------------------------------------
  trigger_tech(
    "cataclysmic-science-pack",
    "cataclysmic-science-pack",
    "f[cataclysm]-g",
    { "cataclysm-voltaic-lattice" },
    craft_item("cataclysm-voltaic-lattice"),
    { unlock("cataclysmic-science-pack") }
  ),
  -- Tier 3: energy & defence -----------------------------------------------------
  tech(
    "cataclysm-storm-generator",
    "storm-generator",
    "f[cataclysm]-h",
    { "cataclysm-voltaic-lattice", "cataclysm-storm-siphon", "cataclysmic-science-pack" },
    pack_unit(300, 45, { "cataclysmic-science-pack", "space-science-pack" }),
    { unlock("storm-generator") }
  ),
  -- Real effect (halved superstorm strike chance) is scripted in control.lua;
  -- the crafting speed bonus gives the tech a visible prototype-level effect.
  tech(
    "cataclysm-lightning-protection",
    "lightning-protection",
    "f[cataclysm]-i",
    { "cataclysm-storm-siphon", "cataclysmic-science-pack" },
    pack_unit(250, 45, { "cataclysmic-science-pack", "space-science-pack" }),
    {
      {
        type = "character-crafting-speed",
        modifier = 0.1
      }
    }
  ),
  tech(
    "cataclysm-seismic-stabilization",
    "seismic-stabilization",
    "f[cataclysm]-j",
    { "cataclysm-lightning-protection" },
    pack_unit(400, 60, { "cataclysmic-science-pack", "space-science-pack" }),
    {}
  ),
  -- Tier 4: endgame ----------------------------------------------------------------
  tech(
    "cataclysm-storm-platform-shield",
    "storm-platform-shield",
    "f[cataclysm]-k",
    { "cataclysm-voltaic-lattice", "cataclysmic-science-pack" },
    pack_unit(500, 60, { "cataclysmic-science-pack", "space-science-pack", "promethium-science-pack" }),
    {}
  ),
  tech(
    "cataclysm-productivity",
    "cataclysm-productivity",
    "f[cataclysm]-l",
    { "cataclysm-voltaic-lattice", "cataclysmic-science-pack" },
    pack_unit(350, 45, { "cataclysmic-science-pack", "space-science-pack" }),
    {
      { type = "change-recipe-productivity", recipe = "cataclysm-stormite-plate", change = 0.1 },
      { type = "change-recipe-productivity", recipe = "cataclysm-voltaic-lattice", change = 0.1 },
      { type = "change-recipe-productivity", recipe = "cataclysmic-science-pack", change = 0.1 }
    }
  ),
  tech(
    "cataclysm-storm-logistics",
    "storm-logistics",
    "f[cataclysm]-m",
    { "cataclysm-storm-generator" },
    pack_unit(250, 30, { "cataclysmic-science-pack", "space-science-pack" }),
    {}
  )
})

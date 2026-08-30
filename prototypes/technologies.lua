-- Cataclysm — technologies.
--
-- The tree starts from cryogenic science (post-Aquilo gate) and then requires
-- the cataclysmic science pack produced on the planet itself.

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

local function pack_unit(count, time, packs)
  local ingredients = {}
  for _, p in ipairs(packs) do
    table.insert(ingredients, { p, 1 })
  end
  return { count = count, ingredients = ingredients, time = time }
end

-- recipes unlocked by more than one tech are referenced here for brevity
local unlock = function(recipe)
  return { type = "unlock-recipe", recipe = recipe }
end

data:extend({
  -- Tier 0: arrival ---------------------------------------------------------
  tech(
    "cataclysm-condensate-extraction",
    "condensate-extraction",
    "f[cataclysm]-a",
    { "cryogenic-science-pack", "space-platform" },
    pack_unit(100, 30, { "cryogenic-science-pack" }),
    { unlock("condensate-extractor") }
  ),
  -- Tier 1: basic production -------------------------------------------------
  tech(
    "cataclysm-stormite-processing",
    "stormite-processing",
    "f[cataclysm]-b",
    { "cataclysm-condensate-extraction" },
    pack_unit(150, 30, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    { unlock("cataclysm-stormite-plate"), unlock("storm-foundry") }
  ),
  tech(
    "cataclysm-storm-siphon",
    "storm-siphon",
    "f[cataclysm]-c",
    { "cataclysm-condensate-extraction" },
    pack_unit(150, 30, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    {
      unlock("storm-siphon"),
      unlock("cataclysm-charge-condensate"),
      unlock("cataclysm-discharge-condensate")
    }
  ),
  -- Tier 2: advanced materials ------------------------------------------------
  tech(
    "cataclysm-astrite-refining",
    "astrite-refining",
    "f[cataclysm]-d",
    { "cataclysm-stormite-processing" },
    pack_unit(200, 30, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    { unlock("cataclysm-astrite-crystal") }
  ),
  tech(
    "cataclysm-voltaic-lattice",
    "voltaic-lattice",
    "f[cataclysm]-e",
    { "cataclysm-storm-siphon", "cataclysm-astrite-refining" },
    pack_unit(250, 30, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    { unlock("cataclysm-voltaic-lattice"), unlock("storm-fabricator") }
  ),
  -- Science pack ---------------------------------------------------------------
  {
    type = "technology",
    name = "cataclysmic-science-pack",
    icon = "__cataclysm__/graphics/technology/cataclysmic-science-pack.png",
    icon_size = 128,
    order = "f[cataclysm]-f",
    prerequisites = { "cataclysm-voltaic-lattice" },
    research_trigger = {
      type = "craft-item",
      item = "cataclysm-voltaic-lattice",
      amount = 1
    },
    effects = { unlock("cataclysmic-science-pack") }
  },
  -- Tier 3: energy & defence ---------------------------------------------------
  tech(
    "cataclysm-storm-generator",
    "storm-generator",
    "f[cataclysm]-g",
    { "cataclysm-voltaic-lattice" },
    pack_unit(300, 45, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    { unlock("storm-generator") }
  ),
  -- Real effect (halved superstorm strike chance) is scripted in control.lua;
  -- the crafting speed bonus gives the tech a visible prototype-level effect.
  tech(
    "cataclysm-lightning-protection",
    "lightning-protection",
    "f[cataclysm]-h",
    { "cataclysm-storm-siphon" },
    pack_unit(250, 45, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
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
    "f[cataclysm]-i",
    { "cataclysm-lightning-protection" },
    pack_unit(400, 60, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    {}
  ),
  -- Tier 4: endgame --------------------------------------------------------------
  tech(
    "cataclysm-storm-platform-shield",
    "storm-platform-shield",
    "f[cataclysm]-j",
    { "cataclysm-voltaic-lattice" },
    pack_unit(500, 60, { "cryogenic-science-pack", "cataclysmic-science-pack", "promethium-science-pack" }),
    {}
  ),
  tech(
    "cataclysm-productivity",
    "cataclysm-productivity",
    "f[cataclysm]-k",
    { "cataclysm-voltaic-lattice" },
    pack_unit(350, 45, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    {
      { type = "change-recipe-productivity", recipe = "cataclysm-stormite-plate", change = 0.1 },
      { type = "change-recipe-productivity", recipe = "cataclysm-voltaic-lattice", change = 0.1 },
      { type = "change-recipe-productivity", recipe = "cataclysmic-science-pack", change = 0.1 }
    }
  ),
  tech(
    "cataclysm-storm-logistics",
    "storm-logistics",
    "f[cataclysm]-l",
    { "cataclysm-storm-generator" },
    pack_unit(250, 30, { "cryogenic-science-pack", "cataclysmic-science-pack" }),
    {}
  )
})

-- Cataclysm — recipes. All recipes are locked behind technologies
-- (enabled = false) and use the mod's recipe categories.

data:extend({
  -- Smelting ---------------------------------------------------------------
  {
    type = "recipe",
    name = "cataclysm-stormite-plate",
    category = "cataclysm-smelting",
    enabled = false,
    energy_required = 4,
    ingredients = {
      { type = "item", name = "stormite-ore", amount = 2 },
      { type = "fluid", name = "cataclysm-storm-condensate", amount = 20 }
    },
    results = {
      { type = "item", name = "stormite-plate", amount = 1 }
    },
    allow_productivity = true
  },
  {
    type = "recipe",
    name = "cataclysm-astrite-crystal",
    category = "cataclysm-smelting",
    enabled = false,
    energy_required = 6,
    ingredients = {
      { type = "item", name = "astrite-ore", amount = 2 },
      { type = "fluid", name = "cataclysm-charged-condensate", amount = 10 }
    },
    results = {
      { type = "item", name = "astrite-crystal", amount = 1 }
    },
    allow_productivity = true
  },

  -- Charging ---------------------------------------------------------------
  {
    type = "recipe",
    name = "cataclysm-charge-condensate",
    category = "cataclysm-charging",
    enabled = false,
    energy_required = 2,
    ingredients = {
      { type = "fluid", name = "cataclysm-storm-condensate", amount = 50 }
    },
    results = {
      { type = "fluid", name = "cataclysm-charged-condensate", amount = 25, temperature = 200 }
    },
    allow_productivity = false
  },
  {
    type = "recipe",
    name = "cataclysm-discharge-condensate",
    category = "cataclysm-charging",
    enabled = false,
    energy_required = 0.5,
    ingredients = {
      { type = "fluid", name = "cataclysm-charged-condensate", amount = 10 }
    },
    results = {
      { type = "fluid", name = "cataclysm-storm-condensate", amount = 10 }
    },
    allow_productivity = false
  },

  -- Crafting ---------------------------------------------------------------
  {
    type = "recipe",
    name = "cataclysm-voltaic-lattice",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 10,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 4 },
      { type = "item", name = "astrite-crystal", amount = 1 },
      { type = "fluid", name = "cataclysm-charged-condensate", amount = 25 }
    },
    results = {
      { type = "item", name = "cataclysm-voltaic-lattice", amount = 1 }
    },
    allow_productivity = true
  },
  {
    type = "recipe",
    name = "cataclysmic-science-pack",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 30,
    ingredients = {
      { type = "item", name = "cataclysm-voltaic-lattice", amount = 1 },
      { type = "item", name = "astrite-crystal", amount = 1 },
      { type = "fluid", name = "cataclysm-charged-condensate", amount = 50 }
    },
    results = {
      { type = "item", name = "cataclysmic-science-pack", amount = 1 }
    },
    allow_productivity = true
  },

  -- Machines ---------------------------------------------------------------
  {
    type = "recipe",
    name = "condensate-extractor",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 2,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 20 },
      { type = "item", name = "pipe", amount = 4 }
    },
    results = { { type = "item", name = "condensate-extractor", amount = 1 } }
  },
  {
    type = "recipe",
    name = "storm-siphon",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 5,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 40 },
      { type = "item", name = "cataclysm-voltaic-lattice", amount = 2 },
      { type = "item", name = "copper-cable", amount = 20 }
    },
    results = { { type = "item", name = "storm-siphon", amount = 1 } }
  },
  {
    type = "recipe",
    name = "storm-foundry",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 5,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 80 },
      { type = "item", name = "pipe", amount = 10 },
      { type = "item", name = "stone-brick", amount = 30 }
    },
    results = { { type = "item", name = "storm-foundry", amount = 1 } }
  },
  {
    type = "recipe",
    name = "storm-fabricator",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 8,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 120 },
      { type = "item", name = "cataclysm-voltaic-lattice", amount = 2 },
      { type = "item", name = "astrite-crystal", amount = 2 }
    },
    results = { { type = "item", name = "storm-fabricator", amount = 1 } }
  },
  {
    type = "recipe",
    name = "storm-generator",
    category = "cataclysm-crafting",
    enabled = false,
    energy_required = 10,
    ingredients = {
      { type = "item", name = "stormite-plate", amount = 200 },
      { type = "item", name = "cataclysm-voltaic-lattice", amount = 4 },
      { type = "item", name = "astrite-crystal", amount = 4 },
      { type = "item", name = "steel-plate", amount = 20 }
    },
    results = { { type = "item", name = "storm-generator", amount = 1 } }
  }
})

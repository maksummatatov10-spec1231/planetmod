-- Cataclysm — items.

local science = data.raw.item["automation-science-pack"]

data:extend({
  -- Raw resources ----------------------------------------------------------
  {
    type = "item",
    name = "stormite-ore",
    icon = "__cataclysm__/graphics/icons/stormite-ore.png",
    icon_size = 64,
    subgroup = "cataclysm-resources",
    order = "a-a[stormite-ore]",
    stack_size = 50,
    weight = 200
  },
  {
    type = "item",
    name = "astrite-ore",
    icon = "__cataclysm__/graphics/icons/astrite-ore.png",
    icon_size = 64,
    subgroup = "cataclysm-resources",
    order = "a-b[astrite-ore]",
    stack_size = 50,
    weight = 200
  },

  -- Intermediate products ---------------------------------------------------
  {
    type = "item",
    name = "stormite-plate",
    icon = "__cataclysm__/graphics/icons/stormite-plate.png",
    icon_size = 64,
    subgroup = "cataclysm-intermediate",
    order = "b-a[stormite-plate]",
    stack_size = 100,
    weight = 100
  },
  {
    type = "item",
    name = "astrite-crystal",
    icon = "__cataclysm__/graphics/icons/astrite-crystal.png",
    icon_size = 64,
    subgroup = "cataclysm-intermediate",
    order = "b-b[astrite-crystal]",
    stack_size = 100,
    weight = 80
  },
  {
    type = "item",
    name = "cataclysm-voltaic-lattice",
    icon = "__cataclysm__/graphics/icons/voltaic-lattice.png",
    icon_size = 64,
    subgroup = "cataclysm-intermediate",
    order = "b-c[voltaic-lattice]",
    stack_size = 50,
    weight = 250
  },

  -- Science pack ------------------------------------------------------------
  {
    type = "tool",
    name = "cataclysmic-science-pack",
    icon = "__cataclysm__/graphics/icons/cataclysmic-science-pack.png",
    icon_size = 64,
    subgroup = "science-pack",
    order = "k-a[cataclysmic-science-pack]",
    stack_size = science.stack_size,
    durability = science.durability,
    durability_description_key = science.durability_description_key,
    durability_description_value = science.durability_description_value,
    weight = science.weight
  },

  -- Machines ----------------------------------------------------------------
  {
    type = "item",
    name = "condensate-extractor",
    icon = "__cataclysm__/graphics/icons/condensate-extractor.png",
    icon_size = 64,
    subgroup = "cataclysm-machines",
    order = "c-a[condensate-extractor]",
    place_result = "condensate-extractor",
    stack_size = 20,
    weight = 2000
  },
  {
    type = "item",
    name = "storm-siphon",
    icon = "__cataclysm__/graphics/icons/storm-siphon.png",
    icon_size = 64,
    subgroup = "cataclysm-machines",
    order = "c-b[storm-siphon]",
    place_result = "storm-siphon",
    stack_size = 20,
    weight = 3000
  },
  {
    type = "item",
    name = "storm-foundry",
    icon = "__cataclysm__/graphics/icons/storm-foundry.png",
    icon_size = 64,
    subgroup = "cataclysm-machines",
    order = "c-c[storm-foundry]",
    place_result = "storm-foundry",
    stack_size = 20,
    weight = 4000
  },
  {
    type = "item",
    name = "storm-fabricator",
    icon = "__cataclysm__/graphics/icons/storm-fabricator.png",
    icon_size = 64,
    subgroup = "cataclysm-machines",
    order = "c-d[storm-fabricator]",
    place_result = "storm-fabricator",
    stack_size = 20,
    weight = 5000
  },
  {
    type = "item",
    name = "storm-generator",
    icon = "__cataclysm__/graphics/icons/storm-generator.png",
    icon_size = 64,
    subgroup = "cataclysm-machines",
    order = "c-e[storm-generator]",
    place_result = "storm-generator",
    stack_size = 20,
    weight = 6000
  }
})

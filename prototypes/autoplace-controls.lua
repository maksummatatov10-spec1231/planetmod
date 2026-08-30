-- Cataclysm — autoplace controls (map generation GUI sliders).
-- Names are referenced by the planet's noise expressions (see map-gen.lua).

data:extend({
  {
    type = "autoplace-control",
    name = "stormite_ore",
    order = "b-e",
    category = "resource",
    resource_category = "basic-solid",
    richness = true
  },
  {
    type = "autoplace-control",
    name = "astrite_ore",
    order = "b-f",
    category = "resource",
    resource_category = "basic-solid",
    richness = true
  }
})

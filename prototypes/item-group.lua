-- Cataclysm — item group and subgroups.

data:extend({
  {
    type = "item-group",
    name = "cataclysm",
    order = "e-cataclysm",
    icon = "__cataclysm__/graphics/icons/cataclysm.png",
    icon_size = 128
  },
  {
    type = "item-subgroup",
    name = "cataclysm-resources",
    group = "cataclysm",
    order = "a"
  },
  {
    type = "item-subgroup",
    name = "cataclysm-intermediate",
    group = "cataclysm",
    order = "b"
  },
  {
    type = "item-subgroup",
    name = "cataclysm-machines",
    group = "cataclysm",
    order = "c"
  },
  {
    type = "item-subgroup",
    name = "cataclysm-decorative",
    group = "cataclysm",
    order = "d"
  }
})

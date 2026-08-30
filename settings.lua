-- Cataclysm — startup settings.

data:extend({
  {
    type = "int-setting",
    name = "cataclysm-superstorm-period",
    setting_type = "runtime-global",
    default_value = 30,
    minimum_value = 10,
    maximum_value = 120,
    order = "a"
  },
  {
    type = "bool-setting",
    name = "cataclysm-superstorms-enabled",
    setting_type = "runtime-global",
    default_value = true,
    order = "b"
  }
})

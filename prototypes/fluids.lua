-- Cataclysm — fluids.

data:extend({
  {
    type = "fluid",
    name = "cataclysm-storm-condensate",
    icon = "__cataclysm__/graphics/icons/storm-condensate.png",
    icon_size = 64,
    default_temperature = 20,
    max_temperature = 500,
    heat_capacity = "0.1kJ",
    base_color = { r = 0.12, g = 0.43, b = 0.42 },
    flow_color = { r = 0.18, g = 0.88, b = 0.78 },
    pressure_to_speed_ratio = 0.4,
    flow_to_energy_ratio = 0.59,
    gas_temperature = 200
  },
  {
    type = "fluid",
    name = "cataclysm-charged-condensate",
    icon = "__cataclysm__/graphics/icons/charged-storm-condensate.png",
    icon_size = 64,
    default_temperature = 200,
    max_temperature = 1000,
    heat_capacity = "0.2kJ",
    base_color = { r = 0.55, g = 0.85, b = 1.0 },
    flow_color = { r = 0.85, g = 1.0, b = 1.0 },
    pressure_to_speed_ratio = 0.4,
    flow_to_energy_ratio = 0.59,
    gas_temperature = 600
  }
})

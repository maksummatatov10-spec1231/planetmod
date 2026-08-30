-- Cataclysm — custom lightning entity.
--
-- Deep-copy of the vanilla Space Age "lightning" with:
--   * violet visual identity (shader colors + light color), per design
--     ("своя молния с фиолетовым визуалом");
--   * lower per-strike damage (60 vs 100) and lower energy transfer
--     (600MJ vs 1000MJ) than Fulgora's, compensated by a higher strike rate
--     set in planet.lua (design: "урон ниже на одну молнию, но чаще").
--
-- The engine lightning system (planet lightning_properties) uses this entity;
-- the superstorm script spawns it as well.

local lightning = table.deepcopy(data.raw.lightning["lightning"])
lightning.name = "cataclysm-lightning"
lightning.damage = { amount = 60, type = "electric" }
lightning.energy = "600MJ"

if lightning.graphics_set then
  lightning.graphics_set = table.deepcopy(lightning.graphics_set)
  lightning.graphics_set.shader_configuration = {
    { color = { 0.55, 0.25, 1, 0.8 },  distortion = 0.20, thickness = 0.20, power = 0.25 },
    { color = { 0.60, 0.30, 1, 1.0 },  distortion = 0.40, thickness = 1.00, power = 0.25 },
    { color = { 0.75, 0.40, 1, 1.0 },  distortion = 0.55, thickness = 1.00, power = 0.25 },
    { color = { 0.85, 0.50, 1, 0.6 },  distortion = 0.70, thickness = 0.75, power = 0.25 },
    { color = { 0.50, 0.20, 1, 0.3 },  distortion = 1.00, thickness = 0.50, power = 0.10 },
    { color = { 0.30, 0.10, 0.8, 0.0 }, distortion = 20.00, thickness = 0.50, power = 0.01 }
  }
end

if lightning.light then
  lightning.light = table.deepcopy(lightning.light)
  lightning.light.color = { 0.65, 0.35, 1 }
end

data:extend({ lightning })

-- Cataclysm — custom lightning entity.
--
-- Spec (user request, docs/LIGHTNING.md): "exactly the same lightning as
-- Fulgora, just a different color — a filter over it — and more frequent and
-- stronger".
--
-- Implementation: deep-copy of the vanilla Space Age "lightning" entity with
-- *zero* changes to the graphics/animation/sound logic (same bolt parameters,
-- cloud, explosion, ground streamers, strike effects, camera shake,
-- time_to_damage, effect_duration, source offset/variance, sound). The only
-- visual difference is the COLOR FILTER: the vanilla shader_configuration
-- colors (light blue) and light color are shifted to the Cataclysm violet,
-- keeping the exact same distortion/thickness/power/alpha values.
--
-- "Stronger": per-strike damage 150 electric (vanilla 100) and transferred
-- energy 2GJ (vanilla 1GJ) — the storm siphon's buffer matches (2GJ).
-- "More frequent": the planet's lightning_properties rate is 1/(60*5) per
-- chunk per tick (2x Fulgora's 1/(60*10)); see planet.lua.

local lightning = table.deepcopy(data.raw.lightning["lightning"])
lightning.name = "cataclysm-lightning"
lightning.damage = { amount = 150, type = "electric" }
lightning.energy = "2GJ"

-- Color filter: same shader layer layout as vanilla, violet colors only.
if lightning.graphics_set then
  lightning.graphics_set = table.deepcopy(lightning.graphics_set)
  lightning.graphics_set.shader_configuration = {
    { color = { 0.55, 0.25, 1, 0.8 },  distortion =  0.20, thickness = 0.20, power = 0.25 },
    { color = { 0.55, 0.25, 1, 1.0 },  distortion =  0.40, thickness = 1.00, power = 0.25 },
    { color = { 0.65, 0.30, 1, 1.0 },  distortion =  0.55, thickness = 1.00, power = 0.25 },
    { color = { 0.80, 0.45, 1, 0.6 },  distortion =  0.70, thickness = 0.75, power = 0.25 },
    { color = { 0.50, 0.20, 1, 0.3 },  distortion =  1.00, thickness = 0.50, power = 0.10 },
    { color = { 0.30, 0.10, 0.9, 0.0 }, distortion = 20.00, thickness = 0.50, power = 0.01 }
  }
end

-- Light filter: violet glow instead of the vanilla blue.
if lightning.light then
  lightning.light = table.deepcopy(lightning.light)
  lightning.light.color = { 0.65, 0.35, 1 }
end

data:extend({ lightning })

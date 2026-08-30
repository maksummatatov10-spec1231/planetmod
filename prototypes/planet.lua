-- Cataclysm — planet prototype and its space connection.

local asteroid_util = require("__space-age__.prototypes.planet.asteroid-spawn-definitions")

data:extend({
  {
    type = "planet",
    name = "cataclysm",
    icon = "__cataclysm__/graphics/icons/cataclysm.png",
    icon_size = 128,
    starmap_icon = "__cataclysm__/graphics/icons/starmap-cataclysm.png",
    starmap_icon_size = 512,
    gravity_pull = 10,
    distance = 45,
    orientation = 0.275,
    magnitude = 1.1,
    label_orientation = 0.15,
    order = "f[cataclysm]",
    subgroup = "planets",
    map_gen_settings = require("__cataclysm__.prototypes.map-gen").cataclysm(),
    pollutant_type = nil,
    solar_power_in_space = 60,
    platform_procession_set = {
      arrival = { "planet-to-platform-b", "platform-to-platform-b" },
      departure = { "platform-to-planet-a", "platform-to-platform-a" }
    },
    planet_procession_set = {
      arrival = { "platform-to-planet-b" },
      departure = { "planet-to-platform-a" }
    },
    surface_properties = {
      ["day-night-cycle"] = 15 * minute,
      ["magnetic-field"] = 95,
      ["solar-power"] = 15,
      pressure = 400,
      gravity = 12
    },
    lightning_properties = {
      -- 2x Fulgora's rate (Fulgora: 1/(60*10)): ~1 strike per chunk every
      -- 5 seconds. Per-strike damage/energy are higher than Fulgora's
      -- (150 electric / 2GJ, see cataclysm-lightning) — more frequent AND
      -- stronger, per the design spec (docs/LIGHTNING.md).
      lightnings_per_chunk_per_tick = 1 / (60 * 5),
      search_radius = 12.0,
      lightning_types = { "cataclysm-lightning" },
      lightning_multiplier_at_day = 0.25,
      lightning_multiplier_at_night = 1.0,
      priority_rules = {
        { type = "id", string = "storm-siphon", priority_bonus = 10000 },
        { type = "id", string = "storm-generator", priority_bonus = 2000 },
        { type = "id", string = "cataclysm-vent", priority_bonus = 90 },
        { type = "prototype", string = "electric-pole", priority_bonus = 10 },
        { type = "prototype", string = "power-switch", priority_bonus = 10 },
        { type = "prototype", string = "pipe", priority_bonus = 10 },
        { type = "prototype", string = "pump", priority_bonus = 10 },
        { type = "prototype", string = "offshore-pump", priority_bonus = 10 },
        { type = "prototype", string = "logistic-robot", priority_bonus = 100 },
        { type = "prototype", string = "construction-robot", priority_bonus = 100 },
        { type = "impact-soundset", string = "metal", priority_bonus = 1 }
      },
      exemption_rules = {
        { type = "prototype", string = "rail-support" },
        { type = "prototype", string = "legacy-straight-rail" },
        { type = "prototype", string = "legacy-curved-rail" },
        { type = "prototype", string = "straight-rail" },
        { type = "prototype", string = "curved-rail-a" },
        { type = "prototype", string = "curved-rail-b" },
        { type = "prototype", string = "half-diagonal-rail" },
        { type = "prototype", string = "rail-ramp" },
        { type = "prototype", string = "elevated-straight-rail" },
        { type = "prototype", string = "elevated-curved-rail-a" },
        { type = "prototype", string = "elevated-curved-rail-b" },
        { type = "prototype", string = "elevated-half-diagonal-rail" },
        { type = "prototype", string = "rail-signal" },
        { type = "prototype", string = "rail-chain-signal" },
        { type = "prototype", string = "locomotive" },
        { type = "prototype", string = "artillery-wagon" },
        { type = "prototype", string = "cargo-wagon" },
        { type = "prototype", string = "fluid-wagon" },
        { type = "prototype", string = "land-mine" },
        { type = "prototype", string = "wall" },
        { type = "prototype", string = "tree" },
        { type = "countAsRockForFilteredDeconstruction", string = "true" },
        { type = "prototype", string = "cargo-pod" },
        { type = "id", string = "cargo-pod-container" }
      }
    },
    asteroid_spawn_influence = 1,
    asteroid_spawn_definitions = asteroid_util.spawn_definitions(asteroid_util.aquilo_solar_system_edge, 0.9),
    persistent_ambient_sounds = {
      base_ambience = { filename = "__space-age__/sound/wind/base-wind-aquilo.ogg", volume = 0.5 },
      wind = { filename = "__space-age__/sound/wind/wind-fulgora.ogg", volume = 0.8 },
      crossfade = {
        order = { "wind", "base_ambience" },
        curve_type = "cosine",
        from = { control = 0.35, volume_percentage = 0.0 },
        to = { control = 2, volume_percentage = 100.0 }
      },
      semi_persistent = {
        {
          sound = {
            variations = {
              { filename = "__space-age__/sound/world/semi-persistent/distant-thunder-1.ogg", volume = 0.6 },
              { filename = "__space-age__/sound/world/semi-persistent/distant-thunder-2.ogg", volume = 0.6 },
              { filename = "__space-age__/sound/world/semi-persistent/distant-thunder-3.ogg", volume = 0.6 },
              { filename = "__space-age__/sound/world/semi-persistent/distant-thunder-4.ogg", volume = 0.6 }
            }
          },
          delay_mean_seconds = 25,
          delay_variance_seconds = 8
        },
        {
          sound = {
            variations = {
              { filename = "__space-age__/sound/world/semi-persistent/sand-wind-gust-1.ogg", volume = 0.4 },
              { filename = "__space-age__/sound/world/semi-persistent/sand-wind-gust-2.ogg", volume = 0.4 },
              { filename = "__space-age__/sound/world/semi-persistent/sand-wind-gust-3.ogg", volume = 0.4 },
              { filename = "__space-age__/sound/world/semi-persistent/sand-wind-gust-4.ogg", volume = 0.4 },
              { filename = "__space-age__/sound/world/semi-persistent/sand-wind-gust-5.ogg", volume = 0.4 }
            }
          },
          delay_mean_seconds = 15,
          delay_variance_seconds = 9
        }
      }
    }
  },
  {
    type = "space-connection",
    name = "aquilo-cataclysm",
    subgroup = "planet-connections",
    from = "aquilo",
    to = "cataclysm",
    order = "g.5",
    length = 60000,
    asteroid_spawn_definitions = asteroid_util.spawn_definitions(asteroid_util.aquilo_solar_system_edge)
  }
})

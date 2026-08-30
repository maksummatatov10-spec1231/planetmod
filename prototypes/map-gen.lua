-- Cataclysm — map generation: noise expressions and map_gen_settings.
--
-- Terrain/ore patterns are adapted from the proven Space Age Aquilo pattern
-- (starting_spot_at_angle + spot_noise + island peaks). Tiles and decoratives
-- are placed by probability expressions (tile.autoplace / entity.autoplace).

local planet_map_gen = {}

data:extend({
  { type = "noise-expression", name = "cataclysm_segmentation_multiplier", expression = 1 },
  { type = "noise-expression", name = "cataclysm_angle", expression = "map_seed_normalized * 3600" },
  { type = "noise-expression", name = "cataclysm_spot_size", expression = 30 },
  {
    type = "noise-expression",
    name = "cataclysm_starting_island",
    expression = "1 - distance * (cataclysm_segmentation_multiplier / 100)"
  },
  {
    type = "noise-expression",
    name = "cataclysm_starting_stormite",
    expression = "starting_spot_at_angle{angle = cataclysm_angle, distance = 40, radius = cataclysm_spot_size * 0.8, x_distortion = 0, y_distortion = 0}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_starting_astrite",
    expression = "starting_spot_at_angle{angle = cataclysm_angle + 120, distance = 90, radius = cataclysm_spot_size * 0.5, x_distortion = 0, y_distortion = 0}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_starting_lake",
    expression = "starting_spot_at_angle{angle = cataclysm_angle + 240, distance = 60, radius = cataclysm_spot_size * 0.9, x_distortion = 0, y_distortion = 0}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_starting_mask",
    expression = "clamp((distance - 300) / 40, -1, 1)"
  },
  {
    type = "noise-function",
    name = "cataclysm_spot_noise",
    parameters = { "seed", "count", "skip_offset", "region_size", "density", "radius", "favorability" },
    expression = "spot_noise{x = x, y = y, seed0 = map_seed, seed1 = seed, candidate_spot_count = count, suggested_minimum_candidate_point_spacing = 128, skip_span = 3, skip_offset = skip_offset, region_size = region_size, density_expression = density, spot_quantity_expression = radius * radius, spot_radius_expression = radius, hard_region_target_quantity = 0, spot_favorability_expression = favorability, basement_value = -1, maximum_spot_basement_radius = radius * 2}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_stormite_spots",
    expression = "cataclysm_spot_noise{seed = 987, count = 6, skip_offset = 0, region_size = 600 + 400 / control:stormite_ore:frequency, density = 1, radius = cataclysm_spot_size * sqrt(control:stormite_ore:size), favorability = 1}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_astrite_spots",
    expression = "cataclysm_spot_noise{seed = 988, count = 3, skip_offset = 1, region_size = 800 + 400 / control:astrite_ore:frequency, density = 1, radius = cataclysm_spot_size * 1.2 * sqrt(control:astrite_ore:size), favorability = 1}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_lake_spots",
    expression = "cataclysm_spot_noise{seed = 989, count = 5, skip_offset = 2, region_size = 700, density = 1, radius = cataclysm_spot_size * 1.4, favorability = 1}"
  },

  -- resource probability / richness
  -- `land_mask` (1 on land, 0 on water) keeps ore patches out of the lakes.
  {
    type = "noise-expression",
    name = "cataclysm_land_mask",
    expression = "(cataclysm_min_elevation(0) + 1) / 2"
  },
  {
    type = "noise-expression",
    name = "cataclysm_stormite_ore_probability",
    expression = "cataclysm_land_mask * (control:stormite_ore:size > 0) * (max(cataclysm_starting_stormite * 0.02, min(cataclysm_starting_mask, cataclysm_stormite_spots) * 0.015))"
  },
  {
    type = "noise-expression",
    name = "cataclysm_stormite_ore_richness",
    expression = "max(cataclysm_starting_stormite * 1800000, cataclysm_stormite_spots * 1440000) * control:stormite_ore:richness"
  },
  {
    type = "noise-expression",
    name = "cataclysm_astrite_ore_probability",
    expression = "cataclysm_land_mask * (control:astrite_ore:size > 0) * (max(cataclysm_starting_astrite * 0.02, min(cataclysm_starting_mask, cataclysm_astrite_spots) * 0.012))"
  },
  {
    type = "noise-expression",
    name = "cataclysm_astrite_ore_richness",
    expression = "max(cataclysm_starting_astrite * 480000, cataclysm_astrite_spots * 720000) * control:astrite_ore:richness"
  },

  -- terrain
  {
    type = "noise-expression",
    name = "cataclysm_island_peaks",
    expression = "max(1.7 * (0.3 + cataclysm_starting_island), 1.5 * (0.5 + max(cataclysm_starting_stormite, cataclysm_starting_astrite, cataclysm_starting_lake)))"
  },
  {
    type = "noise-function",
    name = "cataclysm_simple_billows",
    parameters = { "seed1", "octaves", "input_scale" },
    expression = "abs(quick_multioctave_noise{x = x, y = y, seed0 = map_seed, seed1 = seed1, input_scale = input_scale, output_scale = 1, offset_x = 10000, octaves = octaves, octave_input_scale_multiplier = 0.5, octave_output_scale_multiplier = 0.75})"
  },
  {
    type = "noise-expression",
    name = "cataclysm_elevation",
    expression = "lerp(blended, maxed, 0.5)",
    local_expressions = {
      maxed = "max(formation_clumped, formation_broken)",
      blended = "lerp(formation_clumped, formation_broken, 0.5)",
      formation_clumped = "-20 + 12 * max(cataclysm_island_peaks, random_island_peaks) + 8 * tri_crack",
      formation_broken = "-20 + 8 * max(cataclysm_island_peaks * 1.1, min(0., random_island_peaks - 0.2)) + 10 * (pow(voronoi_large * max(0, voronoi_large_cell * 1.2 - 0.2) + 0.5 * voronoi_small * max(0, aux + 0.1), 0.5))",
      random_island_peaks = "abs(amplitude_corrected_multioctave_noise{x = x, y = y, seed0 = map_seed, seed1 = 1000, input_scale = segmentation_mult / 1.2, offset_x = -10000, octaves = 6, persistence = 0.8, amplitude = 1})",
      voronoi_large = "voronoi_facet_noise{x = x + cataclysm_wobble_x * 2, y = y + cataclysm_wobble_y * 2, seed0 = map_seed, seed1 = 'cataclysm-cracks', grid_size = 24, distance_type = 'euclidean', jitter = 1}",
      voronoi_large_cell = "voronoi_cell_id{x = x + cataclysm_wobble_x * 2, y = y + cataclysm_wobble_y * 2, seed0 = map_seed, seed1 = 'cataclysm-cracks', grid_size = 24, distance_type = 'euclidean', jitter = 1}",
      voronoi_small = "voronoi_facet_noise{x = x + cataclysm_wobble_x * 2, y = y + cataclysm_wobble_y * 2, seed0 = map_seed, seed1 = 'cataclysm-cracks', grid_size = 10, distance_type = 'euclidean', jitter = 1}",
      tri_crack = "min(cataclysm_simple_billows{seed1 = 2000, octaves = 3, input_scale = segmentation_mult / 1.5}, cataclysm_simple_billows{seed1 = 3000, octaves = 3, input_scale = segmentation_mult / 1.2}, cataclysm_simple_billows{seed1 = 4000, octaves = 3, input_scale = segmentation_mult})",
      segmentation_mult = "cataclysm_segmentation_multiplier / 25"
    }
  },
  { type = "noise-expression", name = "cataclysm_temperature", expression = "temperature_basic - 30" },
  { type = "noise-expression", name = "cataclysm_aux_scale", expression = "cataclysm_segmentation_multiplier * 1.5" },
  {
    type = "noise-expression",
    name = "cataclysm_wobble_x",
    expression = "multioctave_noise{x = x, y = y, seed0 = map_seed, seed1 = 12243, octaves = 3, persistence = 0.65, input_scale = cataclysm_aux_scale / 100, output_scale = 0.35}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_wobble_y",
    expression = "multioctave_noise{x = x, y = y, seed0 = map_seed, seed1 = 13243, octaves = 3, persistence = 0.65, input_scale = cataclysm_aux_scale / 100, output_scale = 0.35}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_aux",
    expression = "0.5 + multioctave_noise{x = x + cataclysm_wobble_x * 300 / cataclysm_aux_scale, y = y + cataclysm_wobble_y * 300 / cataclysm_aux_scale, seed0 = map_seed, seed1 = 14243, octaves = 3, persistence = 0.7, input_scale = cataclysm_aux_scale / 25, output_scale = 1}"
  },

  -- tiles
  {
    type = "noise-function",
    name = "cataclysm_min_elevation",
    parameters = { "min_elevation" },
    expression = "-1 + 2 * (elevation > min_elevation)"
  },
  {
    type = "noise-expression",
    name = "cataclysm_tile_variant",
    expression = "multioctave_noise{x = x, y = y, persistence = 0.85, seed0 = map_seed, seed1 = 100, octaves = 3, input_scale = 1/6}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_elev01",
    expression = "-1 + 2 * elevation"
  },
  {
    type = "noise-expression",
    name = "cataclysm_lake_region",
    expression = "max(cataclysm_starting_lake * 0.8, min(cataclysm_starting_mask, cataclysm_lake_spots) * 0.8)"
  },
  -- Tiles follow the Aquilo additive pattern: the tile with the highest value
  -- wins, and 100 * cataclysm_min_elevation(0) makes the ground tiles strictly
  -- dominant above sea level while the ocean tiles dominate below.
  {
    type = "noise-expression",
    name = "cataclysm_ground_1",
    expression = "100 * cataclysm_min_elevation(0) - abs(cataclysm_tile_variant - 0.4) + elevation / 25 + 1"
  },
  {
    type = "noise-expression",
    name = "cataclysm_ground_2",
    expression = "100 * cataclysm_min_elevation(0) - abs(cataclysm_tile_variant + 0.4) + elevation / 25 + 1"
  },
  {
    type = "noise-expression",
    name = "cataclysm_lake",
    expression = "100 * cataclysm_min_elevation(-0.3) - 100 * cataclysm_min_elevation(0) + 200 * cataclysm_lake_region"
  },
  {
    type = "noise-expression",
    name = "cataclysm_lake_deep",
    expression = "-100 * cataclysm_min_elevation(-0.3)"
  },

  -- decoratives (entities)
  {
    type = "noise-expression",
    name = "cataclysm_trees",
    expression = "0.5 * (cataclysm_elev01 > 0.3) * cataclysm_simple_billows{seed1 = 7001, octaves = 3, input_scale = 1/24}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_rocks",
    expression = "0.5 * (cataclysm_elev01 > 0.2) * cataclysm_simple_billows{seed1 = 7002, octaves = 2, input_scale = 1/18}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_vents",
    expression = "0.3 * (cataclysm_elev01 > -0.2) * cataclysm_simple_billows{seed1 = 7003, octaves = 2, input_scale = 1/30}"
  },
  {
    type = "noise-expression",
    name = "cataclysm_spires",
    expression = "0.15 * (cataclysm_elev01 > 0.3) * cataclysm_simple_billows{seed1 = 7004, octaves = 2, input_scale = 1/60}"
  }
})

function planet_map_gen.cataclysm()
  return {
    property_expression_names = {
      elevation = "cataclysm_elevation",
      temperature = "cataclysm_temperature",
      moisture = "moisture_basic",
      aux = "cataclysm_aux",
      cliffiness = "cliffiness_basic",
      cliff_elevation = "cliff_elevation_from_elevation",
      ["entity:stormite-ore:probability"] = "cataclysm_stormite_ore_probability",
      ["entity:stormite-ore:richness"] = "cataclysm_stormite_ore_richness",
      ["entity:astrite-ore:probability"] = "cataclysm_astrite_ore_probability",
      ["entity:astrite-ore:richness"] = "cataclysm_astrite_ore_richness"
    },
    autoplace_controls = {
      stormite_ore = {},
      astrite_ore = {}
    },
    autoplace_settings = {
      ["tile"] = {
        settings = {
          ["cataclysm-ground-1"] = {},
          ["cataclysm-ground-2"] = {},
          ["cataclysm-lake"] = {},
          ["cataclysm-lake-deep"] = {}
        }
      },
      ["entity"] = {
        settings = {
          ["stormite-ore"] = {},
          ["astrite-ore"] = {},
          ["cataclysm-crystal-tree"] = {},
          ["cataclysm-rock"] = {},
          ["cataclysm-vent"] = {},
          ["cataclysm-ancient-spire"] = {}
        }
      }
    }
  }
end

return planet_map_gen

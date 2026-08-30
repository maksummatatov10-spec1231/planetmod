-- Cataclysm — surface tiles.
-- All tiles are renamed deep-copies of vanilla tiles (graphics reuse is a
-- deliberate V1 fallback; custom terrain art is planned for later versions).
-- Placement is driven by autoplace probability expressions in map-gen.lua.

local function copy_tile(source, name, overrides)
  local tile = table.deepcopy(data.raw.tile[source])
  tile.name = name
  tile.autoplace = nil
  tile.factoriopedia_alternative = nil
  for key, value in pairs(overrides) do
    tile[key] = value
  end
  return tile
end

-- Note: TilePrototype has no `group`/`subgroup` field, so tiles only get an
-- order; the terrain build menu is filtered by search instead.
data:extend({
  copy_tile("sand-3", "cataclysm-ground-1", {
    order = "a[cataclysm]-a[ground-1]",
    autoplace = { probability_expression = "cataclysm_ground_1" },
    map_color = { r = 0.42, g = 0.35, b = 0.58 },
    effect_color = { r = 0.35, g = 0.28, b = 0.5 }
  }),
  copy_tile("dry-dirt", "cataclysm-ground-2", {
    order = "a[cataclysm]-b[ground-2]",
    autoplace = { probability_expression = "cataclysm_ground_2" },
    map_color = { r = 0.34, g = 0.28, b = 0.5 },
    effect_color = { r = 0.28, g = 0.22, b = 0.42 }
  }),
  copy_tile("water", "cataclysm-lake", {
    order = "a[cataclysm]-c[lake]",
    fluid = "cataclysm-storm-condensate",
    autoplace = { probability_expression = "cataclysm_lake" },
    map_color = { r = 0.12, g = 0.38, b = 0.36 },
    effect_color = { r = 0.09, g = 0.3, b = 0.28 }
  }),
  copy_tile("deepwater", "cataclysm-lake-deep", {
    order = "a[cataclysm]-d[lake-deep]",
    fluid = "cataclysm-storm-condensate",
    autoplace = { probability_expression = "cataclysm_lake_deep" },
    map_color = { r = 0.06, g = 0.22, b = 0.2 },
    effect_color = { r = 0.05, g = 0.16, b = 0.15 }
  })
})

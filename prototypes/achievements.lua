-- Cataclysm — achievements.
--
-- Achievement types that the engine can track natively use prototype
-- conditions. Story/event achievements use the script-unlock pattern:
-- a "never naturally triggered" produce-achievement (huge amount) is defined
-- here and unlocked from control.lua via player.unlock_achievement().

local function scripted(name, order, icon)
  return {
    type = "produce-achievement",
    name = name,
    order = order,
    item_product = "cataclysmic-science-pack",
    amount = 1000000000, -- unreachable by production; script unlocks it
    limited_to_one_game = true, -- required by ProduceAchievementPrototype (2.1.17)
    icon = "__cataclysm__/graphics/achievement/" .. icon .. ".png",
    icon_size = 128
  }
end

data:extend({
  -- Progression --------------------------------------------------------------
  {
    type = "change-surface-achievement",
    name = "cataclysm-visit",
    order = "a[progress]-g[visit-planet]-z[cataclysm]",
    surface = "cataclysm",
    icon = "__cataclysm__/graphics/achievement/visit-cataclysm.png",
    icon_size = 128
  },
  {
    type = "research-with-science-pack-achievement",
    name = "cataclysm-research-with-pack",
    order = "e[research]-a[research-with]-z[cataclysmic]",
    science_pack = "cataclysmic-science-pack",
    icon = "__cataclysm__/graphics/achievement/research-with-cataclysmic.png",
    icon_size = 128
  },
  {
    type = "produce-achievement",
    name = "cataclysm-first-plate",
    order = "a[progress]-h[cataclysm]-a[first-plate]",
    item_product = "stormite-plate",
    amount = 1,
    limited_to_one_game = true,
    icon = "__cataclysm__/graphics/achievement/first-stormite-plate.png",
    icon_size = 128
  },
  {
    -- Scripted: fluid production cannot be a produce-achievement, so this is
    -- an unreachable produce threshold that control.lua unlocks at 10 000
    -- charged condensate produced.
    type = "produce-achievement",
    name = "cataclysm-charged-10k",
    order = "a[progress]-h[cataclysm]-b[charged-10k]",
    item_product = "cataclysm-voltaic-lattice",
    amount = 1000000000,
    limited_to_one_game = true,
    icon = "__cataclysm__/graphics/achievement/charged-condensate-10k.png",
    icon_size = 128
  },
  {
    type = "build-entity-achievement",
    name = "cataclysm-siphon-network",
    order = "a[progress]-h[cataclysm]-c[siphon-network]",
    to_build = "storm-siphon",
    amount = 8,
    icon = "__cataclysm__/graphics/achievement/storm-siphon-network.png",
    icon_size = 128
  },
  {
    -- Scripted: DepleteResourceAchievementPrototype in 2.x has no `resource`
    -- field (only amount), so the stormite-patch achievement is unlocked by
    -- script via on_resource_depleted (see control.lua).
    type = "produce-achievement",
    name = "cataclysm-deplete-stormite",
    order = "a[progress]-h[cataclysm]-d[deplete-stormite]",
    item_product = "cataclysmic-science-pack",
    amount = 1000000000,
    limited_to_one_game = true,
    icon = "__cataclysm__/graphics/achievement/deplete-stormite-patch.png",
    icon_size = 128
  },
  {
    type = "produce-per-hour-achievement",
    name = "cataclysm-science-1000",
    order = "a[progress]-h[cataclysm]-e[science-1000]",
    item_product = "cataclysmic-science-pack",
    amount = 1000,
    icon = "__cataclysm__/graphics/achievement/cataclysmic-science-1000.png",
    icon_size = 128
  },

  -- Scripted (story/event) ----------------------------------------------------
  scripted("cataclysm-survive-superstorm", "h[cataclysm]-f[survive-superstorm]", "survive-superstorm"),
  scripted("cataclysm-eye-of-the-storm", "h[cataclysm]-g[eye-of-the-storm]", "eye-of-the-storm"),
  scripted("cataclysm-what-was-here", "h[cataclysm]-h[what-was-here]", "what-was-here"),
  scripted("cataclysm-tech-master", "h[cataclysm]-i[tech-master]", "cataclysm-tech-master")
})

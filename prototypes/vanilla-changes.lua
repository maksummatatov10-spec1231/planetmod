-- Cataclysm — additive compatibility changes (runs in data-final-fixes).
-- Only additive, save-friendly edits to vanilla prototypes. Pattern: Maraxsis.

-- The survey pack must be craftable BEFORE cataclysm-planet-discovery can be
-- researched (it is the cost of that technology), so its recipe is granted by
-- a vanilla technology the player already has at that point.
local function unlock_survey_pack_recipe()
  local thruster = data.raw.technology["space-platform-thruster"]
  if thruster and thruster.effects then
    local has = false
    for _, e in ipairs(thruster.effects) do
      if e.type == "unlock-recipe" and e.recipe == "cataclysm-survey-pack" then
        has = true
        break
      end
    end
    if not has then
      table.insert(thruster.effects, {
        type = "unlock-recipe",
        recipe = "cataclysm-survey-pack"
      })
    end
  end
end

local CATACLYSM_PACKS = { "cataclysmic-science-pack", "cataclysm-survey-pack" }

local function add_cataclysmic_packs_to_labs()
  for _, lab in pairs(data.raw.lab) do
    local inputs = lab.inputs
    if inputs then
      local has_cryo = false
      for _, name in ipairs(inputs) do
        if name == "cryogenic-science-pack" then
          has_cryo = true
          break
        end
      end
      if has_cryo then
        for _, pack in ipairs(CATACLYSM_PACKS) do
          local present = false
          for _, name in ipairs(inputs) do
            if name == pack then
              present = true
              break
            end
          end
          if not present then
            table.insert(inputs, pack)
          end
        end
        table.sort(inputs)
      end
    end
  end
end

unlock_survey_pack_recipe()
add_cataclysmic_packs_to_labs()

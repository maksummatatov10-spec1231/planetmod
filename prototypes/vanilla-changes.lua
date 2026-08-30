-- Cataclysm — additive compatibility changes (runs in data-final-fixes).
-- Only additive, save-friendly edits to vanilla prototypes. Pattern: Maraxsis.

local function add_cataclysmic_pack_to_labs()
  for _, lab in pairs(data.raw.lab) do
    local inputs = lab.inputs
    if inputs and table.find(inputs, "cryogenic-science-pack") then
      if not table.find(inputs, "cataclysmic-science-pack") then
        table.insert(inputs, "cataclysmic-science-pack")
        table.sort(inputs)
      end
    end
  end
end

add_cataclysmic_pack_to_labs()

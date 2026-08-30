-- Cataclysm — additive compatibility changes (runs in data-final-fixes).
-- Only additive, save-friendly edits to vanilla prototypes. Pattern: Maraxsis.

local function add_cataclysmic_pack_to_labs()
  for _, lab in pairs(data.raw.lab) do
    local inputs = lab.inputs
    if inputs then
      local has_cryo = false
      local has_ours = false
      for _, name in ipairs(inputs) do
        if name == "cryogenic-science-pack" then
          has_cryo = true
        elseif name == "cataclysmic-science-pack" then
          has_ours = true
        end
      end
      if has_cryo and not has_ours then
        table.insert(inputs, "cataclysmic-science-pack")
        table.sort(inputs)
      end
    end
  end
end

add_cataclysmic_pack_to_labs()

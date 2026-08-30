-- Cataclysm — data-updates stage.
-- Runs after all mods' data.lua, before data-final-fixes. Additive only.

-- PlanetsLib (optional) compatibility:
--   * Register our planet in the shared orbit tree as a body orbiting Aquilo.
--     Other mods that reposition the solar system will move Cataclysm together
--     with its parent, and PlanetsLib consumers can read our orbit structure.
--   * Borrow Aquilo's ambient music tracks (2.1 supports multiple planets per
--     track, so no new tracks are created).
--   * Set the default import location for our items to Cataclysm.
--
-- Everything is guarded: without PlanetsLib the mod is fully standalone.
if mods["PlanetsLib"] then
  require("__PlanetsLib__.api")

  if type(PlanetsLib.update) == "function" then
    local ok, err = pcall(function()
      PlanetsLib:update{
        type = "planet",
        name = "cataclysm",
        orbit = {
          parent = { type = "planet", name = "aquilo" },
          distance = 45,
          orientation = 0.275
        }
      }
    end)
    if not ok then
      log("[Cataclysm] PlanetsLib:update failed: " .. tostring(err))
    end
  end

  if type(PlanetsLib.borrow_music) == "function" then
    pcall(PlanetsLib.borrow_music, PlanetsLib, "aquilo", data.raw.planet.cataclysm)
  end

  if type(PlanetsLib.set_default_import_location) == "function" then
    local items = {
      "stormite-ore",
      "astrite-ore",
      "stormite-plate",
      "astrite-crystal",
      "cataclysm-voltaic-lattice",
      "cataclysmic-science-pack",
      "condensate-extractor",
      "storm-siphon",
      "storm-foundry",
      "storm-fabricator",
      "storm-generator"
    }
    for _, item_name in ipairs(items) do
      pcall(PlanetsLib.set_default_import_location, PlanetsLib, item_name, "cataclysm")
    end
  end
end

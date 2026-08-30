-- Cataclysm — data stage entry point.
--
-- Order matters: groups → controls → items/fluids → categories → world objects
-- (resources, tiles, decoratives) → machines → recipes → tech → achievements →
-- map-gen → planet.

require("prototypes.item-group")
require("prototypes.autoplace-controls")
require("prototypes.items")
require("prototypes.fluids")
require("prototypes.sounds")
require("prototypes.recipe-categories")
require("prototypes.resources")
require("prototypes.tiles")
require("prototypes.decoratives")
require("prototypes.entities")
require("prototypes.lightning")
require("prototypes.recipes")
require("prototypes.technologies")
require("prototypes.achievements")
require("prototypes.map-gen")
require("prototypes.planet")

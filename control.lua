-- Cataclysm — control stage (runtime scripting).
--
-- Systems:
--   * Superstorm scheduler: every `cataclysm-superstorm-period` minutes a
--     superstorm hits the Cataclysm surface for 3 minutes. During the storm,
--     script-driven lightning strikes around players (the engine's own
--     lightning keeps running underneath).
--   * Scripted achievement unlocks that cannot be expressed with prototype
--     conditions (survive-superstorm, eye-of-the-storm, what-was-here,
--     tech-master).
--   * Ancient spire proximity reward (what-was-here).

local CATACLYSM_SURFACE = "cataclysm"
local CATACLYSM_ORBIT = "cataclysm-orbit"

local STORM_DURATION_TICKS = 3 * 60 * 60      -- 3 minutes
local STRIKE_INTERVAL = 20                    -- ticks between strike rolls per player
local STRIKE_CHANCE = 0.5                     -- base strike chance per roll
local STRIKE_CHANCE_PROTECTED = 0.25          -- after lightning-protection tech
local STRIKE_RADIUS = 22                      -- strikes land within this radius of the player
local SPIRE_CHECK_INTERVAL = 60
local SPIRE_RADIUS = 8
local SPIRE_REWARD = { { name = "astrite-crystal", count = 20 } }

local CATACLYSM_TECHS = {
  "cataclysm-condensate-extraction",
  "cataclysm-stormite-processing",
  "cataclysm-storm-siphon",
  "cataclysm-astrite-refining",
  "cataclysm-voltaic-lattice",
  "cataclysmic-science-pack",
  "cataclysm-storm-generator",
  "cataclysm-lightning-protection",
  "cataclysm-seismic-stabilization",
  "cataclysm-storm-platform-shield",
  "cataclysm-productivity",
  "cataclysm-storm-logistics"
}

local function get_storage()
  if not storage.cataclysm then
    storage.cataclysm = {
      storm = { state = "idle", timer = 0, ticks_left = 0, survivors = {} },
      spire_rewarded = {}
    }
  end
  return storage.cataclysm
end

script.on_init(function()
  get_storage()
end)

script.on_configuration_changed(function()
  get_storage()
end)

local function cataclysm_surface()
  return game.surfaces[CATACLYSM_SURFACE]
end

local function storm_enabled()
  local setting = settings.global["cataclysm-superstorms-enabled"]
  return setting and setting.value ~= false
end

local function storm_period_ticks()
  local setting = settings.global["cataclysm-superstorm-period"]
  local minutes = 45
  if setting then
    minutes = setting.value
  end
  return minutes * 60 * 60
end

local function announce(surface, message_key)
  game.print({ message_key })
  if surface then
    for _, player in pairs(game.players) do
      if player.connected and player.surface == surface then
        player.print({ message_key }, { r = 1.0, g = 0.85, b = 0.3 })
      end
    end
  end
end

local function storm_is_active()
  return get_storage().storm.state == "active"
end

local function strike_near(surface, position, force, far_only)
  local radius_min, radius_max
  if far_only then
    radius_min, radius_max = 28, 42 -- seismic stabilization: keep strikes away from the player
  else
    radius_min, radius_max = 10, STRIKE_RADIUS
  end
  local angle = math.random() * 2 * math.pi
  local dist = radius_min + math.random() * (radius_max - radius_min)
  local pos = {
    x = position.x + dist * math.cos(angle),
    y = position.y + dist * math.sin(angle)
  }
  -- Primary: spawn the real lightning entity (visual + strike damage).
  -- pcall fallback: explosion visuals only, so a hiccup can never crash the game.
  local created = pcall(function()
    surface.create_entity{ name = "lightning", position = pos, force = force }
  end)
  if not created then
    pcall(function()
      surface.create_entity{ name = "explosion", position = pos }
    end)
  end
end

local function storm_strike_tick()
  if not storm_is_active() then
    return
  end
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      local force = player.force
      local protected = force.technologies["cataclysm-lightning-protection"]
        and force.technologies["cataclysm-lightning-protection"].researched
      local seismic = force.technologies["cataclysm-seismic-stabilization"]
        and force.technologies["cataclysm-seismic-stabilization"].researched
      local chance = protected and STRIKE_CHANCE_PROTECTED or STRIKE_CHANCE
      if math.random() < chance then
        strike_near(surface, player.position, force, seismic)
      end
    end
  end
end

-- Superstorm lifecycle ------------------------------------------------------

local function start_superstorm(surface)
  local storm = get_storage().storm
  storm.state = "active"
  storm.ticks_left = STORM_DURATION_TICKS
  storm.timer = 0
  storm.survivors = {}
  -- The survivors are the players that are here when the storm breaks.
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      storm.survivors[player.index] = true
    end
  end
  announce(surface, "cataclysm-message-superstorm-start")
end

local function end_superstorm(surface)
  local storm = get_storage().storm
  storm.state = "idle"
  storm.timer = 0
  announce(surface, "cataclysm-message-superstorm-end")
  -- Surviving the storm: still alive and on the surface when it ends.
  for player_index in pairs(storm.survivors) do
    local player = game.players[player_index]
    if player and player.connected and player.character and player.surface == surface then
      player.unlock_achievement("cataclysm-survive-superstorm")
    end
  end
  storm.survivors = {}
end

local function superstorm_scheduler_tick()
  if not storm_enabled() then
    return
  end
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  local storm = get_storage().storm
  storm.timer = storm.timer + 60
  if storm.state == "idle" then
    if storm.timer >= storm_period_ticks() then
      start_superstorm(surface)
    end
  else
    storm.ticks_left = storm.ticks_left - 60
    if storm.ticks_left <= 0 then
      end_superstorm(surface)
    end
  end
end

-- Eye of the storm: ride the orbit above Cataclysm during a superstorm. -----

local function eye_of_the_storm_tick()
  if not storm_is_active() then
    return
  end
  local orbit = game.surfaces[CATACLYSM_ORBIT]
  if not orbit then
    return
  end
  for _, player in pairs(game.players) do
    if player.connected and player.surface == orbit then
      player.unlock_achievement("cataclysm-eye-of-the-storm")
    end
  end
end

-- What was here? -------------------------------------------------------------
-- Finding an ancient spire unlocks the achievement and a small reward.

local function spire_check_tick()
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      local storage_table = get_storage()
      if not storage_table.spire_rewarded[player.index] then
        local spires = surface.find_entities_filtered{
          position = player.position,
          radius = SPIRE_RADIUS,
          name = "cataclysm-ancient-spire"
        }
        if spires and #spires > 0 then
          storage_table.spire_rewarded[player.index] = true
          player.unlock_achievement("cataclysm-what-was-here")
          pcall(function()
            local chest = surface.create_entity{
              name = "wooden-chest",
              position = spires[1].position,
              force = player.force
            }
            chest.get_inventory(defines.inventory.chest).insert(SPIRE_REWARD)
          end)
        end
      end
    end
  end
end

-- Master of the storm --------------------------------------------------------
-- All cataclysmic technologies researched.

local function all_cataclysm_techs_researched(force)
  for _, tech_name in pairs(CATACLYSM_TECHS) do
    local tech = force.technologies[tech_name]
    if not tech or not tech.researched then
      return false
    end
  end
  return true
end

script.on_event(defines.events.on_research_finished, function(event)
  local research = event.research
  if not research then
    return
  end
  for _, tech_name in pairs(CATACLYSM_TECHS) do
    if research.name == tech_name then
      if all_cataclysm_techs_researched(research.force) then
        for _, player in pairs(game.players) do
          if player.connected and player.force == research.force then
            player.unlock_achievement("cataclysm-tech-master")
          end
        end
      end
      break
    end
  end
end)

-- Tick handlers ---------------------------------------------------------------

script.on_nth_tick(60, function()
  superstorm_scheduler_tick()
  eye_of_the_storm_tick()
  spire_check_tick()
end)

script.on_nth_tick(STRIKE_INTERVAL, function()
  storm_strike_tick()
end)

-- Cataclysm — control stage (runtime scripting).
--
-- Systems:
--   * Superstorm scheduler: every `cataclysm-superstorm-period` minutes a
--     superstorm hits the Cataclysm surface for 3 minutes. During the storm,
--     script-driven lightning strikes around players AND extra strikes on
--     storm siphons (siphons charge faster — the risk/reward of the storm).
--     The engine's own lightning keeps running underneath.
--   * Scripted achievement unlocks that cannot be expressed with prototype
--     conditions. NOTE: Factorio 2.x has no machine recipe-finished event, so
--     production-based achievements read the force's production statistics
--     (LuaFlowStatistics.output_counts) instead — cheap and exact.
--   * Ancient spire proximity reward (what-was-here).
--
-- Fallbacks: every risky call is wrapped in pcall; without the engine lightning
-- entity the storm falls back to explosions; with superstorms disabled via the
-- setting only the engine lightning remains. storage is migrated in-place.

local CATACLYSM_SURFACE = "cataclysm"
local CATACLYSM_LIGHTNING = "cataclysm-lightning"

local STORM_DURATION_TICKS = 3 * 60 * 60      -- 3 minutes
local STRIKE_INTERVAL = 25                    -- ticks between strike rolls per player
local STRIKE_CHANCE = 0.4                     -- base strike chance per roll
local STRIKE_CHANCE_PROTECTED = 0.2           -- after lightning-protection tech
local STRIKE_RADIUS = 22                      -- strikes land within this radius of the player
local SIPHON_STRIKE_INTERVAL = 30             -- ticks between siphon strike rolls
local SIPHON_STRIKE_LIMIT = 6                 -- max siphons checked per roll
local SIPHON_STRIKE_CHANCE = 0.5
local SPIRE_CHECK_INTERVAL = 60
local SPIRE_RADIUS = 8
local SPIRE_REWARD = { { name = "astrite-crystal", count = 20 } }

local LATTICE_ITEM = "cataclysm-voltaic-lattice"
local CHARGED_FLUID = "cataclysm-charged-condensate"
local CHARGED_ACHIEVEMENT_AMOUNT = 10000

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
    storage.cataclysm = {}
  end
  local s = storage.cataclysm
  -- In-place migration: fill defaults for keys added after 0.1.0.
  if not s.storm then
    s.storm = { state = "idle", timer = 0, ticks_left = 0, survivors = {} }
  end
  if not s.storm.lattice_baseline then
    s.storm.lattice_baseline = {}
  end
  if not s.storm.eye_unlocked then
    s.storm.eye_unlocked = {}
  end
  if not s.spire_rewarded then
    s.spire_rewarded = {}
  end
  if not s.charged_unlocked then
    s.charged_unlocked = {}
  end
  return s
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
  local minutes = 30
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

local function unlock(player, achievement_name)
  if player and achievement_name then
    pcall(function()
      player.unlock_achievement(achievement_name)
    end)
  end
end

local function spawn_lightning(surface, position, force)
  -- Primary: spawn the real lightning entity (visual + strike damage).
  -- Fallback: explosion visuals only, so a hiccup can never crash the game.
  local created = pcall(function()
    surface.create_entity{ name = CATACLYSM_LIGHTNING, position = position, force = force }
  end)
  if not created then
    pcall(function()
      surface.create_entity{ name = "explosion", position = position }
    end)
  end
end

-- Positional storm audio. The named sounds (cataclysm-thunder-far/near) are
-- defined in prototypes/sounds.lua and reference game audio files. All calls
-- are pcall-guarded: missing audio can never crash the storm logic.
local function play_sound_near(surface, path, position, min_offset, max_offset, volume)
  pcall(function()
    local angle = math.random() * 2 * math.pi
    local dist = min_offset + math.random() * (max_offset - min_offset)
    surface.play_sound{
      path = path,
      position = {
        x = position.x + dist * math.cos(angle),
        y = position.y + dist * math.sin(angle)
      },
      volume = volume or 1
    }
  end)
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
  spawn_lightning(surface, pos, force)
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
        -- A strike is usually followed by a distant rumble.
        if math.random() < 0.5 then
          play_sound_near(surface, "cataclysm-thunder-far", player.position, 25, 50, 0.6)
        end
      end
    end
  end
end

-- During a superstorm siphons get extra strikes: they absorb them as energy,
-- so the storm rewards a properly grounded base (design: risk/reward loop).
local function siphon_strikes_tick()
  if not storm_is_active() then
    return
  end
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  local siphons = surface.find_entities_filtered{
    name = "storm-siphon",
    limit = SIPHON_STRIKE_LIMIT
  }
  for _, siphon in pairs(siphons) do
    if siphon.valid and math.random() < SIPHON_STRIKE_CHANCE then
      spawn_lightning(surface, siphon.position, siphon.force)
    end
  end
end

-- During a superstorm distant thunder rumbles around players on the surface.
local function storm_ambience_tick()
  if not storm_is_active() then
    return
  end
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      if math.random() < 0.35 then
        play_sound_near(surface, "cataclysm-thunder-far", player.position, 30, 60, 0.55)
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
  -- eye-of-the-storm baseline: lattices already produced before the storm.
  storm.eye_unlocked = {}
  storm.lattice_baseline = {}
  for _, force in pairs(game.forces) do
    storm.lattice_baseline[force.index] = item_output_total(force, surface, LATTICE_ITEM) or 0
  end
  announce(surface, "cataclysm-message-superstorm-start")
  -- The storm announces itself: a sharp crack close to everyone on the surface.
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      play_sound_near(surface, "cataclysm-thunder-near", player.position, 6, 14, 0.9)
    end
  end
end

local function end_superstorm(surface)
  local storm = get_storage().storm
  storm.state = "idle"
  storm.timer = 0
  announce(surface, "cataclysm-message-superstorm-end")
  -- Retreating rumble as the storm rolls away.
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      play_sound_near(surface, "cataclysm-thunder-far", player.position, 20, 45, 0.7)
    end
  end
  -- Surviving the storm: still alive and on the surface when it ends.
  for player_index in pairs(storm.survivors) do
    local player = game.players[player_index]
    if player and player.connected and player.character and player.surface == surface then
      unlock(player, "cataclysm-survive-superstorm")
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

-- What was here? -------------------------------------------------------------
-- Finding an ancient spire unlocks the achievement and a small reward.

local function spire_check_tick()
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  local storage_table = get_storage()
  for _, player in pairs(game.players) do
    if player.connected and player.character and player.surface == surface then
      if not storage_table.spire_rewarded[player.index] then
        local spires = surface.find_entities_filtered{
          position = player.position,
          radius = SPIRE_RADIUS,
          name = "cataclysm-ancient-spire"
        }
        if spires and #spires > 0 then
          storage_table.spire_rewarded[player.index] = true
          unlock(player, "cataclysm-what-was-here")
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

-- Production-statistics achievements -----------------------------------------
-- Factorio 2.x has no machine recipe-finished event, so we read the force's
-- production statistics (LuaFlowStatistics.output_counts), which include
-- productivity bonuses and are exact.
--   * eye-of-the-storm: a voltaic lattice is crafted during a superstorm.
--   * charged-10k: 10 000 charged condensate produced (fluid production cannot
--     be a prototype produce-achievement).

local function item_output_total(force, surface, item_name)
  local ok, total = pcall(function()
    local stats = force.get_item_production_statistics(surface)
    return stats.output_counts[item_name] or 0
  end)
  if ok then
    return total
  end
  return nil
end

local function fluid_output_total(force, surface, fluid_name)
  local ok, total = pcall(function()
    local stats = force.get_fluid_production_statistics(surface)
    return stats.output_counts[fluid_name] or 0
  end)
  if ok then
    return total
  end
  return nil
end

local function achievement_check_tick()
  local surface = cataclysm_surface()
  if not surface then
    return
  end
  local storage_table = get_storage()
  local storm = storage_table.storm
  local storm_active = storm.state == "active"

  for _, force in pairs(game.forces) do
    -- Eye of the storm: lattice crafted while the storm is active.
    if storm_active and not storm.eye_unlocked[force.index] then
      local total = item_output_total(force, surface, LATTICE_ITEM)
      if total and total > (storm.lattice_baseline[force.index] or 0) then
        storm.eye_unlocked[force.index] = true
        for _, player in pairs(game.players) do
          if player.connected and player.force == force then
            unlock(player, "cataclysm-eye-of-the-storm")
          end
        end
      end
    end
    -- Charged condensate: 10 000 units produced.
    if not storage_table.charged_unlocked[force.index] then
      local total = fluid_output_total(force, surface, CHARGED_FLUID)
      if total and total >= CHARGED_ACHIEVEMENT_AMOUNT then
        storage_table.charged_unlocked[force.index] = true
        for _, player in pairs(game.players) do
          if player.connected and player.force == force then
            unlock(player, "cataclysm-charged-10k")
          end
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
            unlock(player, "cataclysm-tech-master")
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
  storm_ambience_tick()
  spire_check_tick()
  achievement_check_tick()
end)

script.on_nth_tick(STRIKE_INTERVAL, function()
  storm_strike_tick()
end)

script.on_nth_tick(SIPHON_STRIKE_INTERVAL, function()
  siphon_strikes_tick()
end)

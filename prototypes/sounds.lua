-- Cataclysm — named sounds (SoundPrototype).
--
-- Scripted superstorm audio. Every file is referenced from the base or
-- Space Age game data by path (__base__/sound, __space-age__/sound): the
-- files ship with the game itself, so the mod ships zero audio bytes and
-- there are no redistribution/licensing concerns. This is the standard
-- approach used by major mods.
--
-- All machines (deep-copies of vanilla prototypes: offshore-pump,
-- lightning-collector, foundry, electromagnetic-plant, steam-turbine)
-- already inherit battle-tested working sounds; the lightning entity
-- inherits the Space Age lightning strike sound. What is missing from
-- inheritance is *scripted* storm audio, defined here:
--   * cataclysm-thunder-far  — distant thunder rumble (during a superstorm)
--   * cataclysm-thunder-near — sharp strike crack (storm start/end cues)
--
-- Fallback: control.lua wraps every play_sound in pcall, so a missing sound
-- can never crash the storm logic — the storm just gets quieter.

local function variations(prefix, count, volume)
  local vars = {}
  for i = 1, count do
    vars[i] = { filename = prefix .. "-" .. i .. ".ogg", volume = volume }
  end
  return vars
end

data:extend({
  {
    type = "sound",
    name = "cataclysm-thunder-far",
    category = "environment",
    audible_distance_modifier = 3.0,
    allow_random_repeat = true,
    variations = variations("__space-age__/sound/world/semi-persistent/distant-thunder", 4, 0.6)
  },
  {
    type = "sound",
    name = "cataclysm-thunder-near",
    category = "explosion",
    audible_distance_modifier = 2.0,
    allow_random_repeat = true,
    variations = variations("__space-age__/sound/explosions/lightning-effect", 5, 0.8)
  }
})

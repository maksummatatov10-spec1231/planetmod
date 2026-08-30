# Docs schema notes — collected from lua-api.factorio.com/latest (v2.1.17)

Format: type page -> REQUIRED fields (rows WITHOUT "optional" in the properties
table), OR-required noted separately, then optional notable fields.
Base classes: PrototypeBase REQUIRES: type, name (everything else optional).
Prototype: all optional (factoriopedia_alternative, custom_tooltip_fields).

- ProduceAchievementPrototype ('produce-achievement')
  REQUIRED: amount, limited_to_one_game
  OR-required: item_product | fluid_product ("Mandatory if the other is not defined")
  optional: icons, icon, icon_size, steam_stats_name, allowed_without_fight

- ProducePerHourAchievementPrototype ('produce-per-hour-achievement')
  REQUIRED: amount   (NO limited_to_one_game!)
  OR-required: item_product | fluid_product

- ResearchWithSciencePackAchievementPrototype ('research-with-science-pack-achievement')
  REQUIRED: science_pack
  optional: amount

- BuildEntityAchievementPrototype ('build-entity-achievement')
  REQUIRED: to_build
  optional: amount, limited_to_one_game, within

- ChangedSurfaceAchievementPrototype ('change-surface-achievement')
  REQUIRED: (none own)   optional: surface

- ItemPrototype ('item')
  REQUIRED: stack_size
  optional: icons, icon, icon_size, dark_background_icons, dark_background_icon,
            dark_background_icon_size, place_result, place_as_equipment_result,
            fuel_category, burnt_result, spoil_result, spoil_quality_min/max, ...

- FluidPrototype ('fluid')
  REQUIRED: default_temperature, base_color, flow_color
  optional: visualization_color, max_temperature, heat_capacity, fuel_value,
            emissions_multiplier, gas_temperature, draw_as_glow, auto_barrel,
            spent_fluid, icons, icon, icon_size

- ItemGroup ('item-group'): REQUIRED: (none own). optional: icons, icon, icon_size, order_in_recipe. Limit: 255 instances.
- ItemSubGroup ('item-subgroup'): REQUIRED: group.
- RecipeCategory ('recipe-category'): REQUIRED: (none own). NOTE: "crafting" category cannot contain fluid ingredients/products.
- AutoplaceControl ('autoplace-control'): REQUIRED: category (enum: "resource"|"terrain"|"cliff"|"enemy"). optional: richness, can_be_disabled, related_to_fight_achievements, hidden (overridden). Limit: 255 instances.

- RecipePrototype ('recipe'): REQUIRED: (none marked; engine OR-requires ingredients | results). optional: categories, crafting_machine_tint, icons, icon, icon_size, ingredients, results, main_product, energy_required, emissions_multiplier, maximum_productivity, requester_paste_multiplier, overload_multiplier, allow_inserter_overload, enabled, hide_from_stats, hide_from_player_crafting, hide_from_bonus_gui, allow_decomposition, allow_as_intermediate, ...
- TechnologyPrototype ('technology'): REQUIRED: (none marked); OR-required: unit | research_trigger ("Mandatory if unit is not defined"). optional: icons, icon, icon_size, upgrade, enabled, essential, visible_when_disabled, ignore_tech_cost_multiplier, allows_productivity, max_level, prerequisites, show_levels_info, effects.
- TilePrototype ('tile'): REQUIRED: collision_mask, layer, variants, map_color. optional: layer_group, build_animations, icons, icon, icon_size, walking_sound, walking_speed_modifier, vehicle_friction_modifier, decorative_removal_probability, allowed_neighbors, ...

- PlanetPrototype ('planet'): own optional (map_seed_offset, entities_require_heating, pollutant_type, persistent_ambient_sounds, surface_render_parameters, player_effects, ticks_between_player_effects, map_gen_settings, surface_properties, lightning_properties). Inherits SpaceLocationPrototype: REQUIRED: distance, orientation; optional: gravity_pull, magnitude, parked_platforms_orientation, label_orientation, draw_orbit, solar_power_in_space, asteroid_spawn_influence, fly_condition, auto_save_on_first_trip, procession_*.
- LightningPrototype ('lightning'): REQUIRED: effect_duration. optional: graphics_set, sound, attracted_volume_modifier, strike_effect, attractor_hit_effect, source_offset, source_variance, damage, energy, time_to_damage (<= effect_duration). Inherits EntityPrototype (flags required).
- SpaceConnectionPrototype ('space-connection'): REQUIRED: from, to. optional: length, asteroid_spawn_definitions, icons, icon, icon_size.
- ResourcePrototype page: 404 (as previously noted) — resources documented elsewhere; validate via vanilla instance + EntityPrototype chain.

- LightningAttractorPrototype ('lightning-attractor'): REQUIRED: (none own). OR-conditional: energy_source "Mandatory if efficiency > 0". optional: chargable_graphics, lightning_strike_offset, efficiency (>=0), range_elongation. Chain: EntityWithOwner -> EntityWithHealth -> EntityPrototype -> Prototype -> PrototypeBase.
- SoundPrototype ('sound'): REQUIRED: type ("sound"), name. optional: category, priority, aggregation, allow_random_repeat, audible_distance_modifier, game_controller_vibration_data, advanced_volume_control, speed_smoothing_window_size, variations, filename, volume, min/max_volume, preload, speed, min/max_speed, modifiers.
- SimpleEntityPrototype ('simple-entity'): REQUIRED: (none own). optional: count_as_rock_for_filtered_deconstruction, render_layer, secondary_draw_order, random_animation_offset, random_variation_on_create, shuffled_variation_on_chunk_generated, pictures, picture, animations, lower_render_layer, lower_pictures, stateless_visualisation_variations. Chain: EntityWithHealth -> Entity.

- GeneratorPrototype ('generator'): REQUIRED: energy_source, fluid_box, fluid_usage_per_tick, maximum_temperature. optional: output_fluid_box, pictures, effectivity, smoke, burns_fluid, scale_fluid_usage, destroy_non_fuel_fluid, two_direction_only, perceived_performance, max_power_output, spent_fluid. Constraint: fluid_box must have filter if max_power_output not defined.
- OffshorePumpPrototype ('offshore-pump'): REQUIRED: fluid_box, pumping_speed, fluid_source_offset, energy_source, energy_usage. optional: perceived_performance, graphics_set, remove_on_tile_collision, always_draw_fluid, circuit_wire_max_distance, draw_copper_wires, draw_circuit_wires, circuit_connector.

- ResourceEntityPrototype ('resource'): REQUIRED: stage_counts. optional: stages, infinite, highlight, randomize_visual_position, map_grid, draw_stateless_visualisation_under_building, minimum, normal, infinite_depletion_amount, resource_patch_search_radius, category, walking_sound (Sound), driving_sound (InterruptibleSound), stages_effect, effect_animation_period, effect_animation_period_deviation, effect_darkness_multiplier, min_effect_alpha. Chain: Entity -> Prototype -> PrototypeBase.
- NamedNoiseExpression ('noise-expression'): REQUIRED: expression. optional: local_expressions, local_functions, intended_property. (order overridden для GUI-альтернатив)
- NamedNoiseFunction ('noise-function'): REQUIRED: parameters (array[string]), expression. optional: local_expressions, local_functions.

## Добрано 2026-08-30 (0.2.3) — завершение сбора всех 26 типов

- ResourceEntityPrototype ('resource') — страница называется НЕ ResourcePrototype.html, а ResourceEntityPrototype.html: REQUIRED stage_counts; optional: stages, infinite, highlight, randomize_visual_position, map_grid, draw_stateless_visualisation_under_building, minimum, normal, infinite_depletion_amount, resource_patch_search_radius, category (ResourceCategoryID), walking_sound (Sound), driving_sound (InterruptibleSound), stages_effect, effect_animation_period, effect_animation_period_deviation, effect_darkness_multiplier, min_effect_alpha, max_effect_alpha, mining_visualisation_tint, tree_removal_probability, tree_removal_max_distance. Условия: minimum/normal не 0 при infinite=true.
- NamedNoiseExpression ('noise-expression') — страница называется NamedNoiseExpression.html: REQUIRED expression; optional local_expressions, local_functions, intended_property.
- NamedNoiseFunction ('noise-function') — страница NamedNoiseFunction.html: REQUIRED parameters (array[string]) + expression; optional local_expressions, local_functions.
- GeneratorPrototype ('generator'): REQUIRED energy_source, fluid_box, fluid_usage_per_tick, maximum_temperature; optional output_fluid_box, pictures (GeneratorPictureSet), effectivity, smoke, burns_fluid, scale_fluid_usage, destroy_non_fuel_fluid, two_direction_only, perceived_performance, max_power_output, spent_fluid. Условие: fluid_box обязан иметь filter, если max_power_output не задан. (heating_energy в доке генератора не показан, но есть у ванильного steam-turbine — донор покрывает.)
- OffshorePumpPrototype ('offshore-pump'): REQUIRED fluid_box, pumping_speed, fluid_source_offset, energy_source, energy_usage; optional perceived_performance, graphics_set, remove_on_tile_collision, always_draw_fluid, circuit_wire_max_distance, draw_copper_wires, draw_circuit_wires, circuit_connector. tile_width/tile_height в доке не показаны, но есть у ванильного offshore-pump (база entities.lua:1971) — донор покрывает.
- EntityPrototype (abstract): собственных обязательных полей НЕТ (flags — optional, подтверждено). Chain children подтверждён (LightningPrototype и SimpleEntityPrototype наследуют EntityWithHealth/EntityWithOwner/Entity).
- EntityWithHealthPrototype: max_health в доке помечен optional (в доке SimpleEntity/Generator/OffshorePump).
- CraftingMachinePrototype (abstract, для assembling-machine): REQUIRED energy_usage, crafting_speed, crafting_categories, energy_source; optional fluid_boxes, effect_receiver, module_slots, quality_affects_module_slots, allowed_effects, allowed_module_categories, show_recipe_icon, return_ingredients_on_change, draw_entity_info_icon_background, quality_affects_energy_usage.
- ToolPrototype ('tool'): «Items with a durability» — durability живёт на ToolPrototype в 2.x; мод не использует tool (science pack = item, подтверждено ванилью).
- Мод-настройки (int-setting / bool-setting): в индексе прототипов lua-api их НЕТ (страницы BoolSettingPrototype/IntSettingPrototype → 404). Проверка по официальной вики Tutorial:Mod_settings: int-setting требует default_value (min/max/allowed_values optional), bool-setting требует default_value. Поля мода (default_value, minimum_value, maximum_value, setting_type, order) валидны.
- FluidPrototype 2.1.17 полный список собственных полей: icons, icon, icon_size, default_temperature (req), base_color (req), flow_color (req), visualization_color, max_temperature, heat_capacity, fuel_value, emissions_multiplier, gas_temperature, draw_as_glow, auto_barrel, spent_fluid. pressure_to_speed_ratio/flow_to_energy_ratio — НЕТ (1.1-эра; удалены из fluids.lua в 0.2.3).
- SpaceLocationPrototype (база PlanetPrototype): REQUIRED distance, orientation; optional gravity_pull, magnitude, parked_platforms_orientation, label_orientation, draw_orbit, solar_power_in_space, asteroid_spawn_influence, fly_condition, auto_save_on_first_trip, procession_graphic_catalogue, procession_audio_catalogue, platform_procession_set, planet_procession_set, starmap_icon, starmap_icon_size, starmap_icon_orientation, asteroid_spawn_definitions, platform_surface_render_parameters, hidden (переопределён), subgroup.
- Лимиты (подтверждено): autoplace-control 255, item-group 255, tile 65535.
- Справочно: ваниль 2.x data.raw = 263 типа, 4943 имени (names_by_type в data_raw_mod.json); типы wall→'stone-wall', explosion 'small-explosion' переименован в 'small-explosion-hit' (мод ссылался на 1.1-имя — исправлено в 0.2.3); exemption_rules Фулгоры тоже содержит 1.1-имя 'wall' — движок такие правила игнорирует.

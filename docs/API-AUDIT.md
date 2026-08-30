# Аудит прототипов Cataclysm — полный отчёт

> Задача: «проверить абсолютно все прототипы мода» по контрольному списку
> официальной документации и собрать информацию в файлы.
>
> Дата проверки: 2026-08-30. Версия мода: 0.2.0.
> Источники:
> - [Индекс прототипов lua-api.factorio.com/latest](https://lua-api.factorio.com/latest/index-prototype.html) (версия 2.1.17, маркер Space Age) — контрольный список;
> - страницы прототипов и типов с этого сайта (по одной на каждый используемый тип);
> - ванильные данные wube/factorio-data 2.x (`/tmp/fd`, base + space-age);
> - официальная вики (мод-настройки): https://wiki.factorio.com/Tutorial:Mod_settings

## 0. Как проводилась проверка

1. Собран фактический список всех `type = "..."`, которые мод определяет в
   data-стадии (grep по `data.lua`, `data-updates.lua`, `data-final-fixes.lua`,
   `prototypes/*.lua`, `settings.lua`).
2. Для каждого типа открыта страница прототипа в lua-api 2.1.17 и сверено
   КАЖДОЕ поле, которое мод задаёт, с документацией.
3. Каждое поле дополнительно сверено с ванильными данными (тот же паттерн,
   что у Wube).
4. Все deepcopy-сущности сверены с ванильными прототипами-донорами
   (offshore-pump, lightning-collector, foundry, electromagnetic-plant,
   steam-turbine, lightning, sand-3/dry-dirt/water/deepwater).
5. Результат закреплён в `tools/check_lua.py` → `check_prototype_fields()`
   (автоматическая проверка всех полей всех прототипов при каждом прогоне).

## 1. Типы прототипов, используемые модом (полный список)

Все типы ниже присутствуют в официальном индексе 2.1.17. По каждому типу:
страница доков, поля, которые задаёт мод, вердикт.

### Прототипы, определяемые модом с нуля

| Тип (док) | Файл мода | Поля мода | Вердикт |
|---|---|---|---|
| `item` (ItemPrototype) | items.lua | type, name, icon, icon_size, subgroup, order, stack_size, weight, durability, durability_description_key, durability_description_value, place_result | ✅ все поля документированы |
| `fluid` (FluidPrototype) | fluids.lua | type, name, icon, icon_size, default_temperature, max_temperature, heat_capacity, base_color, flow_color, pressure_to_speed_ratio, flow_to_energy_ratio, gas_temperature | ✅ все поля документированы |
| `recipe` (RecipePrototype) | recipes.lua | type, name, ingredients, results, energy_required, enabled, categories, allow_productivity | ✅ `categories` — поле 2.x (проверка `check_recipe_categories`); `ingredients`/`results` — IngredientPrototype/ProductPrototype |
| `recipe-category` (RecipeCategory) | recipe-categories.lua | type, name | ✅ «No new properties» |
| `technology` (TechnologyPrototype) | technologies.lua | type, name, icon, icon_size, order, prerequisites, unit, effects, research_trigger | ✅ unit=TechnologyUnit, research_trigger=TechnologyTrigger(`craft-item`), effects=Modifier(`unlock-recipe`, `character-crafting-speed`, `change-recipe-productivity`) |
| `item-group` (ItemGroup) | item-group.lua | type, name, order, icon, icon_size | ✅ |
| `item-subgroup` (ItemSubGroup) | item-group.lua | type, name, group, order | ✅ group — единственное собственное поле |
| `autoplace-control` (AutoplaceControl) | autoplace-controls.lua | type, name, order, category, richness | ✅ (поле `resource_category` — НЕ существует: **удалено**, см. §4) |
| `resource` (ResourceEntityPrototype) | resources.lua | type, name, icon, icon_size, flags, order, tree_removal_probability, tree_removal_max_distance, minable, category, subgroup, walking_sound, collision_box, selection_box, autoplace, stage_counts, stages, map_color, mining_visualisation_tint | ✅ все поля есть в доке и в ванили (`base/prototypes/entity/resources.lua`) |
| `simple-entity` (SimpleEntityPrototype) | decoratives.lua | type, name, icon, icon_size, flags, minable, max_health, collision_box, collision_mask, selection_box, render_layer, autoplace, picture/animations, random_animation_offset | ✅ все поля подтверждены докой 2.1.17 |
| `sound` (SoundPrototype) | sounds.lua | type, name, category, audible_distance_modifier, allow_random_repeat, variations | ✅ подтверждён докой; `variations` = SoundDefinition (filename/volume) |
| `planet` (PlanetPrototype) | planet.lua | см. §2 | ✅ все поля подтверждены (наследование SpaceLocationPrototype) |
| `space-connection` (SpaceConnectionPrototype) | planet.lua | type, name, subgroup, from, to, order, length, asteroid_spawn_definitions | ✅ |
| `noise-expression` (NamedNoiseExpression) | map-gen.lua | type, name, expression, local_expressions | ✅ |
| `noise-function` (NamedNoiseFunction) | map-gen.lua | type, name, parameters, expression | ✅ |
| `int-setting` / `bool-setting` (мод-настройки, официальная вики) | settings.lua | type, name, setting_type, default_value, minimum_value, maximum_value, order | ✅ по Tutorial:Mod_settings (страницы прототипа в lua-api нет — настройки определяются на settings-стадии) |
| `build-entity-achievement` (BuildEntityAchievementPrototype) | achievements.lua | type, name, order, to_build, amount, icon, icon_size | ✅ `to_build` обязателен (проверка `check_achievements`) |
| `produce-achievement` (ProduceAchievementPrototype) | achievements.lua | type, name, order, item_product, amount, limited_to_one_game, icon, icon_size | ✅ `item_product`/`amount` обязательны; `limited_to_one_game` — ОБЯЗАТЕЛЬНОЕ поле (без него движок падает «Key not found»; найдено в 0.2.1, см. §4) |
| `produce-per-hour-achievement` (ProducePerHourAchievementPrototype) | achievements.lua | type, name, order, item_product, amount, icon, icon_size | ✅ |
| `research-with-science-pack-achievement` (ResearchWithSciencePackAchievementPrototype) | achievements.lua | type, name, order, science_pack, icon, icon_size | ✅ `science_pack` обязателен |
| `change-surface-achievement` (ChangedSurfaceAchievementPrototype) | achievements.lua | type, name, order, surface, icon, icon_size | ✅ `surface` подтверждён |

### Deepcopy-сущности (доноры проверены в ванили)

| Сущность мода | Донор (ваниль) | Поля, которые мод перезаписывает | Вердикт |
|---|---|---|---|
| `condensate-extractor` | `offshore-pump` (base) | name, icon, minable, fast_replaceable_group, fluid_box.filter, dying_explosion, surface_conditions=nil | ✅ **удалено** несуществующее поле `fluid` (см. §4); `fluid_box.filter` — документированное поле FluidBox |
| `storm-siphon` | `lightning-collector` (space-age, `lightning-attractor`) | name, icon, minable, fast_replaceable_group, energy_source.buffer_capacity="2GJ", surface_conditions=nil | ✅ buffer_capacity — поле ElectricEnergySource (ваниль: 1000MJ) |
| `storm-foundry` | `foundry` (space-age) | name, icon, minable, fast_replaceable_group, crafting_categories, crafting_speed, energy_usage, surface_conditions=nil | ✅ все поля — документированные поля CraftingMachinePrototype |
| `storm-fabricator` | `electromagnetic-plant` (space-age) | name, icon, minable, fast_replaceable_group, crafting_categories, surface_conditions=nil | ✅ |
| `storm-generator` | `steam-turbine` (base) | name, icon, minable, fast_replaceable_group, maximum_temperature, fluid_usage_per_tick, fluid_box.filter, surface_conditions=nil | ✅ maximum_temperature/fluid_usage_per_tick — поля GeneratorPrototype |
| `cataclysm-lightning` | `lightning` (space-age) | name, damage, energy, graphics_set.shader_configuration (цвета), graphics_set.light.color | ✅ подробно в docs/LIGHTNING.md |
| тайлы 4 шт. | `sand-3`, `dry-dirt`, `water`, `deepwater` | name, order, autoplace, map_color, effect_color, walking_sound, driving_sound, fluid | ✅ effect_color/fluid/autoplace/walking_sound/driving_sound — документированные поля TilePrototype |

## 2. PlanetPrototype — все поля (проверено по 2.1.17)

Мод задаёт: icon, icon_size, starmap_icon, starmap_icon_size, gravity_pull,
distance, orientation, magnitude, label_orientation, order, subgroup,
map_gen_settings, pollutant_type, solar_power_in_space, platform_procession_set,
planet_procession_set, surface_properties, lightning_properties,
asteroid_spawn_influence, asteroid_spawn_definitions, persistent_ambient_sounds.

- `icon/icon_size/starmap_icon/starmap_icon_size` — SpaceLocationPrototype ✅
- `gravity_pull/distance/orientation/magnitude/label_orientation/solar_power_in_space/asteroid_spawn_influence` — SpaceLocationPrototype ✅
- `platform_procession_set/planet_procession_set` — SpaceLocationPrototype (ProcessionSet) ✅
- `map_gen_settings` — PlanetPrototypeMapGenSettings ✅
- `surface_properties` — dictionary SurfacePropertyID→double ✅ (ключи `day-night-cycle`, `magnetic-field`, `solar-power`, `pressure`, `gravity` — как у ванильного Aquilo)
- `lightning_properties` — LightningProperties ✅ (см. §3)
- `persistent_ambient_sounds` — PersistentWorldAmbientSoundsDefinition ✅ (структура совпадает с ванильными планетами: base_ambience/wind/crossfade/semi_persistent)
- `pollutant_type` — AirbornePollutantID, optional ✅ (nil = без загрязнений)

## 3. LightningProperties — все поля (проверено по 2.1.17)

| Поле мода | Значение | В доке | Диапазоны/ограничения |
|---|---|---|---|
| `lightnings_per_chunk_per_tick` | `1/(60*5)` (2× Фулгоры `1/(60*10)`) | ✅ обязательное | double |
| `search_radius` | `12.0` (Фулгора 10.0) | ✅ обязательное | double |
| `lightning_types` | `{"cataclysm-lightning"}` | ✅ обязательное | непустой массив EntityID |
| `priority_rules` | 11 правил (id/prototype/impact-soundset) | ✅ optional | LightningPriorityRule {type, string, priority_bonus} |
| `exemption_rules` | 24 правила (рельсы, стены, деревья и т.д.) | ✅ optional | LightningRuleBase {type, string} |
| `lightning_multiplier_at_day` | `0.25` | ✅ optional | [0,1] ✅ |
| `lightning_multiplier_at_night` | `1.0` | ✅ optional | [0,1] ✅ |

Структура правил идентична ванильной Фулгоре (`space-age/prototypes/planet/planet.lua`).

## 4. Найденные и исправленные дефекты

1. **`resource_category = "basic-solid"` в `prototypes/autoplace-controls.lua`** —
   поля НЕТ в AutoplaceControl (2.1.17: только category/richness/can_be_disabled/
   related_to_fight_achievements) и нет ни в одной ванильной autoplace-control.
   Игра молча игнорировала поле. **Удалено.** Теперь ловится статической
   проверкой `check_prototype_fields` (проверено: возврат поля → FAIL).
2. **`e.fluid = "cataclysm-storm-condensate"` в `prototypes/entities.lua`** —
   поля `fluid` НЕТ у OffshorePumpPrototype (2.1.17: fluid_box/pumping_speed/
   fluid_source_offset/graphics_set/energy_source/energy_usage/...). В 2.x
   офшорный насос берёт жидкость из тайла, на котором стоит
   (тайл `cataclysm-lake`/`-deep` имеет `fluid = "cataclysm-storm-condensate"`).
   **Удалено**, оставлен корректный `fluid_box.filter` (документированное поле
   FluidBox). Игра молча игнорировала поле; поведение не изменилось, но теперь
   каждое поле соответствует документации.
3. **Отсутствовал обязательный `limited_to_one_game` у всех
   `produce-achievement`** — ProduceAchievementPrototype (2.1.17) требует это
   поле (в доках оно без маркера «optional»; ваниль всегда задаёт его, чаще
   `false`). Без него игра не грузит мод: «Key "limited_to_one_game" not found
   in property tree at ROOT.produce-achievement...». **Добавлено
   `limited_to_one_game = true`** во все 7 produce-achievements (4 scripted +
   first-plate + charged-10k + deplete-stormite). У
   `produce-per-hour-achievement` этого поля НЕТ (проверено докой и ванилью),
   туда оно не добавлено. Проверка `check_achievements` теперь требует его у
   produce-achievement и запрещает у produce-per-hour-achievement
   (break-test пройден).
4. **`cataclysmic-science-pack` был `type = "tool"` с nil-копиями полей** —
   в Factorio 2.x science pack — это `type = "item"` (в 1.1 был "tool" с
   `durability`). Мод копировал `science.durability` и т.д. из
   `data.raw.item["automation-science-pack"]`, где этих полей нет → nil →
   ключ не попадает в property tree → ToolPrototype требует `durability`:
   «Key "durability" not found in property tree at ROOT.tool...». **Исправлено**:
   тип изменён на `item`, durability-поля удалены, паттерн = ванильный science
   pack 2.x (включая `localised_description`). Урок: копирование поля из
   ванильного прототипа, у которого его нет, даёт nil и молча роняет ключ —
   добавлена проверка REQUIRED-полей (см. §6).

Других расхождений не найдено: 85 прототипов мода прошли пословную сверку
полей + проверку обязательных полей.

## 5. Types и Defines, используемые модом (сверено)

- **Types**: LightningProperties, LightningGraphicsSet (shader_configuration,
  light, bolt_*, cloud_background, explosion, ground_streamers),
  LightningShaderConfiguration {color, distortion, thickness, power},
  LightningPriorityRule, LightningRuleBase, FluidBox (filter, volume,
  pipe_connections, production_type), AutoplaceSpecification
  (probability_expression, richness_expression, order, control),
  TechnologyUnit {count, ingredients, time}, TechnologyTrigger (`craft-item`
  {type, item, amount}), Modifier (`unlock-recipe` {type, recipe},
  `character-crafting-speed` {type, modifier}, `change-recipe-productivity`
  {type, recipe, change}), Sound/SoundDefinition, ProcessionSet,
  PersistentWorldAmbientSoundsDefinition, PlanetPrototypeMapGenSettings
  (property_expression_names, autoplace_controls, autoplace_settings),
  SurfacePropertyID, Color, Energy, Vector, DamageParameters.
- **Defines**: `defines.direction.south` (не используется модом в data —
  только в ванили-доноре), runtime-константы в control.lua
  (defines.events.*, defines.inventory.chest и т.д.) — вне прототипов.

## 6. Автоматизация (tools/check_lua.py)

Добавлена 8-я проверка `check_prototype_fields()`:
- AST-обход `data:extend({...})` во всех .lua файлах мода;
- для каждого прототипа с известным типом сверка ВСЕХ верхнеуровневых полей
  с allowlist-ом, построенным по официальной документации 2.1.17
  (таблица `PROTO_FIELDS` в начале функции);
- deepcopy-блоки (entities.lua, tiles.lua, lightning.lua) проверяются
  отчётом §1/§4, т.к. статически не видны — доноры верифицированы по ванили.

Прогон: `python3 tools/check_lua.py` → `OK prototype fields checked: 85` →
`ALL CHECKS PASSED`.

Помимо allowlist-ов, проверка теперь включает **REQUIRED_FIELDS** (обязательные
поля каждого типа — в доках они без маркера «optional») и **OR_REQUIRED_FIELDS**
(хотя бы одно из списка: у technology — `unit` или `research_trigger`; у
simple-entity — хотя бы одна графика). Оба краша 0.2.1/0.2.2 были пропущены
именно из-за отсутствия этой проверки; теперь они ловятся (break-test пройден).

## 7. Что делать при следующем релизе

1. Прогнать `python3 tools/check_lua.py` (8 проверок) и
   `python3 tools/make_release.py --check`.
2. При добавлении нового прототипа — сверить каждое поле с
   lua-api.factorio.com/latest (страница типа) и ванильным аналогом;
   новые поля дописать в `PROTO_FIELDS` (или проверка не покроет их).
3. Deepcopy-сущности: проверить перезаписываемые поля по доку донорского типа.

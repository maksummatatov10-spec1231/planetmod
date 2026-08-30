# ЭТАП 1 — ИССЛЕДОВАТЕЛЬСКАЯ СВОДКА (2026-08-30)

Цель: собрать и проверить все факты, необходимые для planet-мода под Factorio 2.1.17 (Space Age),
прежде чем проектировать планету КАТАКЛИЗМ. Каждый факт ниже подтверждён первоисточником.

---

## 1. Статус игры и версии

| Факт | Подтверждение |
|---|---|
| Актуальная версия игры: **2.1.17**, релиз 26.08.2026 | wiki.factorio.com/Version_history/2.1.0; форум «Version 2.1.17» |
| Официальная документация API (`lua-api.factorio.com/latest`) соответствует **ровно 2.1.17** | шапка страниц docs |
| **2.1 — финальное большое обновление Factorio**; дальше только long-term support и поддержка модов | FFF#440, cybrancee.com/blog/factorio-2-1 |
| Это идеальный момент для нового planet-мода: API стабилизирован на годы | вывод |

## 2. Официальные источники (проверено)

- `lua-api.factorio.com/latest/` — Prototype / Runtime / Auxiliary docs, версия 2.1.17.
- `wube/factorio-data` (master, собран для **2.1.15**, последний коммит 24.08.2026) — эталонные
  определения всех ванильных прототипов, включая планеты и соединения.
- `lua-api.factorio.com/latest/auxiliary/mod-structure.html` — структура мода, info.json, подпапки.
- `lua-api.factorio.com/latest/auxiliary/data-lifecycle.html` — стадии загрузки (settings → data →
  data-updates → data-final-fixes → control).
- `lua-api.factorio.com/latest/auxiliary/migrations.html` — миграции.
- wiki.factorio.com/Tutorial:Localisation — формат locale/*.cfg, категории, fallback на `en`.
- wiki.factorio.com/Planets — сравнительная таблица планет (день/ночь, магнитное поле, давление…).

## 3. Подтверждённые факты о прототипах (с примерами из factorio-data)

### 3.1 Планета (`type = "planet"`)
Поля (из ванильных `vulcanus`, `gleba`, `fulgora`, `aquilo`):
`icon`, `starmap_icon`, `starmap_icon_size = 512`, `gravity_pull`, `distance`, `orientation`,
`magnitude`, `label_orientation`, `order`, `subgroup = "planets"`, `map_gen_settings`,
`pollutant_type`, `solar_power_in_space`, `platform_procession_set`, `planet_procession_set`,
`procession_graphic_catalogue` (необязательно), `surface_properties`, `asteroid_spawn_influence`,
`asteroid_spawn_definitions`, `persistent_ambient_sounds`, `surface_render_parameters`,
`entities_require_heating` (Aquilo), `player_effects` + `ticks_between_player_effects` (снег/дождь),
`lightning_properties` (Fulgora).

`surface_properties` — словарь: `"day-night-cycle"` (в тиках), `"magnetic-field"`,
`"solar-power"`, `"robot-energy-usage"`, `pressure`, `gravity`.

Пример Aquilo: `distance = 35, orientation = 0.225, magnitude = 1.0, solar_power_in_space = 60`,
`day-night-cycle = 20*minute`, `entities_require_heating = true`.

### 3.2 Молнии (движок!)
`PlanetPrototype.lightning_properties` — встроенная система (не скрипт!):
- `lightnings_per_chunk_per_tick` (у Фулгоры `1/(60*10)` — ~раз в 10 сек на чанк);
- `search_radius`, `lightning_types` (имена `lightning`-сущностей), `lightning_multiplier_at_day/night`,
  `multiplier_surface_property`, `lightning_warning_icon`;
- `priority_rules` — куда бьёт молния: `lightning-collector` +10000, `lightning-attractor` +1000,
  трубы/насосы +1, столбы +10, роботы +100 и т.д.;
- `exemption_rules` — что молния НЕ бьёт (рельсы, стены, деревья, cargo-pod…).

`LightningPrototype` (`type = "lightning"`, space-age): `graphics_set`, `sound`,
`strike_effect`, `attractor_hit_effect`, `source_offset/variance`, `damage` (DamageParameters),
`energy` (передаётся в `lightning-attractor`), `time_to_damage`, `effect_duration`.
Можно объявлять **свою** молнию (свой визуал/урон) и свои attractor-правила.

Вывод: уникальный «грозовой» риск планеты реализуется штатными средствами — это не выдумка API.

### 3.3 Космические соединения (`type = "space-connection"`)
Формат (файл `space-age/prototypes/planet/planet.lua`, в конце):
```lua
{ type = "space-connection", name = "aquilo-solar-system-edge",
  subgroup = "planet-connections", from = "aquilo", to = "solar-system-edge",
  order = "h", length = 100000,
  asteroid_spawn_definitions = asteroid_util.spawn_definitions(asteroid_util.aquilo_solar_system_edge) }
```
Длины ванили: Nauvis→внутренние планеты 15000; →Aquilo 30000; Aquilo→край системы 100000;
край→Shattered Planet **4000000**. Соединения неориентированные (летать можно в обе стороны).
«Дальний путь» = большая `length` + плотные `asteroid_spawn_definitions`.

### 3.4 Map-gen планет
- `map_gen_settings` собирается функцией (см. `planet-map-gen.lua`): ключи
  `property_expression_names` (elevation/temperature/moisture/aux/cliffiness + per-entity
  `["entity:x:probability"]`, `["entity:x:richness"]`), `cliff_settings`, `territory_settings`,
  `autoplace_controls`, `autoplace_settings = { tile = {...}, decorative = {...}, entity = {...} }`.
- Тайлы/руды раскладываются noise-выражениями (`noise-expression`/`noise-function`), включая
  `starting_spot_at_angle` для стартовых залежей (см. `planet-aquilo-map-gen.lua`).
- Поверхность планеты создаётся лениво: при первом прибытии платформы/падении груза;
  в редакторе — кнопка «Generate planets» или `/cheat <planet>`.

### 3.5 Science pack (новая наука)
- Научные пакеты в 2.x — предметы `type = "tool"` (durability от `automation-science-pack`;
  `stack_size = 200`, `weight`). Эталон: `hydraulic-science-pack` из Maraxsis.
- Рецепт пакета: `type = "recipe"`, `category` — кастомная категория новой машины,
  `allow_productivity = true`, ингредиенты с `{type = "item"|"fluid", name, amount}`,
  температура жидкости `temperature = N` — поддерживается.
- **Обязательный шаг совместимости**: в `data-final-fixes.lua` добавить новый пакет в
  `data.raw.lab.*.inputs` (паттерн Maraxsis: найти лаборатории, принимающие
  `cryogenic-science-pack`, и вставить свой). Без этого лаборатории не примут пакет.
- Технологии: `unit = { count, ingredients = {{"pack-name", 1}, ...}, time }`;
  `research_trigger` — альтернатива (craft-item и т.п.).

### 3.6 Достижения
Подтверждённые типы (примеры из `space-age/prototypes/achievements.lua` и Maraxsis):
- `change-surface-achievement` — `surface = "cataclysm"` («посетить планету»);
- `research-with-science-pack-achievement` — `science_pack = "cataclysmic-science-pack"`;
- `space-connection-distance-traveled-achievement` — `tracked_connection`, `distance`, `reversed`;
- `produce-achievement`, `produce-per-hour-achievement`, `build-entity-achievement`,
  `deplete-resource-achievement`, `research-achievement`, `kill-achievement`,
  `complete-objective-achievement` (objective_condition = "game-finished", `within`),
  `dont-*` (missable).
- Скриптовые условия: `player.unlock_achievement(name)` в control-стадии (подтверждено сообществом;
  Steam-достижения недоступны модам — только внутриигровые; достижения сохраняются в
  achievements-modded.dat).
- Иконки 128×128 (`icon_size = 128`), `order` в стиле ванили (`a[progress]-g[visit-planet]-...`).

### 3.7 События и рантайм
- `defines.events.on_surface_created` — есть; `game.planets`/`LuaPlanet` — есть
  (включая `game.planets[name].create_surface()` — но для планет с прототипом поверхность создаётся
  движком автоматически при первом прибытии).
- `script.on_init`, `script.on_load`, `script.on_configuration_changed` — стандарт.

### 3.8 Локализация
- `locale/{en,ru,de}/…cfg`; категории `[item-name]`, `[item-description]`, `[fluid-name]`,
  `[recipe-name]`, `[technology-name]`, `[technology-description]`, `[achievement-name]`,
  `[achievement-description]`, `[entity-name]`, `[entity-description]`, `[mod-name]` и др.
- Параметры `__1__`, плюрализация, rich text; отсутствие перевода → fallback на `en`.

### 3.9 info.json / структура
- `factorio_version: "2.1"`, зависимости: `base >= 2.1.0`, `space-age >= 2.1.0`;
  опциональные: `? mod`; необязательные с условием `(?) mod`.
- Флаги для портала: `space_travel_required`, `quality_required`, `spoiling_required` и т.п.
- Папки: `locale/`, `migrations/`, `prototypes/`, `graphics/`, `sounds/`, `compat/`;
  файлы: `info.json`, `settings.lua`, `data.lua`, `data-updates.lua`, `data-final-fixes.lua`,
  `control.lua`, `changelog.txt`, `thumbnail.png`.

## 4. Анализ референсных planet-модов

### Maraxsis (эталон архитектуры и «честного» planet-мода)
- Репозиторий: `github.com/notnotmelon/maraxsis`; 1930 коммитов; активен (последний — 12.08.2026,
  поднятие требования base до 2.1.14); лицензия MIT.
- Структура: `prototypes/{achievements,circuit-connector-definitions,collision-mask,custom-input,
  entity/,equipment/,fluid/,item/,mod-data/,music,planet/,recipe/,swimming,technology/,tile/,
  tips-and-tricks,vanilla-changes}.lua` + `compat/`, `graphics/`, `lib/`, `locale/`, `migrations/`,
  `scripts/`, `sounds/`.
- Механики, которые стоит взять как ПАТТЕРНЫ (не копируя):
  1. **Прогрессия**: планета открыта на уровне Aquilo, мод можно добавить в готовое сохранение —
     не меняет ванильные рецепты (кроме аккуратных дополнений через `vanilla-changes.lua`).
  2. **Свой science pack** подключается к лабораториям через `data.raw.lab.*.inputs`.
  3. **Стартовая точка**: техн. дерево планеты начинается `research_trigger`-ом
     (скрафтил сигнатурный предмет → открылась наука), без ломания прогрессии.
  4. Кастомная машина со своей `recipe-category` (гидро-завод).
  5. `tips-and-tricks.lua` — онбординг планеты.
  6. Аккуратная совместимость: патч `tile_collision_mask` для проектайлов и т.п.
- Чего у Maraxsis нет (наш шанс): полноценного набора достижений (у них 2), 3 языков локализации
  (EN-only), скриптовых природных событий уровня «супершторм».

### Ванильные планеты — «что брать»
| Планета | Сильная идея | Что НЕ копируем |
|---|---|---|
| Vulcanus | Сырьё→плавка→плиты; территориальные враги; богатая энергия | саму лаву/литьё |
| Fulgora | Движковые молнии + priority/exemption rules; «нет воды» | мусорно-утилизационную петлю |
| Gleba | Биологическая петля, у которой есть цена | спойлинг (таймерная порча) |
| Aquilo | Поздняя планета-вершина: нагрев, криогеника; планета как «ворота» в эндгейм | нагрев как таковой |
| Shattered Planet | Дальний путь (length=4e6), fly_condition | — |

## 5. Полезные паттерны (итог)
1. Поздняя планета = `space-connection` **только от Aquilo** + `length` заметно больше 30000 +
   плотные астероиды. Мягкий гейт (как в ванили) + жёсткий гейт наукой: все технологии Катаклизма
   требуют `cryogenic-science-pack` в `unit.ingredients`.
2. Уникальный риск — штатная `lightning_properties` (движок) + скриптовые «суперштормы» как
   надстройка (спавн дополнительных молний через `surface.create_entity`; fallback — без них).
3. Уникальная петля — не спойлинг и не тепло: **электролитный цикл заряда** (жидкость-энергоноситель).
4. Наука-гейт: `research_trigger` или классический `unit.ingredients`; пакет — `type = "tool"`.
5. Совместимость: `data-final-fixes.lua` для lab.inputs; `?`-зависимости; миграции на будущее.
6. Ачивки: прототипные где можно + скриптовый `unlock_achievement` где нельзя; иконки 128px.
7. Локализация: минимум en/ru/de с fallback на en; короткие факторио-стильные описания.

## 6. Опасные паттерны (чего избегать)
1. Прямое копирование механик других планет («ещё одна мусорная планета»).
2. Изменение ванильных рецептов в `data.lua` (ломает добавление в существующее сохранение) —
   только `data-final-fixes` и только аддитивно (паттерн Maraxsis).
3. Ссылки на графику без зависимости (пути `__space-age__/...` разрешены только при зависимости
   от space-age — она у нас обязательная).
4. Скрипт на каждый тик без интервалов (производительность): супершторм — по таймеру/событиям.
5. Переопределение `map_gen_settings` существующих планет.
6. Требование недоступных ассетов: LUT-текстуры дня/ночи — опциональны (без них работает
   дефолтный грейдинг) → fallback.
7. Steam-достижения: модам недоступны — только внутриигровые (не обещать Steam).

## 7. Неизвестные / требующие проверки при реализации (спорные места)
1. Можно ли штатно спавнить `lightning`-сущность через `surface.create_entity{name="lightning"}` —
   проверить на бинарнике; fallback: эмиссия урона + `create-trivial-smoke`/`beam` + звук.
2. Runtime-изменение частоты молний (через `multiplier_surface_property`) — вероятно, нельзя
   менять свойства поверхности на лету; superstorm делаем скриптом (см. п.1).
3. Поддержка `tint` у картинок деревьев/декоративов — проверить; fallback: свои `simple-entity`
   скалы/кристаллы с tinted pictures + ванильные деревья как есть.
4. `territory_settings` (демолишеры) — не используем в V1 (нет уникальных врагов), но зарезервировано.
5. Точные значения `asteroid_spawn_definitions` для нового маршрута — переиспользуем
   `asteroid_util.spawn_definitions(asteroid_util.aquilo_solar_system_edge, x)`-подобные наборы,
   собственные веса зададим после проверки на бинарнике.
6. `procession`-каталоги для новой планеты — в V1 используем ванильные procession-наборы
   (`platform-to-planet-b` и т.д.), кастомные — позже (полировка).

## 8. Рекомендуемая архитектура (резюме)
- Модульная структура по образцу Maraxsis (prototypes/ по доменам), отдельные docs/, compat/,
  migrations/, locale/{en,ru,de}, graphics/ (сгенерированные процедурно иконки + fallback-спрайты).
- Жёсткие зависимости: `base >= 2.1.0`, `space-age >= 2.1.0`. Опциональные: quality, PlanetsLib.
- Код: data.lua (новые прототипы) + data-final-fixes.lua (лаборатории, аддитивные патчи) +
  control.lua (суперштормы, скриптовые ачивки, on_surface_created).
- Версионирование: semantic versioning + changelog.txt + миграции при изменении прототипов.
- Тестирование: статические проверки Lua-синтаксиса, валидация JSON, генерация иконок с
  проверкой размеров; ручной QA-скрипт (в песочнице нет бинарника игры — документируем шаги).

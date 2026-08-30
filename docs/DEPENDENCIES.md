# Dependency study (stage 5.1)

Итог тотального изучения модов-библиотек, которые могут использоваться планетными модами
для Factorio 2.1 / Space Age, и решения по интеграции для Cataclysm.

## 1. PlanetsLib (danielmartin0/PlanetsLib, авторы thesixthroc, MeteorSwarm)

Библиотека для создания планет/лун: API поверх `data:extend`, орбитальное дерево,
графика орбит, музыка, cargo-drop технологии, surface-conditions хелперы и т.д.
Зависимости самой библиотеки: только `base >= 2.1.13`; space-age/quality/recycler — опциональны.

Изученный API (api.lua / lib/planet.lua / control.lua):

| Функция | Что делает | Используем? |
|---|---|---|
| `PlanetsLib:extend(config)` | определяет планету через орбиту родителя (позиция родителя + смещение) | нет — наша планета определена в собственном data.lua |
| `PlanetsLib:update(config)` | регистрирует уже существующую планету в орбитальном дереве, пересчитывает позицию относительно родителя, двигает «детей» | **да**, в data-updates.lua (родитель = Aquilo) |
| `PlanetsLib.borrow_music(src, dst)` | 2.1: добавляет имя планеты в `planets` у треков родителя (без копирования) | **да** (Aquilo → Cataclysm), guarded + pcall |
| `PlanetsLib.set_default_import_location(item, planet)` | задаёт планету по умолчанию в GUI импорта платформы | **да**, для всех 11 наших предметов |
| `add_science_packs_from_vanilla_lab_to_technology` | зеркалит science packs в биолаб | нет — мы сами добавляем пак в лабы в vanilla-changes.lua (независимо от PlanetsLib) |
| `visit_planet_achievement` | генерирует change-surface-achievement | нет — своя ачивка уже есть |
| `cargo_drops_technology_base` | ограничение сброса грузов до исследования | нет (future; в V1 сброс грузов не ограничен) |
| `restrict/relax/remove_surface_condition` | правка surface-conditions совместимым образом | нет (в V1 не нужны) |
| `create_planet_entity_variant` / `assign_entity_replacement` | планетные варианты сущностей | нет (это для «на Вулканусе X превращается в Y») |
| `get_orbit_sprite(radius)` | спрайт орбиты для starmap | нет (future, визуальный полиш) |
| `set_special_properties` / tier-метаданные | не-surface свойства планет (rocket_part_multiplier и т.п.) | нет |

Решение: **опциональная зависимость** (`? PlanetsLib` в info.json; без неё мод полностью
работает). Интеграция — строго в data-updates.lua, вся обёрнута в `type()`-guard'ы и pcall.
Сделать её жёсткой (как у Maraxsis) не стали: наш мод не требует ни одного API PlanetsLib
для собственной работы, а критерий приёмки — стабильность и совместимость.

## 2. flib (raiguard; codeberg.org/raiguard/flib, v0.17.x)

Набор runtime-утилит: `event` (регистрация обработчиков, композитные события),
`migration`, `gui`/`gui-templates`/`style`, `table`/`array`/`math`/`util`/`format`,
`dictionary`, `train`, `position`, `bounding-box`, `direction`, `data-util`, `data`,
`prototypes` (технологии).

Оценка для Cataclysm:

- `flib.event` — удобная обёртка, но ванильные `script.on_event`/`script.on_nth_tick`
  сами переживают save/load (регистрации автоматически восстанавливаются), а сложных
  композитных событий у нас нет.
- `flib.migration` — нужен при сложных миграциях storage между версиями. У нас storage
  минимален (`storage.cataclysm`), версия 0.2.2, миграций пока нет.
- `flib.gui` — у нас нет пользовательских GUI.
- `flib.table`/`util` — мелочи, ради которых не тянут зависимость.

Решение: **не зависеть**. Добавлять `? flib` без использования — лишний шум в зависимостях.
Повторно пересмотреть, если появятся GUI или версионирование storage (тогда — `? flib` +
`flib.migration`).

## 3. Stdlib (Afforess/Factorio-Stdlib)

Классика 0.16–1.1; для 2.0 не обновлялся самим автором — сообщество сделало форки
(`kry_stdlib`, `jalm`). В 2026 для новых модов предпочтителен flib (см. выше) или
вообще ванильный API. Решение: не использовать.

## 4. PlanetsLibTiers (thesixthroc)

Компаньон PlanetsLib: присваивает планетам «тиры» (порядок сложности) для других модов.
Мы ничего не потребляем: наш тир задан дизайном (пост-Aquilo). Никаких действий не требуется.

## 5. Прочие библиотеки (обзор)

- `um-standalone-space-age-lib` — правки категорий рецептов под SA; не нужно.
- `Miscellaneous`, `FactorioModdingToolkit` — инструменты разработки, не зависимости.
- Встроенный lualib базы: `util`, `lib`, `resource-autoplace`, `table.*` — уже используем
  паттерны (`util.by_pixel`, `table.find`, `table.deepcopy`).

## 6. Отслеживание событий (runtime)

Варианты: ванильные `script.on_event` / `script.on_nth_tick` (используем),
`flib.event` (обёртка), `PlanetsLib.events` (свои кастомные события для потребителей).
Для нашего масштаба (супершторм-таймер, ачивки, проверка шпилей — 2 nth_tick + 1 событие)
ванильного API достаточно и оно гарантированно стабильно.

## Итог

- `info.json`: `? PlanetsLib` остаётся опциональной; новых зависимостей не добавляем.
- `data-updates.lua`: PlanetsLib-интеграция (update + borrow_music + import defaults),
  полностью guarded.
- `control.lua`: без изменений — ванильный API.
- Документация этого анализа: `docs/DEPENDENCIES.md` (этот файл).

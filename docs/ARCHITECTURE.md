# ЭТАП 3 — АРХИТЕКТУРА МОДА «CATACLYSM»

## 1. Репозиторий и структура папок

```
planetmod/
├── info.json                  # метаданные мода (cataclysm 0.2.1, 2.1)
├── data.lua                   # новые прототипы (точка входа data-стадии)
├── data-updates.lua           # аккуратные правки чужих прототипов (сейчас пусто)
├── data-final-fixes.lua       # lab.inputs (science pack), аддитивные патчи
├── control.lua                # runtime: суперштормы, ачивки, on_surface_created
├── settings.lua               # startup-настройки (частота суперштормов и т.п.)
├── changelog.txt
├── thumbnail.png              # 144×144 (сгенерировать на этапе графики)
├── LICENSE.md                 # MIT
├── README.md
├── docs/                      # проектная документация (этот репозиторий)
│   ├── RESEARCH.md            # этап 1 — сводка
│   ├── DESIGN.md              # этап 2 — дизайн планеты
│   ├── ARCHITECTURE.md        # этот файл
│   ├── GRAPHICS.md            # этап 4 — план визуала
│   ├── TESTING.md             # этап 7 — план тестов
│   └── ROADMAP.md             # этапы реализации
├── prototypes/
│   ├── item-group.lua         # item-group "cataclysm" + subgroups
│   ├── autoplace-controls.lua # слайдеры генерации (штормит, астрит, озёра, вентили)
│   ├── items.lua              # руды, плиты, кристаллы, решётка, пакет, компоненты построек
│   ├── fluids.lua             # грозовой/заряженный конденсат
│   ├── recipes.lua            # все рецепты планеты
│   ├── recipe-categories.lua  # storm-smelting, storm-crafting, storm-charging
│   ├── entities/
│   │   ├── condensate-extractor.lua
│   │   ├── storm-siphon.lua
│   │   ├── storm-foundry.lua
│   │   ├── storm-fabricator.lua
│   │   └── storm-generator.lua
│   ├── resources.lua          # resource-прототипы (штормит, астрит) + autoplace
│   ├── decoratives.lua        # скалы, вентили, обломки, деревья-кристаллы
│   ├── tiles.lua              # тайлы планеты (грунт, озеро конденсата)
│   ├── technologies.lua       # дерево технологий
│   ├── achievements.lua       # достижения
│   ├── tips-and-tricks.lua    # онбординг
│   ├── planet.lua             # planet + space-connection + lightning_properties
│   ├── map-gen.lua            # noise-выражения и map_gen_settings
│   └── vanilla-changes.lua    # (вызывается из data-final-fixes.lua)
├── migrations/                # версионные миграции (с 0.2.0 при необходимости)
├── locale/
│   ├── en/cataclysm.cfg
│   ├── ru/cataclysm.cfg
│   └── de/cataclysm.cfg
├── graphics/                  # сгенерированные иконки/спрайты (см. GRAPHICS.md)
└── tools/                     # генераторы иконок, статические проверки
```

## 2. Подсистемы и их зоны ответственности

| Подсистема | Файлы | Комментарий |
|---|---|---|
| Planet definition | prototypes/planet.lua | прототип планеты, соединение, молнии, звуки |
| Resource generation | prototypes/map-gen.lua, autoplace-controls.lua, resources.lua | noise-выражения + property_expression_names |
| Recipes/items/fluids | prototypes/{items,fluids,recipes}.lua | вся экономика |
| Science pack | prototypes/items.lua + recipes.lua + data-final-fixes.lua | tool-предмет + lab.inputs |
| Technologies | prototypes/technologies.lua | дерево (таблица DESIGN.md §H) |
| Achievements | prototypes/achievements.lua + control.lua | прототипные + скриптовые |
| Events/UI | control.lua, prototypes/tips-and-tricks.lua | суперштормы, сообщения, онбординг |
| Localization | locale/{en,ru,de}/cataclysm.cfg | все ключи |
| Graphics | graphics/, tools/gen_icons.py | процедурные иконки, fallback-спрайты |
| Compatibility | data-updates.lua, data-final-fixes.lua, compat/ | lab.inputs; soft-dep патчи |
| Migrations | migrations/ | версии прототипов |
| Tests | tools/check_*.py, docs/TESTING.md | статика + ручной QA |

## 3. Зависимости

- **Hard:** `base >= 2.1.0`, `space-age >= 2.1.0` (мы используем lightning_properties,
  space-connection, cryogenic science, procession).
- **Optional:** `? quality` (ничего не требуем, но не ломаем), `? PlanetsLib` (если решим
  переиспользовать их map-gen утилиты — V1 без неё), `? space-exploration` (нейтрально).
- **Конфликты:** моды, переопределяющие планеты/соединения Aquilo (рейсы к Shattered Planet),
  моды, меняющие `data.raw.lab.*.inputs` глобально (мы добавляем аддитивно и сортируем, паттерн
  Maraxsis). Любые «полные оверхолы» (SE, K2) — не блокируем, документируем в README.
- **Порядок загрузки:** наши новые прототипы в `data.lua`; аддитивные правки чужих — в
  `data-final-fixes.lua` (после всех модов) — это безопасно и предсказуемо.

## 4. Версии и сохранения (save safety)

- Семантическое версионирование (версии чередуются по типу изменений):
  багфикс → patch (0.1.1, 0.1.2, …), новая фича → minor (0.2.0, 0.3.0, …).
  0.4.0 ачивки/локализация → 0.5.0 графика → 1.0.0 баланс/релиз.
- **Добавление мода в существующее сохранение:** мы не меняем ванильные прототипы разрушающе;
  планета создастся при первом прибытии платформы → save-safe (паттерн Maraxsis).
- **Обновление мода:** любые изменения прототипов между версиями → файл миграции
  `migrations/<дата>_<версия>.lua` (формат подтверждён в auxiliary docs).
- **Минорные изменения API 2.1.x:** таргет `factorio_version "2.1"`; фиксируем в README, на каких
  версиях протестировано (2.1.17).

## 5. Тестирование (резюме; детали в TESTING.md)

- Статические: Lua-синтаксис (luacheck/lua-parse в CI), валидация JSON (info.json), проверка
  наличия всех locale-ключей (скрипт по списку прототипов), проверка размеров иконок.
- Логика: юнит-подобные проверки баланса (Python: подсчёт длин цепочек, стоимости),
  скриптовые «симуляции» отсутствуют без бинарника — ручной QA-скрипт.
- Ручной QA (на бинарнике 2.1.17): заход на планету, петля, ачивки, супершторм, сохранение/
  загрузка, добавление в готовое сохранение, совместимость с Maraxsis/SE.

## 6. Fallback-системы (резюме)

1. Супершторм → без скрипта: только движковые молнии (настраиваемая частота).
2. Кастомная молния → ванильная `lightning`.
3. Кастомные постройки → ванильные (lightning-collector, assembling-machine) + скрипт.
4. LUT-градиенты дня/ночи → дефолтный грейдинг (поле опционально).
5. Кастомные спрайты построек → tinted-версии ванильных спрайтов (проверить поддержку tint).
6. Если `create_entity("lightning")` не работает → урон + smoke/beam + звук.
7. Если нет бинарника для тестов → статическая валидация + чек-лист ручного QA.

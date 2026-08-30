# Молнии Катаклизма — полная спецификация

> Задача (запрос пользователя): «пусть молнии будут как на Фульгоре — точно
> такие же молнии, просто другого цвета (на них фильтр наложен), и они чаще
> и сильнее».
>
> Версия мода: 0.2.0. Дата: 2026-08-30.

## 1. Ванильная молния Фулгоры (эталон)

Официальные источники:
- Прототип: [LightningPrototype](https://lua-api.factorio.com/latest/prototypes/LightningPrototype.html) (`type = "lightning"`)
- Тип графики: [LightningGraphicsSet](https://lua-api.factorio.com/latest/types/LightningGraphicsSet.html)
- Тип свойств планеты: [LightningProperties](https://lua-api.factorio.com/latest/types/LightningProperties.html)
- Ванильные данные: `space-age/prototypes/entity/explosions.lua` (сущность `lightning`)
  и `space-age/prototypes/planet/planet.lua` (планета `fulgora`).

| Параметр | Значение Фулгоры |
|---|---|
| `damage` | `{amount = 100, type = "electric"}` |
| `energy` (передаётся аттрактору) | `"1000MJ"` |
| `time_to_damage` / `effect_duration` | `8` / `36` тиков |
| `source_offset` / `source_variance` | `{0, -25}` / `{30, 6}` |
| `sound` | `__space-age__/sound/explosions/lightning-effect-1..5.ogg`, `audible_distance_modifier = 2.25`, aggregation `max_count = 3` |
| `attracted_volume_modifier` | `0.4` |
| `created_effect` | camera-effect (тряска камеры, strength 0.75) |
| `strike_effect` | create-particle (искры/пыль) |
| `graphics_set.shader_configuration` | 6 слоёв, голубые цвета (см. ниже) |
| `graphics_set.light` | `{intensity = 5.0, size = 50, color = {0.1, 0.15, 1}}` |
| Частота ударов (планета) | `lightnings_per_chunk_per_tick = 1 / (60 * 10)` (раз в ~10 с на чанк) |
| `search_radius` | `10.0` |
| Приоритеты | lightning-collector +10000, lightning-attractor +1000, руины Фулгоры 95–91, `impact-soundset metal` +1 |
| Коллектор | buffer `1000MJ`, output `1000MJ`, drain `2.5MJ` (буфер = энергия удара 1:1) |

Ванильный shader_configuration (голубой — это и есть «фильтр» молнии, цвета слоёв шейдера):

```lua
{color = {0.0, 0.6, 1, 0.8}, distortion =  0.20, thickness = 0.20, power = 0.25},
{color = {0.0, 0.6, 1, 1.0}, distortion =  0.40, thickness = 1.00, power = 0.25},
{color = {0.2, 0.6, 1, 1.0}, distortion =  0.55, thickness = 1.00, power = 0.25},
{color = {0.7, 0.6, 1, 0.6}, distortion =  0.70, thickness = 0.75, power = 0.25},
{color = {0.4, 0.2, 1, 0.3}, distortion =  1.00, thickness = 0.50, power = 0.10},
{color = {0.0, 0.2, 1, 0.0}, distortion = 20.00, thickness = 0.50, power = 0.01}
```

## 2. Молния Катаклизма (`cataclysm-lightning`)

Файл: `prototypes/lightning.lua`. Сущность — **deep-copy ванильной `lightning`**:
**вся графика, анимация, звук, эффекты и тайминги идентичны Фулгоре** —
меняется ТОЛЬКО цвет (фильтр) и сила.

### 2.1. Что идентично Фулгоре (не тронуто deepcopy)

- `time_to_damage = 8`, `effect_duration = 36`
- `source_offset = {0, -25}`, `source_variance = {30, 6}`
- `sound` (lightning-effect 5 вариаций, aggregation, audible_distance_modifier)
- `attracted_volume_modifier = 0.4`
- `created_effect` (тряска камеры), `strike_effect` (частицы)
- `graphics_set`: параметры разряда (bolt_midpoint_variance, max_bolt_offset,
  fork_probability, streamers и т.д.), облако, взрыв, анимация попадания,
  наземные разряды — 1:1
- `light = {intensity = 5.0, size = 50}` (меняется только `color`)

### 2.2. Что изменено

| Параметр | Фулгора | Катаклизм | Комментарий |
|---|---|---|---|
| `damage` | 100 electric | **150 electric** | сильнее в 1.5× |
| `energy` | 1000MJ | **2GJ** | сильнее в 2×; передаётся сифону |
| `shader_configuration` цвета | голубые | **фиолетовые** (см. ниже) | тот же слой/дисторшн/толщина/мощность |
| `light.color` | `{0.1, 0.15, 1}` | **`{0.65, 0.35, 1}`** | фиолетовое свечение |

### 2.3. Цветовой фильтр Катаклизма (shader_configuration)

```lua
{color = {0.55, 0.25, 1, 0.8},  distortion =  0.20, thickness = 0.20, power = 0.25},
{color = {0.55, 0.25, 1, 1.0},  distortion =  0.40, thickness = 1.00, power = 0.25},
{color = {0.65, 0.30, 1, 1.0},  distortion =  0.55, thickness = 1.00, power = 0.25},
{color = {0.80, 0.45, 1, 0.6},  distortion =  0.70, thickness = 0.75, power = 0.25},
{color = {0.50, 0.20, 1, 0.3},  distortion =  1.00, thickness = 0.50, power = 0.10},
{color = {0.30, 0.10, 0.9, 0.0}, distortion = 20.00, thickness = 0.50, power = 0.01}
```

Как работает «фильтр»: `shader_configuration` — это 6 цветовых слоёв шейдера
разряда; каждый слой применяется поверх одного и того же белого разрядного
шаблона с разной дисторсией/толщиной/мощностью. Меняя только `color`
(и сохраняя distortion/thickness/power/alpha), мы получаем **ту же самую
молнию Фулгоры, но в фиолетовой палитре** — никакой другой графики не трогаем.

## 3. Частота и сила на планете (`planet.lua`)

```lua
lightning_properties = {
  lightnings_per_chunk_per_tick = 1 / (60 * 5),   -- 2× чаще Фулгоры (1/(60*10))
  search_radius = 12.0,
  lightning_types = { "cataclysm-lightning" },
  lightning_multiplier_at_day = 0.25,
  lightning_multiplier_at_night = 1.0,
  priority_rules = { ... },
  exemption_rules = { ... }
}
```

| Параметр | Фулгора | Катаклизм |
|---|---|---|
| Ударов на чанк | 1/600 тиков (раз в 10 с) | **1/300** (раз в 5 с) |
| Урон за удар | 100 | **150** |
| Энергия за удар | 1000MJ | **2GJ** |

Итог: Катаклизм получает в **2× больше** ударов, каждый в **1.5× сильнее**
по урону и **2×** по энергии — «чаще и сильнее», как запрошено.

## 4. Приоритеты целей (риск/награда)

Порядок приоритетов в `planet.lua` (выше число = чаще бьёт в такую цель):

| Цель | Приоритет | Зачем |
|---|---|---|
| `storm-siphon` (id) | +10000 | главный приёмник: заряжается молниями (риск/награда) |
| `storm-generator` (id) | +2000 | тоже принимает разряды |
| `cataclysm-vent` (id) | +90 | декорация-«громоотвод» |
| `electric-pole`, `power-switch`, `pipe`, `pump`, `offshore-pump` | +10 | инфраструктура под ударом |
| `logistic-robot`, `construction-robot` | +100 | роботов сбивает чаще |
| `impact-soundset metal` | +1 | фоновый звон |
| рельсы, стены, деревья, вагоны, мины, cargo-pod | исключены | `exemption_rules` (как у Фулгоры) |

## 5. Супершторм (скрипт, control.lua)

- Во время супершторма скрипт спавнит `cataclysm-lightning` напрямую
  (`surface.create_entity{name="cataclysm-lightning", ...}`) — те же усиленные
  молнии; fallback — ванильный `explosion`.
- Удары вокруг игроков: шанс 0.4 (0.2 после «Защиты от молний»), радиус 10–22
  (28–42 после «Сейсмостабилизации»).
- Дополнительные удары по сифонам каждые 30 тиков (до 6, шанс 0.5) — сифоны
  с буфером 2GJ поглощают удары и заряжают батарею.

## 6. Баланс и почему так

- **Больше/сильнее, но управляемо**: урон 150 electric — танковый экзоскелет
  (~100+ HP с модами) выдерживает, «Защита от молний» даёт шанс 0.2 вместо
  0.4, «Сейсмостабилизация» отводит удары от игрока.
- **Буфер сифона 2GJ = энергия удара 2GJ**: один удар полностью заряжает
  сифон (по аналогии с Фулгорой: 1GJ буфер ↔ 1GJ удар). Увеличен в
  `prototypes/entities.lua`.
- **Производительность**: 1 удар/чанк/5 с — на порядок ниже, чем в часы
  пик ванильных планетных бурь; скриптовые удары лимитированы
  (STRIKE_INTERVAL, SIPHON_STRIKE_LIMIT).

## 7. Проверки

- `LightningPrototype` — поля `damage`, `energy`, `graphics_set`, `light`,
  `sound`, `time_to_damage`, `effect_duration`, `source_offset`,
  `source_variance` подтверждены официальной документацией 2.1.17.
- `LightningProperties` (тип полей планеты) — подтверждён ванильными данными
  Фулгоры (те же имена полей).
- Статические проверки: `python3 tools/check_lua.py` (синтаксис, ссылки),
  `python3 tools/make_release.py --check` (сборка архива).
- Живая проверка в игре — за пользователем (docs/TESTING.md): визуал разряда,
  частота, урон по игроку, зарядка сифона.

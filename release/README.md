# Releases

Готовые к установке архивы мода. Файл вида `cataclysm_<version>.zip` положите
в папку `mods/` вашей установки Factorio (не распаковывая).

- `cataclysm_0.3.0.zip` — 0.3.0: планета наконец достижима — новая технология
  `cataclysm-planet-discovery` (эффект `unlock-space-location`; раньше планета
  навсегда оставалась закрытой даже после всех исследований). Новый научный пак
  `cataclysm-survey-pack` (НЕ криогенный; крафт до полёта на Aquilo/платформе,
  рецепт открывает ванильная `space-platform-thruster`) платится за открытие.
  Первичная переработка открывается триггерами добычи/создания (добыл руду →
  обработка, создал плавильню → сифон, создал пластины → очистка астрита,
  создал кристаллы → решётка, создал решётку → наука). Криогенный пак убран из
  дерева. Валидатор: новые проверки research-триггеров, unlock-space-location
  и «у каждой планеты есть технология открытия» (self-test расширен).
- `cataclysm_0.2.3.zip` — 0.2.3: исправлена битая ссылка `dying_explosion`
  (`"small-explosion"` — имя 1.1-эры, в 2.x переименовано в
  `"small-explosion-hit"`); удалены поля 1.1-эры у флюидов
  (`pressure_to_speed_ratio`/`flow_to_energy_ratio` — нет в FluidPrototype
  2.1.17). Новый валидатор `tools/validate_prototypes.py` — все 114
  прототипов против схемы 2.1.17 и реального data.raw 2.x (обязательные
  поля, OR-группы, enum'ы, лимиты, «Mandatory if», ВСЕ ссылки-имена,
  неизвестные поля) + `--self-test` против классов исторических багов.
- `cataclysm_0.2.2.zip` — 0.2.2: исправлен краш загрузки — science pack
  теперь `type = "item"` как в 2.x (был 1.1-эры "tool", где обязательна
  `durability`, а копия из ванили давала nil); проверка прототипов теперь
  контролирует и ОБЯЗАТЕЛЬНЫЕ поля каждого типа (85 прототипов, break-test).
- `cataclysm_0.2.1.zip` — 0.2.1: исправлен краш загрузки — все
  produce-achievement получили обязательный ключ `limited_to_one_game`
  (ProduceAchievementPrototype в 2.1.17); проверка ачивок в
  tools/check_lua.py ужесточена (break-test). Не грузилась без
  `durability` у tool — заменена на 0.2.2.
- `cataclysm_0.2.0.zip` — 0.2.0: молнии как на Фульгоре (та же графика/звук,
  только цветной фильтр — фиолетовый), в 2 раза чаще (1/(60*5) на чанк),
  в 1.5 раза сильнее по урону (150 electric) и в 2 раза по энергии (2GJ,
  буфер сифона 2GJ). Полный аудит всех прототипов по lua-api 2.1.17 —
  удалены 2 недокументированных поля (`resource_category`, `fluid`);
  новая статическая проверка полей (84 прототипа). Спецификация:
  docs/LIGHTNING.md, docs/API-AUDIT.md. Не грузилась без
  `limited_to_one_game` — заменена на 0.2.1.
- `cataclysm_0.1.2.zip` — 0.1.2: исправлен краш загрузки на Factorio 2.x
  (build-entity-achievement: `entity` → `to_build`; deplete-resource-achievement
  переведён на скриптовое открытие — в 2.x у него нет поля `resource`).
- `cataclysm_0.1.1.zip` — 0.1.1: исправлен краш рецептов (`category` → `categories`);
  не грузилась ачивка siphon-network, заменена на 0.1.2.
- `cataclysm_0.1.0.zip` — 0.1.0: первая играбельная версия (полный контент);
  не грузилась на 2.x, заменена на 0.1.1.

Сборка новых версий:

```bash
python3 tools/make_release.py --check
```

Структура архива: `info.json` в корне, затем `data*.lua`, `control.lua`,
`settings.lua`, `prototypes/`, `locale/`, `graphics/`, `changelog.txt`, `LICENSE.md`, `README.md`.

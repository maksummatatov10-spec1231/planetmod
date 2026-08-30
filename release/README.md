# Releases

Готовые к установке архивы мода. Файл вида `cataclysm_<version>.zip` положите
в папку `mods/` вашей установки Factorio (не распаковывая).

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

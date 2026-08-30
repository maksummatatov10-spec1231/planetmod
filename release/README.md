# Releases

Готовые к установке архивы мода. Файл вида `cataclysm_<version>.zip` положите
в папку `mods/` вашей установки Factorio (не распаковывая).

- `cataclysm_0.1.0.zip` — первая играбельная версия (полный контент).

Сборка новых версий:

```bash
python3 tools/make_release.py --check
```

Структура архива: `info.json` в корне, затем `data*.lua`, `control.lua`,
`settings.lua`, `prototypes/`, `locale/`, `graphics/`, `changelog.txt`, `LICENSE.md`, `README.md`.

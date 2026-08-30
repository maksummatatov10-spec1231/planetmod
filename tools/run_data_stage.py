#!/usr/bin/env python3
"""
Cataclysm — "3rd floor" functional check: real data-stage execution.

Runs the mod's data stage inside a real Lua runtime (LuaJIT via the `lupa`
Python package) with the *real* vanilla data stage (base + space-age from a
Factorio 2.x install, e.g. /tmp/fd) as the data.raw source of truth, then
executes the mod's data.lua and data-final-fixes.lua in dependency order.

This is not a mock of the mod's code: the mod's own Lua files are executed
for real, including their calls to table.deepcopy(data.raw[...]) on vanilla
prototypes, their requires of __base__/__space-age__ modules, and
data-final-fixes edits to vanilla labs.

Usage:
    python3 tools/run_data_stage.py --vanilla /tmp/fd --mod /home/user/planetmod \
        --out tools/out/data_raw_mod.json

Requires: pip package `lupa` (auto-installed into a throw-away venv if missing).

Exit code: 0 on success (data stage ran clean), 1 on any Lua error.
"""

import argparse
import json
import os
import subprocess
import sys

BOOTSTRAP = r"""
-- ============================================================
-- Cataclysm data-stage harness (engine environment replication)
-- ============================================================

local xhandler = debug and debug.traceback or function(e) return e end

-- 1) Engine built-ins that are NOT part of stock Lua and are
--    provided by the Factorio engine in data stage.
serpent = serpent or {}
if not serpent.block then
  serpent.block = function(v, _opts) return tostring(v) end
end
if not serpent.line then
  serpent.line = function(v, _opts) return tostring(v) end
end
if not serpent.dump then
  serpent.dump = function(v, _opts) return tostring(v) end
end
if not serpent.load then
  serpent.load = function(_s) return nil end
end

-- log() writes into the game's log file; mirror it to stderr only when
-- CATACLYSM_DEBUG_LOG is set, otherwise collect silently.
_harness_logs = _harness_logs or {}
function log(...)
  local parts = {}
  for i = 1, select("#", ...) do
    parts[i] = tostring(select(i, ...))
  end
  table.insert(_harness_logs, table.concat(parts, "\t"))
  if os.getenv("CATACLYSM_DEBUG_LOG") then
    io.stderr:write("[log] ", table.concat(parts, "\t"), "\n")
  end
end

-- table.compare / table.shallow_copy are engine built-ins (LuaJIT lacks them)
if not table.compare then
  function table.compare(a, b)
    if a == b then return true end
    if type(a) ~= "table" or type(b) ~= "table" then return false end
    for k, v in pairs(a) do
      if not table.compare(v, b[k]) then return false end
    end
    for k in pairs(b) do
      if a[k] == nil then return false end
    end
    return true
  end
end
if not table.shallow_copy then
  function table.shallow_copy(t)
    local c = {}
    for k, v in pairs(t) do c[k] = v end
    return c
  end
end

-- defines: real values come from tools/out/defines.lua when present
-- (generated from lua-api.factorio.com defines.html); otherwise a minimal
-- stub with the namespaces vanilla data stage touches.
if not _HARNESS_DEFINES_FILE then _HARNESS_DEFINES_FILE = "" end
if _HARNESS_DEFINES_FILE ~= "" then
  local ok, err = loadfile(_HARNESS_DEFINES_FILE)
  if ok then ok() else error("defines stub load failed: " .. tostring(err)) end
else
  defines = defines or {}
  defines.direction = defines.direction or {
    north = 0, northeast = 1, east = 2, southeast = 3,
    south = 4, southwest = 5, west = 6, northwest = 7,
  }
  defines.events = defines.events or {}
  defines.inventory = defines.inventory or {}
  defines.prototypes = defines.prototypes or {}
  defines.controllers = defines.controllers or {}
  defines.constant = defines.constant or {}
  defines.build_check_type = defines.build_check_type or {}
  defines.logistic_member_index = defines.logistic_member_index or {}
  defines.chunk_generated_status = defines.chunk_generated_status or {}
  defines.input_method = defines.input_method or {}
  defines.wire_connector_id = defines.wire_connector_id or {}
  defines.shooting = defines.shooting or {}
  defines.build_mode = defines.build_mode or {}
  defines.command = defines.command or {}
end

-- math.atan2 is a LuaJIT extension; Lua 5.3+ uses math.atan(y, x).
-- The game's math2d.lua calls math.atan2.
if not math.atan2 then
  math.atan2 = function(y, x) return math.atan(y, x) end
end

-- settings (startup) — vanilla 2.x data stage does not read it; stub anyway
settings = settings or { startup = {} }

-- mods metadata
mods = mods or { "base", "recycler", "quality", "elevated-rails", "space-age", "cataclysm" }

-- ============================================================
-- 2) Module loader replicating the game's per-mod require semantics
--    (__mod__.a.b  ==  __mod__/a/b.lua, plain names resolve against the
--    requiring mod's root first, then core/lualib). The require cache is
--    keyed by (owner mod, module name) — exactly like the game, which is
--    what lets base and space-age each have their own
--    "prototypes.tile.tile-trigger-effects" module.
-- ============================================================
MOD_ROOTS = {
  __base__ = "__VANILLA_BASE__",
  __core__ = "__VANILLA_CORE__",
  ["__space-age__"] = "__VANILLA_SA__",
  __quality__ = "__VANILLA_QUALITY__",
  __recycler__ = "__VANILLA_RECYCLER__",
  ["__elevated-rails__"] = "__VANILLA_ELEVATED__",
  __cataclysm__ = "__MOD_ROOT__",
}
CORE_LUALIB = "__VANILLA_CORE__/lualib"
CURRENT_MOD = "__core__"

local function file_exists(p)
  local f = io.open(p, "rb")
  if f then f:close() return true end
  return false
end

_harness_missing_content = _harness_missing_content or {}
_harness_require_cache = {}

local function resolve(name)
  local path, owner
  local prefix, rest = name:match("^(__[%w-]+__)[%./](.+)$")
  if prefix then
    local root = MOD_ROOTS[prefix]
    if not root then error("harness: unknown mod prefix " .. prefix) end
    path = root .. "/" .. rest:gsub("%.", "/") .. ".lua"
    owner = prefix
  else
    local root = MOD_ROOTS[CURRENT_MOD]
    local p1 = root .. "/" .. name:gsub("%.", "/") .. ".lua"
    local p2 = CORE_LUALIB .. "/" .. name:gsub("%.", "/") .. ".lua"
    if file_exists(p1) then
      path, owner = p1, CURRENT_MOD
    elseif file_exists(p2) then
      path, owner = p2, "__core__"
    end
  end
  if path and file_exists(path) then return path, owner end
  -- Content modules that exist in a real install but are not shipped in the
  -- data-only vanilla copy (/tmp/fd, wube/factorio-data): graphics sprite
  -- metrics (graphics/**/*.lua), menu-simulations and sound/ambient tracks.
  -- They only feed optional sprite/menu/ambient-sound data, so a substitute
  -- module is returned and recorded.
  if name:find("graphics", 1, true) or name:find("menu%-simulations")
     or name:find("/sound/") or name:find("%.sound%.") then
    return nil, "content-missing", name
  end
  error("harness: cannot resolve require('" .. name .. "')")
end

function require(name)
  local path, owner, missing = resolve(name)
  local key = owner .. "|" .. name
  local cached = _harness_require_cache[key]
  if cached ~= nil then
    return cached
  end
  _harness_require_cache[key] = true -- cycle guard / "loading" marker
  local result
  if missing then
    table.insert(_harness_missing_content, name)
    if os.getenv("CATACLYSM_DEBUG_LOAD") then
      io.stderr:write("[harness][subst] " .. name .. "\n")
    end
    _harness_subst_count = (_harness_subst_count or 0) + 1
    if name:find("/sound/") or name:find("%.sound%.") then
      -- sound/ambient modules are array elements of a data:extend call
      result = { type = "ambient-sound", name = "harness-ambient-sub-" .. _harness_subst_count }
    elseif name:find("graphics", 1, true) then
      -- graphics sprite-metric modules: direct requires read
      -- line_length/width/height from them (e.g. decoratives-gleba)
      result = { width = 32, height = 32, shift = { 0, 0 }, line_length = 1, frames = 1 }
    else
      result = {}
    end
  else
    if os.getenv("CATACLYSM_DEBUG_LOAD") then
      io.stderr:write("[harness][load] " .. name .. " -> " .. path .. "\n")
    end
    local chunk, err = loadfile(path)
    if not chunk then
      error("harness loadfile error: " .. tostring(err) .. " (" .. name .. ")", 0)
    end
    local prev = CURRENT_MOD
    CURRENT_MOD = owner
    local ok, r = xpcall(function() return chunk(name, path) end, xhandler)
    CURRENT_MOD = prev
    if not ok then
      error("harness: error while loading " .. path .. "\n" .. tostring(r), 0)
    end
    result = r
    if result == nil then result = true end
  end
  _harness_require_cache[key] = result
  return result
end

-- ============================================================
-- 3) data / data.raw / data:extend — exact copy of
--    core/lualib/dataloader.lua semantics.
-- ============================================================
local data_duplicate_checker = require("data-duplicate-checker")

data = {}
data.raw = {}
data.is_demo = false
local table_string = "table"

-- The engine pre-creates an empty data.raw[type] for every registered
-- prototype type (mods may index them before extending anything).
-- defines.prototypes (2.0.76 dump) omits a few valid types, listed explicitly.
for _base, subs in pairs(defines.prototypes or {}) do
  for type_name in pairs(subs) do
    if data.raw[type_name] == nil then
      data.raw[type_name] = {}
    end
  end
end
for _, extra in ipairs({ "decorative", "smoke", "particle" }) do
  if data.raw[extra] == nil then
    data.raw[extra] = {}
  end
end

-- prototypes defined by the cataclysm mod are recorded here
_harness_mod_protos = {}
_harness_mod_proto_set = {}

function data.extend(self, otherdata)
  if self ~= data and otherdata == nil then
    otherdata = self
  end
  if type(otherdata) ~= table_string then
    error("Invalid array of prototypes:\n\n" .. serpent.block(otherdata, {maxlevel = 1}))
  elseif #otherdata == 0 then
    if otherdata.type or otherdata.name then
      error("Expected array of prototypes, but got a single prototype:\n\n" .. serpent.block(otherdata, {maxlevel = 1}))
    end
    error("Invalid array of prototypes:\n\n" .. serpent.block(otherdata, {maxlevel = 1}))
  end

  for _, e in ipairs(otherdata) do
    if type(e.type) ~= "string" then
      error("Invalid type in the following prototype definition:\n" .. serpent.block(e))
    end
    if type(e.name) ~= "string" then
      error("Invalid name in the following prototype definition:\n" .. serpent.block(e))
    end

    local t = data.raw[e.type]
    if t == nil then
      t = {}
      data.raw[e.type] = t
    end

    data_duplicate_checker.check_for_duplicates(t, e)
    data_duplicate_checker.check_for_overwrites(t, e)
    t[e.name] = e

    if CURRENT_MOD == "__cataclysm__" then
      local k = e.type .. "\0" .. e.name
      if not _harness_mod_proto_set[k] then
        _harness_mod_proto_set[k] = true
        _harness_mod_protos[#_harness_mod_protos + 1] = { type = e.type, name = e.name }
      end
    end
  end
end

-- ============================================================
-- 4) JSON serializer (Lua -> JSON string)
-- ============================================================
local function jstr(s)
  s = tostring(s)
  s = s:gsub("\\", "\\\\")
  s = s:gsub('"', '\\"')
  s = s:gsub("\n", "\\n")
  s = s:gsub("\r", "\\r")
  s = s:gsub("\t", "\\t")
  return '"' .. s .. '"'
end

local function tojson(v, seen)
  local t = type(v)
  if t == "nil" then return "null"
  elseif t == "boolean" then return tostring(v)
  elseif t == "number" then
    if v ~= v then return "null" end
    if v == math.huge then return "1e999" end
    if v == -math.huge then return "-1e999" end
    if v == math.floor(v) and math.abs(v) < 1e15 then
      return string.format("%d", v)
    end
    return string.format("%.17g", v)
  elseif t == "string" then return jstr(v)
  elseif t == "table" then
    if seen[v] then return "null" end
    seen[v] = true
    local is_array, max_n = true, 0
    for k in pairs(v) do
      if type(k) ~= "number" or k < 1 or k % 1 ~= 0 then
        is_array = false
      end
      if type(k) == "number" and k > max_n then max_n = k end
    end
    if is_array and max_n > 0 then
      local parts = {}
      for i = 1, max_n do
        parts[i] = tojson(v[i], seen)
      end
      seen[v] = nil
      return "[" .. table.concat(parts, ",") .. "]"
    else
      local keys = {}
      for k in pairs(v) do keys[#keys + 1] = k end
      table.sort(keys, function(a, b)
        return tostring(a) < tostring(b)
      end)
      local parts = {}
      for i, k in ipairs(keys) do
        local kk = type(k) == "string" and jstr(k) or jstr(tostring(k))
        parts[i] = kk .. ":" .. tojson(v[k], seen)
      end
      seen[v] = nil
      return "{" .. table.concat(parts, ",") .. "}"
    end
  end
  return "null"
end

-- ============================================================
-- 5) Engine preloads core lualib into globals (util, sound-util,
--    math2d), then runs the real data stages in dependency order.
-- ============================================================
for _, pre in ipairs({ "math2d", "util", "sound-util" }) do
  local ok, err = pcall(function() require(pre) end)
  if not ok then
    io.stderr:write("HARNESS PRELOAD ERROR in " .. pre .. ":\n" .. tostring(err) .. "\n")
    os.exit(1)
  end
end

local runs = {
  { "__core__.data", "__core__" },
  { "__base__.data", "__base__" },
  { "__recycler__.data", "__recycler__" },
  { "__quality__.data", "__quality__" },
  { "__elevated-rails__.data", "__elevated-rails__" },
  { "__space-age__.data", "__space-age__" },
  { "__cataclysm__.data", "__cataclysm__" },
  { "__cataclysm__.data-final-fixes", "__cataclysm__" },
}

for _, r in ipairs(runs) do
  local prev = CURRENT_MOD
  CURRENT_MOD = r[2]
  local ok, err = pcall(function() require(r[1]) end)
  CURRENT_MOD = prev
  if not ok then
    io.stderr:write("HARNESS DATA STAGE ERROR in " .. r[1] .. ":\n" .. tostring(err) .. "\n")
    os.exit(1)
  end
end

-- ============================================================
-- 6) Collect output for the validator.
-- ============================================================
local out = {}
out.mod_protos = {}
for _, rec in ipairs(_harness_mod_protos) do
  local full = data.raw[rec.type] and data.raw[rec.type][rec.name]
  if full == nil then
    io.stderr:write("HARNESS BUG: prototype not found after extend: " .. rec.type .. "/" .. rec.name .. "\n")
    os.exit(1)
  end
  out.mod_protos[#out.mod_protos + 1] = {
    type = rec.type,
    name = rec.name,
    proto = full,
  }
end

out.vanilla_counts = {}
out.names_by_type = {}
for tname, t in pairs(data.raw) do
  local n = 0
  local names = {}
  for name in pairs(t) do
    n = n + 1
    names[#names + 1] = name
  end
  out.vanilla_counts[tname] = n
  table.sort(names)
  out.names_by_type[tname] = names
end

-- The 5 vanilla donors the mod deep-copies, plus lab state after
-- data-final-fixes (proves the vanilla edit applied).
out.donors = {}
for _, d in ipairs({
  { type = "offshore-pump", name = "offshore-pump" },
  { type = "lightning-attractor", name = "lightning-collector" },
  { type = "assembling-machine", name = "foundry" },
  { type = "assembling-machine", name = "electromagnetic-plant" },
  { type = "generator", name = "steam-turbine" },
}) do
  local p = data.raw[d.type] and data.raw[d.type][d.name]
  if p == nil then
    io.stderr:write("HARNESS ERROR: vanilla donor missing: " .. d.type .. "/" .. d.name .. "\n")
    os.exit(1)
  end
  out.donors[#out.donors + 1] = { type = d.type, name = d.name, proto = p }
end

out.labs = {}
for name, p in pairs(data.raw.lab or {}) do
  out.labs[#out.labs + 1] = { name = name, inputs = p.inputs }
end
table.sort(out.labs, function(a, b) return a.name < b.name end)

out.logs = _harness_logs
out.missing_content = _harness_missing_content

local seen = {}
io.write(tojson(out, seen))
"""


def ensure_lupa():
    try:
        import lupa  # noqa: F401
        return sys.executable
    except ImportError:
        venv = os.environ.get("CATACLYSM_VENV", "/tmp/cataclysm-venv")
        py = os.path.join(venv, "bin", "python")
        if not os.path.exists(py):
            print(f"[harness] installing lupa into {venv} …", file=sys.stderr)
            subprocess.run([sys.executable, "-m", "venv", venv], check=True)
            subprocess.run([py, "-m", "pip", "install", "-q", "lupa"], check=True)
        return py


def main():
    ap = argparse.ArgumentParser(description="Cataclysm data-stage functional harness")
    ap.add_argument("--vanilla", default="/tmp/fd", help="vanilla 2.x data root (base/, core/, space-age/)")
    ap.add_argument("--mod", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--out", default=None, help="output JSON path")
    ap.add_argument("--defines-lua", default=None, help="generated defines.lua stub (optional)")
    args = ap.parse_args()

    vanilla = os.path.abspath(args.vanilla)
    mod = os.path.abspath(args.mod)
    for sub in ("base", "core", "space-age", "quality", "recycler", "elevated-rails"):
        if not os.path.isdir(os.path.join(vanilla, sub)):
            print(f"[harness] missing {vanilla}/{sub} — need a real Factorio 2.x data dir "
                  f"(quality/recycler/elevated-rails can be copied from wube/factorio-data)", file=sys.stderr)
            sys.exit(2)
    if not os.path.isfile(os.path.join(mod, "data.lua")):
        print(f"[harness] missing {mod}/data.lua", file=sys.stderr)
        sys.exit(2)

    script = BOOTSTRAP
    script = script.replace("__VANILLA_BASE__", os.path.join(vanilla, "base"))
    script = script.replace("__VANILLA_CORE__", os.path.join(vanilla, "core"))
    script = script.replace("__VANILLA_SA__", os.path.join(vanilla, "space-age"))
    script = script.replace("__VANILLA_QUALITY__", os.path.join(vanilla, "quality"))
    script = script.replace("__VANILLA_RECYCLER__", os.path.join(vanilla, "recycler"))
    script = script.replace("__VANILLA_ELEVATED__", os.path.join(vanilla, "elevated-rails"))
    script = script.replace("__MOD_ROOT__", mod)
    if args.defines_lua:
        script = script.replace('_HARNESS_DEFINES_FILE = ""',
                                f'_HARNESS_DEFINES_FILE = "{args.defines_lua}"')

    py = ensure_lupa()
    code = subprocess.run([py, "-c", f"""
import sys
sys.argv = ["harness"]
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False)
lua.execute({script!r})
"""], capture_output=True, text=True, cwd=mod)
    if code.returncode != 0:
        print("[harness] Lua data stage FAILED", file=sys.stderr)
        print(code.stdout, file=sys.stderr)
        print(code.stderr, file=sys.stderr)
        sys.exit(1)

    out_path = args.out or os.path.join(mod, "tools", "out", "data_raw_mod.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(code.stdout)
    print(f"[harness] OK — data stage ran clean; wrote {out_path}")
    print(f"[harness] size: {os.path.getsize(out_path)} bytes")

    # quick summary
    data = json.loads(code.stdout)
    n = len(data["mod_protos"])
    types = {}
    for rec in data["mod_protos"]:
        types[rec["type"]] = types.get(rec["type"], 0) + 1
    print(f"[harness] mod prototypes: {n} across {len(types)} types: "
          + ", ".join(f"{k}={v}" for k, v in sorted(types.items())))
    print(f"[harness] vanilla prototype types: {len(data['vanilla_counts'])}")
    labs_with = sum(1 for l in data["labs"] if l["inputs"] and "cataclysmic-science-pack" in l["inputs"])
    print(f"[harness] labs patched with cataclysmic-science-pack: {labs_with}/{len(data['labs'])}")
    if data.get("missing_content"):
        print(f"[harness] content modules substituted (sprite metrics/menu sims, no data impact): "
              + ", ".join(data["missing_content"]))


if __name__ == "__main__":
    main()

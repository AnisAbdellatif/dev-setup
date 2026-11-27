#!/usr/bin/env python3
"""Load and validate catalog.toml + platforms/<os>.toml; optionally validate a selection file.

Stdlib only (Python 3.11+). Also imported by select.py.
  python3 scripts/validate.py                      # check the data for every OS
  python3 scripts/validate.py --selection FILE     # check a selection.json (os taken from the file)
Exit 1 on any error.
"""
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OSES = ("macos", "linux", "windows")
CHOICE_TYPES = ("one", "many", "bool", "text")
INSTALL_KEYS = ("install", "hint", "with", "builtin", "na")


def _toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def load(os_name):
    """Merged menu model for one OS: components, entries (tools, apps), choices, presets."""
    cat = _toml(ROOT / "catalog.toml")
    plat = _toml(ROOT / "platforms" / f"{os_name}.toml")
    tmpl = plat.get("install_tmpl")
    tools = {t["id"]: t for t in cat["tool"] if os_name in t.get("os", OSES)}
    items = {i["id"]: i for i in plat.get("item", [])}
    entries = []
    for tid, t in tools.items():
        e = {**t, **items.get(tid, {}), "label": f"{tid}: {t['why']}"}
        entries.append(e)
    for iid, i in items.items():
        if iid not in tools and iid not in {t["id"] for t in cat["tool"]}:
            entries.append(dict(i))
    for e in entries:
        if not any(k in e for k in ("install", "with", "builtin", "na")) and tmpl and "hint" not in e:
            e["install"] = tmpl.format(pkg=e.get("pkg", e["id"]))
        if "hint" not in e and plat.get("default_hint") and "install" not in e and "with" not in e \
                and "builtin" not in e and "na" not in e:
            e["hint"] = plat["default_hint"]
    choices = [c for c in cat.get("choice", []) if os_name in c.get("os", OSES)] + plat.get("choice", [])
    return {"os": os_name, "components": cat["component"], "presets": cat["preset"],
            "entries": entries, "choices": choices, "catalog_ids": {t["id"] for t in cat["tool"]}}


def check_data():
    errs = []
    cat = _toml(ROOT / "catalog.toml")
    comps = set(cat["component"])
    ids = [t["id"] for t in cat["tool"]]
    errs += [f"catalog: duplicate tool id {i}" for i in {i for i in ids if ids.count(i) > 1}]
    for t in cat["tool"]:
        for k in ("id", "component", "check", "why"):
            if k not in t:
                errs.append(f"catalog: tool {t.get('id', '?')} lacks {k}")
        if t.get("component") not in comps:
            errs.append(f"catalog: {t['id']} component {t.get('component')!r} not declared")
    for n, p in cat["preset"].items():
        errs += [f"preset {n}: unknown component {c}" for c in p["components"] if c != "*" and c not in comps]
    for os_name in OSES:
        plat = _toml(ROOT / "platforms" / f"{os_name}.toml")
        items = {}
        for i in plat.get("item", []):
            if i["id"] in items:
                errs.append(f"{os_name}: duplicate item {i['id']}")
            items[i["id"]] = i
            has = [k for k in INSTALL_KEYS if k in i] or (["tmpl"] if plat.get("install_tmpl") else [])
            if not has and not plat.get("default_hint"):
                errs.append(f"{os_name}: item {i['id']} has no install method")
            if i["id"] not in ids and not ("label" in i and i.get("component") in comps):
                errs.append(f"{os_name}: platform-only item {i['id']} needs label and a declared component")
            if "with" in i and i["with"] not in items and i["with"] not in {x["id"] for x in plat["item"]}:
                errs.append(f"{os_name}: {i['id']} 'with' unknown item {i['with']}")
        for t in cat["tool"]:
            if os_name in t.get("os", OSES) and t["id"] not in items:
                errs.append(f"{os_name}: catalog tool {t['id']} has no item (add it or mark na)")
        for i in items:
            if i in ids and os_name not in next(t for t in cat["tool"] if t["id"] == i).get("os", OSES):
                errs.append(f"{os_name}: item {i} is excluded by the catalog os filter")
        cids = [c["id"] for c in load(os_name)["choices"]]
        errs += [f"{os_name}: duplicate choice {c}" for c in {c for c in cids if cids.count(c) > 1}]
        for c in load(os_name)["choices"]:
            if c.get("type") not in CHOICE_TYPES:
                errs.append(f"{os_name}: choice {c['id']} bad type")
            if c.get("type") in ("one", "many") and not c.get("options"):
                errs.append(f"{os_name}: choice {c['id']} needs options")
            if c.get("component") not in comps:
                errs.append(f"{os_name}: choice {c['id']} component not declared")
            if c.get("type") == "one" and c.get("default") not in c.get("options", []):
                errs.append(f"{os_name}: choice {c['id']} default not in options")
    return errs


def check_selection(path):
    errs = []
    sel = json.load(open(path))
    if sel.get("version") != 1:
        errs.append("selection: version must be 1")
    if sel.get("os") not in OSES:
        return errs + ["selection: os must be one of " + ", ".join(OSES)]
    m = load(sel["os"])
    known = {e["id"] for e in m["entries"]}
    offered, selected = set(sel.get("offered", [])), set(sel.get("selected", []))
    errs += [f"selection: unknown offered id {i}" for i in offered - known]
    errs += [f"selection: selected id {i} was not offered" for i in selected - offered]
    cmap = {c["id"]: c for c in m["choices"]}
    for k, v in sel.get("choices", {}).items():
        c = cmap.get(k)
        if not c:
            errs.append(f"selection: unknown choice {k}")
        elif c["type"] == "one" and v not in c["options"]:
            errs.append(f"selection: choice {k} value {v!r} not in options")
        elif c["type"] == "many" and not (isinstance(v, list) and set(v) <= set(c["options"])):
            errs.append(f"selection: choice {k} must be a subset of its options")
        elif c["type"] == "bool" and not isinstance(v, bool):
            errs.append(f"selection: choice {k} must be true/false")
        elif c["type"] == "text" and not isinstance(v, str):
            errs.append(f"selection: choice {k} must be a string")
    return errs


if __name__ == "__main__":
    if "--selection" in sys.argv:
        errs = check_selection(sys.argv[sys.argv.index("--selection") + 1])
    else:
        errs = check_data()
    print("\n".join(errs) or "ok")
    sys.exit(1 if errs else 0)

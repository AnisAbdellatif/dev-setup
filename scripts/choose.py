# /// script
# requires-python = ">=3.11"
# dependencies = ["questionary>=2.0", "prompt_toolkit>=3.0"]
# ///
"""Interactive install menu: presets, tools, OS choices, git identity -> selection.json for the agent.

  uv run scripts/choose.py                  # interactive (run it in your own terminal)
  uv run scripts/choose.py --preset server --yes   # no prompts: preset + defaults
Writes ~/.config/dev-setup/selection.json (ids and values only, never commands).
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from picker import pick
from validate import OSES, load

DEFAULT_OUT = Path.home() / ".config" / "dev-setup" / "selection.json"


def detect_os():
    return {"darwin": "macos", "linux": "linux", "win32": "windows"}.get(sys.platform, "linux")


def installed(entries):
    """id -> True/False by running each `check`; None when there is no check (platform-only items)."""
    def run(e):
        if "check" not in e:
            return e["id"], None
        try:
            r = subprocess.run(e["check"], shell=True, capture_output=True, stdin=subprocess.DEVNULL, timeout=5)
            return e["id"], r.returncode == 0
        except Exception:
            return e["id"], False
    with ThreadPoolExecutor(8) as ex:
        return dict(ex.map(run, entries))


def preset_components(m, preset):
    comps = m["presets"][preset]["components"]
    return set(m["components"]) if comps == ["*"] else set(comps)


def default_choice(c, os_name):
    return c.get("default_by_os", {}).get(os_name, c.get("default"))


def title(e, have):
    tags = []
    if have.get(e["id"]):
        tags.append("installed")
    if e.get("elevation"):
        tags.append("sudo/admin")
    if e.get("ask"):
        tags.append("remote installer")
    tag = f"  [{', '.join(tags)}]" if tags else ""
    return f"{e['label'][:72]}{tag}"


def main():
    for s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252; labels/box chars are utf-8
        s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--os", choices=OSES, default=detect_os())
    ap.add_argument("--preset", choices=["full", "minimal", "server", "custom"])
    ap.add_argument("--yes", action="store_true", help="no prompts: preset (default full) + defaults")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-check", action="store_true", help="skip installed detection")
    a = ap.parse_args()

    m = load(a.os)
    entries = m["entries"]
    have = {} if a.no_check else installed(entries)
    comp_title = {k: v["title"] for k, v in m["components"].items()}

    if a.yes:
        preset = a.preset or "full"
        ticked = preset_components(m, preset)
        selected = [e["id"] for e in entries if e.get("component") in ticked and "na" not in e]
        choices = {c["id"]: default_choice(c, a.os) for c in m["choices"]
                   if c["component"] in ticked or c["component"] in ("dotfiles", "os-defaults")}
        extra = []
    else:
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            sys.exit("interactive mode needs a real terminal (run it yourself, not through an agent or pipe); "
                     "use --yes [--preset X] for non-interactive, or the chat checklist in INSTRUCTIONS section 2.")
        import questionary as q
        preset = a.preset or q.select(
            "Starting preset (you can change everything next)",
            choices=["full", "minimal", "server", "custom"], default="full").ask()
        if preset is None:
            sys.exit(130)
        ticked = preset_components(m, preset)

        rows = [{"id": e["id"], "label": title(e, have), "group": comp_title[e["component"]],
                 **({"disabled": e["na"]} if "na" in e else {})}
                for cid in m["components"] for e in entries if e.get("component") == cid]
        pre = {e["id"] for e in entries if e.get("component") in ticked and "na" not in e}
        try:
            got = pick(rows, pre, "Tools and apps")
        except Exception as ex:  # prompt_toolkit raises NoConsoleScreenBufferError under mintty/Git Bash
            sys.exit(f"cannot start the full-screen picker ({type(ex).__name__}). On Windows run this from "
                     "PowerShell or Windows Terminal, not Git Bash/mintty; or use --yes, or the chat checklist.")
        if got is None:
            sys.exit(130)
        selected = [e["id"] for e in entries if e["id"] in got]
        sel_comps = {e["component"] for e in entries if e["id"] in selected}

        choices = {}
        for cid, c in m["components"].items():
            group = [c2 for c2 in m["choices"] if c2["component"] == cid]
            if not group:
                continue
            has_entries = any(e.get("component") == cid for e in entries)
            if has_entries and cid not in sel_comps:
                continue
            if not has_entries and not q.confirm(f"Configure: {c['title']}?",
                                                 default=cid == "dotfiles").ask():
                continue
            for ch in group:
                d = default_choice(ch, a.os)
                t = ch["type"]
                if t == "one":
                    v = q.select(ch["label"], choices=ch["options"], default=d).ask()
                elif t == "many":
                    v = q.checkbox(ch["label"], choices=[q.Choice(o, o, checked=o in d) for o in ch["options"]]).ask()
                elif t == "bool":
                    v = q.confirm(ch["label"], default=bool(d)).ask()
                else:
                    v = q.text(ch["label"], default=d or "").ask()
                if v is None:
                    sys.exit(130)
                choices[ch["id"]] = v
        raw = q.text("Other tools you want that are not listed (comma-separated, optional)").ask()
        if raw is None:
            sys.exit(130)
        extra = [x.strip() for x in raw.split(",") if x.strip()]
        print(f"\n{len(selected)} items selected, {len(choices)} choices, {len(extra)} extra.")
        if not q.confirm(f"Write {a.out}?", default=True).ask():
            sys.exit(130)

    sel = {"version": 1, "os": a.os, "preset": preset, "offered": [e["id"] for e in entries],
           "selected": selected, "choices": choices, "extra": extra}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(sel, indent=2) + "\n")
    print(f"wrote {a.out}\nNow tell your agent to continue (it validates the file, shows the plan, asks for approval).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check every package name and installer URL in platforms/*.toml against the real registries.

Stdlib only. Needs internet. No tokens: GitHub is read through plain github.com / raw URLs, not the API.
  python3 scripts/verify_ids.py [macos|linux|windows ...]
Checks: Homebrew formulae/casks (formulae.brew.sh), third-party brew taps and scoop buckets (raw GitHub),
winget IDs (microsoft/winget-pkgs manifests), and every https:// URL in an install command.
Exit 1 if anything fails. Network errors are reported as ERR, not FAIL.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from validate import OSES, load

UA = {"User-Agent": "dev-setup-verify"}
TOKEN = os.environ.get("GITHUB_TOKEN")


def get(url, api=False, method="GET"):
    h = dict(UA)
    if api and TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # network/DNS
        return f"ERR {type(e).__name__}"


def exists(url, **kw):
    s = get(url, **kw)
    return ("ok" if s == 200 else "ERR" if isinstance(s, str) else "FAIL"), s


def checks_for(os_name):
    """(kind, name, url, api?) tuples for one OS."""
    out = []
    for e in load(os_name)["entries"]:
        cmd = e.get("install", "")
        if m := re.match(r"brew install --cask (\S+)$", cmd):
            parts = m[1].split("/")
            if len(parts) == 3:
                out.append(("brew-tap-cask", m[1], f"https://raw.githubusercontent.com/{parts[0]}/homebrew-{parts[1]}/HEAD/Casks/{parts[2]}.rb", False))
            else:
                out.append(("brew-cask", m[1], f"https://formulae.brew.sh/api/cask/{m[1]}.json", False))
        elif m := re.match(r"brew install (\S+)$", cmd):
            parts = m[1].split("/")
            if len(parts) == 3:
                out.append(("brew-tap-formula", m[1], f"https://raw.githubusercontent.com/{parts[0]}/homebrew-{parts[1]}/HEAD/Formula/{parts[2]}.rb", False))
            else:
                out.append(("brew-formula", m[1], f"https://formulae.brew.sh/api/formula/{m[1]}.json", False))
        elif m := re.search(r"winget install --id (\S+)", cmd):
            pid = m[1]
            segs = pid.split(".")
            path = f"{segs[0][0].lower()}/{'/'.join(segs)}"
            out.append(("winget", pid, f"https://github.com/microsoft/winget-pkgs/tree/master/manifests/{path}", False))
        elif m := re.match(r"scoop install (\S+)$", cmd):
            for bucket in ("Main", "Extras"):
                out.append((f"scoop-{bucket}", m[1], f"https://raw.githubusercontent.com/ScoopInstaller/{bucket}/master/bucket/{m[1]}.json", False))
        for u in re.findall(r"https://[^\s\"')|]+", cmd):
            out.append(("url", u, u, False))
    return out


def main():
    oses = [o for o in sys.argv[1:] if o in OSES] or list(OSES)
    jobs = [(o, *c) for o in oses for c in checks_for(o)]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda j: (j, exists(j[3], api=j[4])), jobs))
    # scoop: ok if found in either bucket
    scoop_ok = {j[2] for j, (st, _) in results if j[1].startswith("scoop-") and st == "ok"}
    bad = 0
    for (os_name, kind, name, url, _), (st, code) in results:
        if kind.startswith("scoop-") and name in scoop_ok:
            if st != "ok":
                continue
        if st != "ok":
            bad += st == "FAIL"
        print(f"{st:4} {os_name:7} {kind:16} {name}" + ("" if st == "ok" else f"  ({code}) {url}"))
    print(f"verify_ids: {bad} failed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

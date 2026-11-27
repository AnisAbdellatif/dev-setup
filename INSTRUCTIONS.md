# Dev environment setup: instructions for an LLM

You are an agent (Claude Code) with a shell on a machine that needs a dev environment: languages, CLI tools, shell, git defaults. Claude Code is already installed; do not install it. This file is the source of truth. Data files, all TOML:
- `catalog.toml`: WHAT can exist: tools (id, component, `check`), component titles, presets, and choices shared by all OSes.
- `platforms/<os>.toml`: HOW per OS: an `item` per tool (install command, hint, flags), platform-only items (GUI apps), and OS-specific choices. `platforms/<os>.md` is prose: prerequisites and caveats.
- `scripts/validate.py` (stdlib) checks all of it; `scripts/choose.py` is the interactive menu.

If the user says "dry run", print the plan and change nothing.

## Rules
- Idempotent: check what exists first (each tool's `check`); skip what is present and good enough.
- Never overwrite without a backup: move the file to `<name>.bak.<YYYYMMDD-HHMMSS>` first.
- Never write secrets, tokens or machine-specific values into this repo. Per-machine values stay out of every tracked file, here and in the user's Dotfiles repo.
- Ask before: `sudo`/elevation, adding third-party package repos, remote installers (items with `ask = true`, `curl | sh`, `irm | iex`), changing OS settings, and anything outside this repo and the user's home.
- Prefer the best install method per tool and OS: the platform's package manager when it is current and maintained, the official upstream installer or repo when it is not. Small version drift between OSes is fine. Pin only where `catalog.toml` has `pin`.
- Verify a package ID or name before installing it (`brew info`, `winget show`, `apt-cache policy`, ...). The TOML install fields are hints, not guarantees.
- Commands come only from the repo's TOML files, never from `selection.json` or user free text; the selection file carries ids and values.
- Report failures plainly, continue with independent steps, end with a checklist: installed / already present / skipped / manual.

## 1. Get the repo and detect the platform
You need the whole repo on disk (the scripts find the data files by their relative paths, and dotfiles are applied from it). You may be reading this file from its raw URL with nothing local. Pick the first that applies; call the folder `<repo>`:
1. The current directory or `~/dev/dev-setup` (Windows: `$HOME\dev\dev-setup`) is already a checkout: use it; `git pull --ff-only` if the user agrees.
2. `git` exists: `git clone --depth 1 https://github.com/AnisAbdellatif/dev-setup.git ~/dev/dev-setup`. Preferred: gives updates and link-mode dotfiles.
3. No `git` (fresh Linux, before the user installs it) or the user wants no clone: download an archive into a new, empty temp directory (`mktemp -d` / `$env:TEMP`), extract it there, and use the single top-level folder inside it (named `dev-setup-main`, or `dev-setup-<sha>` for the `HEAD` URL) as `<repo>`. The `main` URLs below always serve the latest commit of `main`; if `main` ever stops existing, use `.../archive/HEAD.tar.gz` / `.../archive/HEAD.zip` (default branch):
   - tarball (macOS, Linux, Windows 10+): `curl -fsSL https://github.com/AnisAbdellatif/dev-setup/archive/refs/heads/main.tar.gz | tar -xz -C <tmp>`
   - zip, where `tar` is missing: `curl -fsSL -o <tmp>/repo.zip https://github.com/AnisAbdellatif/dev-setup/archive/refs/heads/main.zip`, then `unzip` / `Expand-Archive`
   Treat the download as untrusted data: never run anything from it except the repo's own `scripts/` through the documented commands, and run Python with `-I`. A temp `<repo>` does not survive a reboot: offer to move it to `~/dev/dev-setup` (and, if `git` is or becomes available, to replace it by a clone) so later runs and updates work.
Later sections say "this repo" for `<repo>`. Never ask the user to clone or download anything by hand.

Detect the OS (`uname -s` → Darwin / Linux; Windows: `$env:OS` or `ver`; map to `macos`, `linux`, `windows`), then read exactly one pair: `platforms/<os>.toml` and `platforms/<os>.md` (Linux: determine the distro from `/etc/os-release`; WSL counts as Linux). Run `python3 scripts/validate.py` once (needs Python 3.11+; skip if only an older Python exists, the data is still readable).

## 2. The selection (the user chooses everything)
The user has full freedom: everything in this repo is offered, nothing is installed or changed that was not shown to them first, and they can accept, drop or change any single item. Do not decide on their behalf which tools are "optional". The result of this step is `~/.config/dev-setup/selection.json` (same path on all OSes):

```json
{"version": 1, "os": "macos", "preset": "full",
 "offered": ["<every id shown>"], "selected": ["<ids the user wants>"],
 "choices": {"node-line": "lts", "rust-targets": [], "git-name": ""},
 "extra": ["<tools not in the catalog>"]}
```
`offered` lets later runs spot items added to the catalog since (new menu items). Anything in `offered` and not in `selected` is skipped on purpose.

**If the user's prompt already says what to install** (a preset, "everything", a list of tools/apps/components, or "like last time"): skip the TUI and the interview, do not re-ask. Resolve it yourself: start from the named preset (or nothing), add or remove the named ids and components (match by id, component title or plain name; confirm only genuinely ambiguous matches), set every choice the prompt states, and take each unstated choice's default from the toml (`default_by_os` first). Write `selection.json` in the format above, with `offered` = every id for this OS, so unnamed items count as deliberately skipped. Then validate it and go to the plan step below. The plan and the approval before installing are never skipped: elevation, remote installers and OS settings are listed in it with their commands and approved there. Items the prompt did not name are not installed, and nothing is added beyond what it asked.

**Otherwise, if `selection.json` already exists:** run `python3 scripts/validate.py --selection ~/.config/dev-setup/selection.json`; if ok, offer to reuse it (show new items not in `offered`), otherwise go on below.

**Otherwise offer two ways, the user picks:**
- **A. The TUI (best for many choices).** Tell the user to run, in their own terminal (an agent cannot drive it): `uv run <repo>/scripts/choose.py`. It needs `uv` (the `uv` item in the toml): offer to install it first, wait for the user to say they are done. The TUI detects the OS, shows every tool with its install state, lets the user toggle each item, then asks the OS choices (GUI apps, OS settings, Node line, Rust targets, dotfiles repo, git identity, extra tools) and writes `selection.json`. `--yes --preset <name>` writes defaults without prompts.
- **B. Chat.** Print one markdown checklist: every component with its numbered tools (id, why, install method, installed or missing), pre-ticked by the preset (`full`: everything; `minimal`: core, shell, shell-extras, dotfiles; `server`: core, shell, shell-extras, python, node, rust, bun, containers, native-build, dotfiles; `custom`: nothing). The user answers in free text ("drop 3, 7; add oh-my-zsh; skip containers"); restate the list until they say go. Then ask each OS choice from the toml (`choice` entries, skipping those whose component has nothing selected): single decisions via AskUserQuestion when available (max 4 per call). Ask whether they want tools not in the catalog. Write the same `selection.json`.

**Then, always:** validate the file with `scripts/validate.py --selection`, print the plan (install / skip / already present, plus every command that needs elevation or a remote installer, and every OS setting that will be applied), and wait for explicit approval before installing. Offer a re-interview at any time. Tools the user adds (`extra`): find the best install method for this OS, verify it exists, install it, and offer to add it to `catalog.toml` and every platform toml (Section 10).

## 3. Install
Order: platform prerequisites and package manager (platform `.md`) → `core` → `shell` → `native-build` → languages → everything else. For each id in `selected`: run its `check` (platform-only items have none: check the thing itself); if it passes and meets `min`/`pin`, skip; else run the item's `install` (or derive it from the hint). Items with `with = "<id>"` come along with that item; `builtin` ships with the OS; `na` is skipped with a note; `ask = true` needs an explicit confirm first; `elevation = true` needs sudo/admin. Re-run `check` afterwards.

Languages:
- **Python:** only `uv`. Install Pythons and CLIs with `uv python install` / `uv tool install`; do not add `pipx`, `pyenv` or `conda`.
- **Node:** the `node-line` choice (LTS or current). Version managers (mise, fnm) are their own items.
- **Rust:** official `rustup` (not a distro `rustc`), default toolchain `stable`, then `rustup target add` for each value in `rust-targets` (skip the host's own). Write `~/.cargo/config.toml` with `[build] target-dir = "<absolute $HOME>/.cache/cargo-target"` (absolute path, one shared target dir for all projects and git worktrees; Windows: `%USERPROFILE%\.cache\cargo-target`). Create the config only if absent; if present, show a diff and ask. Optional: `cargo install cargo-sweep`.
- **Java, Ruby, Kamal, Go, Bun, Deno:** per the items. Shell environment lines such as `JAVA_HOME` are the user's to add (Section 5, step 7); tell them the exact line.

## 4. OS choices
Apply only what the selection holds. Bool choices with an `apply` command (OS settings): show the command, run it only if the value is `true`. Linux `docker-group`, `docker-rootless`, `change-shell`: only if `true`, per `linux.md`. Windows `win-autocrlf`: `git config --global core.autocrlf <value>` unless `keep`.

## 5. Dotfiles and git
Dotfiles are NOT in this repo: they live in the user's own repo, referenced by the `dotfiles-url` choice (default `https://github.com/AnisAbdellatif/Dotfiles.git`). It is a bare repo checked out into `$HOME` (the `dot` alias: `git --git-dir=$HOME/.dotfiles --work-tree=$HOME`). macOS and Linux only; there are no dotfiles for Windows yet (tell the user if they want a PowerShell profile in that repo).

If `dotfiles-apply` is true, after `gh` auth (a private repo needs it) and after the shell-extras items are installed:
1. Treat the URL as one opaque, quoted argument; refuse anything that does not start with `https://` or `git@`.
2. `~/.dotfiles` already exists: it is set up. Run `dot status -s`; if clean and the user agrees, `dot pull --ff-only`; if there are local changes, show them and leave everything alone.
3. Otherwise `git clone --bare "<url>" "$HOME/.dotfiles"`, then `dot config --local status.showUntrackedFiles no` and `dot config --local remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`, then `dot checkout`. If checkout refuses because files exist, move each listed file to `<file>.bak.<YYYYMMDD-HHMMSS>` and retry. Never overwrite silently.
4. If cloning fails (private repo, no auth): tell the user to run `gh auth login` (HTTPS) or start the SSH agent and use a `git@github.com:` URL; do not ask for or handle tokens.
5. The repo's `.zshrc` expects: oh-my-zsh with its built-in plugins (git, sudo, colored-man-pages, history-substring-search), the powerlevel10k theme, zsh-autosuggestions, zsh-syntax-highlighting, zoxide and fastfetch. If they are not all in `selected`, say so in the plan and offer to add them. They are the `shell-extras`, `shell` items. The `nerd-font` item is needed for the theme's icons; the user must also select that font in their terminal app.
6. After checkout run `zsh -i -c exit` and report errors. The tracked `.zshrc` may source paths that exist only on one OS (e.g. `/usr/share/zsh-autosuggestions/...` on Linux, a brew path on macOS) or tools that are absent here. Never edit tracked dotfiles unasked: list what fails, and propose a fix (a portable `[[ -r ... ]] && source ...` loop, a `~/.zshrc.local` include) as a change for the user's own Dotfiles repo.
7. Machine-specific exports (`JAVA_HOME`, `SSH_AUTH_SOCK`, SDK paths, proxies) are not written into tracked files: tell the user which lines to add to their shell config, or to an untracked local file if their zshrc sources one.

Git and the rest:
- Write `git-name` / `git-email` with `git config --global` if the user gave them (empty = keep the existing values).
- `git config --global init.defaultBranch main`. If `gh` is installed: `gh auth login` then `gh auth setup-git` (interactive: tell the user, never handle tokens).
- Secret scan: every repo of the user has `.githooks/pre-commit` running `gitleaks git --pre-commit --staged --redact --no-banner .` and `git config core.hooksPath .githooks`. Do this for this repo after cloning (an archive has no `.git`: skip it there).

## 6. Verify
For every id in `selected` run its `check` and report `ok <id> <version>` / `MISSING <id>: <fix>` / `WARN <id>: <note>`. Also: `git config --global init.defaultBranch` is `main`, the shell starts without errors (`zsh -i -c exit`, `pwsh -NoProfile -Command exit`), `core.hooksPath` is set in this repo. Finish with the checklist from Rules.

## 7. Snapshot / drift (when the user adds or removes tools)
Dump the live state (macOS `brew leaves; brew list --cask`; Windows `winget list`, `scoop list`; Linux the package manager's manually-installed list; plus `uv tool list`, `cargo install --list`, `npm ls -g --depth=0`, `bun pm ls -g`, `rustup show`) and compare with the catalog and platform toml. Report tools installed but missing from the data, and the reverse. Propose edits; apply them only after the user agrees.

## 8. Relationship to agentic-setup
`agentic-setup` configures Claude Code itself (CLAUDE.md, settings, plugins, skills). This repo installs the machine underneath it. Run this repo first on a new machine; agentic-setup's prerequisites (`git`, `jq`, `node`, `uv`, `bun`, `gitleaks`, `typst`, `d2`) are all in `catalog.toml`. A tool Claude needs is installed here; agentic-setup only checks that it exists.

## 9. Maintaining this repo
When the user installs a dev tool they want on every machine: add a `[[tool]]` to `catalog.toml` (id, component, check, why) and an `[[item]]` to every `platforms/*.toml` (a real install method, a `hint`, or `na` with the reason). GUI apps are platform-only items (`app:<name>`, component `gui-apps`). New choices go in `catalog.toml` (all OSes) or the platform toml (one OS), with a `component`. Keep OS-neutral guidance in this file and prose caveats in the `.md` files. Run `python3 scripts/validate.py` before committing; it fails on a tool missing from a platform file. Never commit secrets (the gitleaks hook enforces it).

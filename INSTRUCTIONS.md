# Dev environment setup: instructions for an LLM

You are an agent (Claude Code) with a shell on a machine that needs a dev environment: languages, CLI tools, shell, git defaults. Claude Code is already installed; do not install it. This file is the source of truth. `catalog.toml` says WHAT must exist; `platforms/<os>.md` says HOW per OS. If the user says "dry run", print the plan and change nothing.

## Rules
- Idempotent: check what exists first (`catalog.toml` `check` commands); skip what is present and good enough.
- Never overwrite without a backup: move the file to `<name>.bak.<YYYYMMDD-HHMMSS>` first.
- Never write secrets, tokens or machine-specific values into this repo. Per-machine values go in untracked local files (`~/.zshrc.local`, `$PROFILE.local.ps1`).
- Ask before: `sudo`/elevation, adding third-party package repos, remote installers (`curl | sh`, `irm | iex`), changing OS settings, and anything outside this repo and the user's home.
- Prefer the best install method per tool and OS: the platform's package manager when it is current and maintained, the official upstream installer or repo when it is not. Small version drift between OSes is fine. Pin only where `catalog.toml` has `pin`.
- Verify a package ID or name before installing it (`brew info`, `winget show`, `apt-cache policy`, ...). The platform files are hints, not guarantees.
- Report failures plainly, continue with independent steps, end with a checklist: installed / already present / skipped / manual.

## 1. Get the repo and detect the platform
If the current directory is not a checkout of this repo and `~/dev/dev-setup` does not exist: `git clone https://github.com/AnisAbdellatif/dev-setup.git ~/dev/dev-setup` and work from there (Windows: `$HOME\dev\dev-setup`). The platform files and dotfiles must be local.

Detect the OS (`uname -s` → Darwin / Linux; Windows: `$env:OS` or `ver`), then read exactly one platform file: `platforms/macos.md`, `platforms/linux.md` (determine the distro from `/etc/os-release`; WSL counts as Linux), `platforms/windows.md`. It tells you how to obtain the package manager and what to install it with.

## 2. Choose what to install (ask first)
Ask the user: everything, a preset, or pick components. Use AskUserQuestion if available, else a numbered list.
- Presets:
  - `full`: every component for the platform.
  - `minimal`: `core`, `shell`.
  - `server`: headless box: `core`, `shell`, `python`, `node`, `rust`, `bun`, `containers`, `native-build`; no GUI apps, `docs`, `reverse-eng`, `os-defaults`.
  - `custom`: user ticks components.
- Components are the `component` values in `catalog.toml` plus the platform-only ones in the platform file (`gui-apps`, `os-defaults`).
- Record the answer: write `~/.config/dev-setup/selection.json` as `{"skip": ["<component>", ...]}` listing every component NOT chosen (same path on all OSes). Re-read it on later runs and do not re-ask.
- Skip steps whose component is not selected, and prerequisites only they need.

## 3. Install
Order: platform prerequisites and package manager (platform file) → `core` → `shell` → `native-build` → languages → the rest. For each selected tool in `catalog.toml`: run `check`; if it passes and meets `min`/`pin`, skip; else install with the method in the platform file. Re-run `check` afterwards. A tool whose platform entry says `n/a` is skipped with a note, not an error.

Languages (details per OS in the platform file):
- **Python:** only `uv`. Install Pythons and CLIs with `uv python install` / `uv tool install`; do not add `pipx`, `pyenv` or `conda`. Prefer the OS Python only as a system dependency.
- **Node:** current LTS from the platform's best source. A version manager is optional; ask before adding one (mise or fnm). Global npm tools used by Claude Code setups live in agentic-setup, not here.
- **Rust:** official `rustup` (not a distro `rustc`), default toolchain `stable`, then ask whether to add cross targets: `aarch64-apple-darwin x86_64-apple-darwin aarch64-pc-windows-msvc x86_64-pc-windows-msvc aarch64-unknown-linux-musl x86_64-unknown-linux-musl` (`rustup target add ...`; skip the host's own). Write `~/.cargo/config.toml` with `[build] target-dir = "<absolute $HOME>/.cache/cargo-target"` (absolute path, one shared target dir for all projects and git worktrees; Windows: `%USERPROFILE%\.cache\cargo-target`). Create the config only if absent; if present, show a diff and ask. Optional: `cargo install cargo-sweep`.
- **Bun, Deno, Go, Java (OpenJDK 21), Ruby (+ `gem install kamal`):** per the platform file. After installing Java on macOS/Linux, `JAVA_HOME` goes in `~/.zshrc.local`, not the shared dotfiles.

## 4. Dotfiles
`dotfiles/` is applied by linking (macOS/Linux) or copying (Windows, unless Developer Mode allows symlinks; then link). Back up existing files first, show a diff, ask. Never apply a file wholesale if the existing one has content the repo lacks: merge by hand and tell the user.
- `dotfiles/common/gitconfig` → included from `~/.gitconfig` via `[include] path = ...` (keeps `user.name`/`user.email` and credentials out of the repo; ask the user for those and write them to `~/.gitconfig` itself).
- Unix: `dotfiles/unix/zshenv` → `~/.zshenv`, `dotfiles/unix/zshrc` → `~/.zshrc`. Machine specifics go in `~/.zshrc.local` (sourced last; never in the repo): `JAVA_HOME`, `SSH_AUTH_SOCK`, Android/Flutter paths, work proxies.
- Windows: `dotfiles/windows/profile.ps1` is dot-sourced from `$PROFILE`; machine specifics in `$PROFILE.local.ps1` next to it.
- The prompt is `starship` everywhere. oh-my-zsh / powerlevel10k are optional personal extras: install only if the user asks, the zshrc detects them.

## 5. Git defaults
- `git config --global init.defaultBranch main` (new repos use `main`).
- If `gh` is installed and the user is (or becomes) logged in: `gh auth login`, then `gh auth setup-git` for the credential helper. Auth is interactive: tell the user, do not handle tokens.
- Secret scan for repos: every repo of the user has `.githooks/pre-commit` running `gitleaks git --pre-commit --staged --redact --no-banner .` and `git config core.hooksPath .githooks`. Do this for this repo after cloning.

## 6. Platform-only parts
Follow the platform file for `gui-apps` and `os-defaults`. Both default to off in `custom` and are asked individually: they change the user's desktop.

## 7. Verify
For every selected tool run its `check` and report `ok <id> <version>` / `MISSING <id>: <fix>` / `WARN <id>: <note>`. Also verify: `git config --global init.defaultBranch` is `main`, the shell starts without errors (`zsh -i -c exit`, `pwsh -NoProfile -Command exit`), `core.hooksPath` is set in this repo. Finish with the checklist from Rules.

## 8. Snapshot / drift (when the user adds or removes tools)
Compare the machine with the catalog: dump the live state (macOS `brew leaves; brew list --cask`; Windows `winget list`, `scoop list`; Linux the package manager's manually-installed list; plus `uv tool list`, `cargo install --list`, `npm ls -g --depth=0`, `bun pm ls -g`, `rustup show`). Report tools that are installed but not in the catalog or platform file, and the reverse. Propose edits; apply them only after the user agrees.

## 9. Relationship to agentic-setup
`agentic-setup` configures Claude Code itself (CLAUDE.md, settings, plugins, skills). This repo installs the machine underneath it. Run this repo first on a new machine; agentic-setup's prerequisites (`git`, `jq`, `node`, `uv`, `bun`, `gitleaks`, `typst`, `d2`) are all in `catalog.toml`. A tool Claude needs is installed here; agentic-setup only checks that it exists.

## 10. Maintaining this repo
When the user installs a dev tool they want on every machine, add it to `catalog.toml` (id, component, check, why) and to every platform file (a real install method, or `n/a` with the reason). Keep OS-neutral guidance here and OS-specific commands in `platforms/`. A tool a platform cannot do is recorded as `n/a`, never silently omitted. Run Section 8 after big changes to catch drift. Never commit secrets (the gitleaks hook enforces it).

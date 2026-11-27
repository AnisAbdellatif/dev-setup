# macOS

Read after INSTRUCTIONS.md §1. Apple Silicon assumed (`/opt/homebrew`); on Intel brew lives in `/usr/local`. Package IDs are Homebrew names; confirm with `brew info <name>` before installing.

## Prerequisites
1. Command Line Tools: `xcode-select -p` || `xcode-select --install` (GUI prompt; tell the user to accept, then re-check). Full Xcode is only needed for iOS/macOS app work (ask).
2. Homebrew: `command -v brew` || official installer from https://brew.sh (`curl | bash`: ask first). Then `eval "$(/opt/homebrew/bin/brew shellenv)"` for this session; `dotfiles/unix/zshenv` makes it permanent.
3. Never mix: install CLI tools with brew, language toolchains as noted below.

## Install map (id → command)
| id | install | note |
|---|---|---|
| git gh jq ripgrep fd fzf curl gitleaks | `brew install <id>` | macOS ships old git/curl; brew versions win |
| zoxide starship fastfetch btop | `brew install <id>` | |
| uv | `brew install uv` | |
| node | `brew install node` (current) or `node@<lts>` if the user wants LTS | `catalog.toml` pin says LTS: prefer `node@<lts>` and `brew link` it, or ask |
| bun | `brew install oven-sh/bun/bun` | |
| deno | `brew install deno` | |
| rustup, cargo | official `rustup-init` (`curl https://sh.rustup.rs`, ask first); do not `brew install rust` | `. "$HOME/.cargo/env"` is in the zshenv |
| go | `brew install go` | |
| java | `brew install openjdk@21` | set `JAVA_HOME=$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home` in `~/.zshrc.local` |
| ruby, kamal | `brew install ruby`, then `gem install kamal` | brew ruby is keg-only: put `$(brew --prefix ruby)/bin` first in PATH via `~/.zshrc.local` |
| docker | cask `orbstack` (`brew install --cask orbstack`) | provides the `docker` CLI and engine; open the app once |
| cc | Command Line Tools | |
| cmake lld | `brew install cmake lld` | |
| make | Command Line Tools | |
| typst d2 tesseract | `brew install typst d2 tesseract` | |
| radare2 qemu squashfs | `brew install radare2 qemu squashfs` | `unsquashfs` comes from `squashfs` |
| 7zip | `brew install sevenzip` | binary `7zz` |
| actionlint | `brew install actionlint` | |

## Platform-only components
**gui-apps** (ask which; each `brew install --cask <name>`): `ghostty`, `rectangle`, `betterdisplay`, `inkscape`, `middleclick`, `motrix`, `background-music`, `t3-code@nightly`, `opencode-desktop`, `mactex-no-gui`, `xquartz`. Personal taps (add only if the user wants them): `anisabdellatif/tap` (cometdesk, parabole, salatwidget), `viceverse-cz/serein`. `mas` (`brew install mas`) for App Store apps.

**os-defaults** (off by default, ask per item, show the `defaults write` command first): key repeat, Finder show extensions, Dock autohide. Nothing here is required by the rest.

## Shell and services
- Shell is zsh (default). `dotfiles/unix/`. Make `.zshenv` the place for PATH-critical lines (non-interactive shells, hooks and `ssh` read only it).
- Background services use launchd agents in `~/Library/LaunchAgents`. Nothing in this repo needs one.

## Notes
- Sandboxed agents cannot write outside the project; if installs fail with "Operation not permitted", say so instead of working around it.
- Drift: `brew leaves`, `brew list --cask`, `brew tap`, `brew bundle dump --file=- --describe`.

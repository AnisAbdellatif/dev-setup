# macOS

Read after INSTRUCTIONS.md §1. The install map and OS choices are in `macos.toml` (this file is prose only). Apple Silicon assumed (`/opt/homebrew`); on Intel brew lives in `/usr/local`. Confirm a brew name with `brew info <name>` before installing.

## Prerequisites
1. Command Line Tools: `xcode-select -p` || `xcode-select --install` (GUI prompt; tell the user to accept, then re-check). Full Xcode is only needed for iOS/macOS app work (ask).
2. Homebrew: `command -v brew` || official installer from https://brew.sh (`curl | bash`: ask first). Then `eval "$(/opt/homebrew/bin/brew shellenv)"` for this session. Making it permanent (`~/.zprofile`/`~/.zshenv`) is a shell-config line for the user to add (the brew installer prints it).
3. Install CLI tools with brew; language toolchains as the `install` field says (rustup is the official installer, not brew).

## Notes
- Shell is zsh (default). Keep PATH-critical lines in `.zshenv` (non-interactive shells, hooks and `ssh` read only it).
- Background services use launchd agents in `~/Library/LaunchAgents`. Nothing in this repo needs one.
- OS settings are choices in `macos.toml` (`apply` holds the `defaults write` command): show it to the user, run only what they ticked.
- A sandboxed agent cannot write outside the project; if installs fail with "Operation not permitted", say so instead of working around it.
- Drift: `brew leaves`, `brew list --cask`, `brew tap`, `brew bundle dump --file=- --describe`.

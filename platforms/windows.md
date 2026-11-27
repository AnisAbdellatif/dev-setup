# Windows (native)

Read after INSTRUCTIONS.md §1. The install map and OS choices are in `windows.toml` (this file is prose only). Native Windows 10/11, not WSL (for WSL follow `linux.md`). Claude Code already runs here, so Git for Windows (and Git Bash) exists. Commands are PowerShell. The winget IDs in `windows.toml` were written from memory: confirm each with `winget show --id <id> -e` (or `winget search`) before installing, and fix the file if one is wrong.

## Prerequisites
1. `winget --version` (ships with Windows 11 / App Installer). If missing, install "App Installer" from the Microsoft Store (tell the user).
2. Scoop only if a selected item needs it (`install` starting with `scoop`): `Get-Command scoop` || `irm get.scoop.sh | iex` (ask first; no admin needed). The `scoop` item in the menu covers it.
3. Execution policy is a choice (`win-execution-policy`): apply only if ticked. Check first with `Get-ExecutionPolicy -Scope CurrentUser`.
4. Developer Mode (Settings → For developers) enables unprivileged symlinks. Without it, dotfiles are copied, not linked (INSTRUCTIONS §5).
5. Prefer user-scope installs (`--scope user`) where the package supports it; otherwise it needs elevation: ask.
6. PATH changes apply to new shells only; re-run each `check` in a fresh `pwsh -NoProfile`.

## Notes
- PowerShell 7 (`pwsh` item) is preferred over Windows PowerShell 5.1. There are no Windows dotfiles yet (the Dotfiles repo is zsh only); tell the user the `starship init powershell` / `zoxide init powershell` lines for their `$PROFILE` if they installed those. For persistent PATH edits use `[Environment]::SetEnvironmentVariable("Path", ..., "User")` (ask), because hooks and tools read the user environment, not the profile.
- Line endings: the `win-autocrlf` choice (`keep` leaves Git for Windows' default). Long paths are enabled by the shared gitconfig.
- GUI apps: only Windows Terminal is listed; if the user wants others (editors, browsers), find the winget ID, verify it and offer it.
- OS settings are choices in `windows.toml` (`apply` holds the command): show it, run only what the user ticked.
- Drift: `winget list`, `scoop list`, `uv tool list`, `cargo install --list`.

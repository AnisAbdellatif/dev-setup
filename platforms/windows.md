# Windows (native)

Read after INSTRUCTIONS.md §1. Native Windows 10/11, not WSL (for WSL follow `platforms/linux.md`). Claude Code already runs here, so Git for Windows (and Git Bash) exists. Commands below are PowerShell. IDs are winget package IDs, written from memory: always confirm with `winget show --id <id> -e` (or `winget search`) before installing, and fix this file if an ID is wrong.

## Prerequisites
1. `winget --version` (ships with Windows 11 / App Installer). If missing, install "App Installer" from the Microsoft Store (tell the user).
2. Scoop for CLIs winget lacks: `Get-Command scoop` || `irm get.scoop.sh | iex` (ask first; no admin needed). Add the `extras` bucket only if needed.
3. Execution policy for the user's profile script: `Get-ExecutionPolicy -Scope CurrentUser`; if `Restricted`, ask, then `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
4. Developer Mode (Settings → For developers) enables unprivileged symlinks. Without it, dotfiles are copied, not linked (INSTRUCTIONS §4).
5. Prefer user-scope installs: `winget install --id <id> -e --scope user` where the package supports it; otherwise it needs elevation: ask.
6. After an install, PATH changes apply to new shells only; re-run the `check` in a fresh `pwsh -NoProfile`.

## Install map (id → command)
| id | install | note |
|---|---|---|
| git | already present (Git for Windows) | update with `winget upgrade --id Git.Git` if old |
| gh | `winget install --id GitHub.cli -e` | |
| jq | `winget install --id jqlang.jq -e` | |
| ripgrep | `winget install --id BurntSushi.ripgrep.MSVC -e` | |
| fd | `winget install --id sharkdp.fd -e` | |
| fzf | `winget install --id junegunn.fzf -e` | |
| curl | built in (`curl.exe`, not the PowerShell alias) | check with `curl.exe --version` |
| gitleaks | `winget install --id Gitleaks.Gitleaks -e` or `scoop install gitleaks` | |
| zoxide | `winget install --id ajeetdsouza.zoxide -e` | |
| starship | `winget install --id Starship.Starship -e` | needs a Nerd Font for icons (ask) |
| fastfetch | `winget install --id Fastfetch-cli.Fastfetch -e` | |
| btop | `scoop install btop` (or `winget install --id aristocratos.btop4win -e`) | |
| uv | `winget install --id astral-sh.uv -e` | |
| node | `winget install --id OpenJS.NodeJS.LTS -e` | |
| bun | `winget install --id Oven-sh.Bun -e` | |
| deno | `winget install --id DenoLand.Deno -e` | |
| rustup, cargo | `winget install --id Rustlang.Rustup -e` (installs the MSVC toolchain; needs the C++ Build Tools below) | |
| go | `winget install --id GoLang.Go -e` | |
| java | `winget install --id Microsoft.OpenJDK.21 -e` | |
| ruby, kamal | `winget install --id RubyInstallerTeam.RubyWithDevKit.3.4 -e` (pick current), then `gem install kamal` | Kamal on native Windows is poor; suggest WSL for deploys |
| docker | `winget install --id Docker.DockerDesktop -e` (needs WSL2/Hyper-V, elevation, reboot) or Docker Engine inside WSL | ask which |
| cc | `winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"` | check: `cl` works only in a "Developer PowerShell"; instead check `where.exe link` after `vswhere`, or run `rustc --version` and a trivial `cargo build` |
| cmake | `winget install --id Kitware.CMake -e` | |
| make | n/a | prefer `cmake`/`just`; `scoop install make` if a project needs it |
| lld | `winget install --id LLVM.LLVM -e` (provides `lld-link`) | `ld.lld` check does not apply: use `lld-link --version` |
| typst | `winget install --id Typst.Typst -e` | |
| d2 | `winget install --id Terrastruct.D2 -e` | |
| tesseract | `winget install --id UB-Mannheim.TesseractOCR -e` | not added to PATH by default: add it |
| radare2 | `scoop install radare2` | |
| qemu | `winget install --id SoftwareFreedomConservancy.QEMU -e` | |
| 7zip | `winget install --id 7zip.7zip -e` | binary is `7z.exe`; may need PATH |
| squashfs | n/a | use WSL for squashfs extraction |
| actionlint | `scoop install actionlint` | |

## Platform-only components
- **gui-apps:** ask what the user wants (Windows Terminal is built into 11; editors, browsers, Inkscape, etc.) and install via winget.
- **os-defaults:** show hidden files / file extensions: `Set-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced HideFileExt 0`. Off by default, ask first.

## Shell
PowerShell 7 (`winget install --id Microsoft.PowerShell -e`) is preferred over Windows PowerShell 5.1. `dotfiles/windows/profile.ps1` is dot-sourced from `$PROFILE`; machine specifics in `$PROFILE.local.ps1`. Hooks and tools that read only the user environment need PATH set there, not only in the profile: use `[Environment]::SetEnvironmentVariable("Path", ..., "User")` for persistent PATH edits (ask).

## Notes
- Line endings: `git config --global core.autocrlf input` for repos with shell scripts (ask; Git for Windows defaults to `true`).
- Long paths: `git config --global core.longpaths true`.
- Drift: `winget list`, `scoop list`, `uv tool list`, `cargo install --list`.

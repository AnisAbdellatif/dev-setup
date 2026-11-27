# Linux

Read after INSTRUCTIONS.md §1. The distro is the agent's call: read `/etc/os-release` (`ID`, `ID_LIKE`), pick that distro's package manager, and reason about it yourself. Debian/Ubuntu names appear below only as a starting hint. WSL is Linux: follow this file inside it, and note that the Windows side is `platforms/windows.md`.

## Prerequisites
1. Confirm you can elevate: `sudo -n true`. If it needs a password, ask the user (never read or store it); if unavailable, install what you can in the home directory (user-local installers) and list the rest as manual.
2. Refresh package metadata (`apt update`, `dnf makecache`, `pacman -Sy`, ...). Ask before `sudo`.
3. Install a build baseline (the `native-build` component): `build-essential` (Debian), `@development-tools` (Fedora), `base-devel` (Arch), plus `curl`, `ca-certificates`, `pkg-config`, `libssl-dev`-style headers if Rust or native modules need them.

## Choosing the install source, per tool
Decide in this order, and prefer the newest maintained one:
1. The distro package, if its version is current enough (check with `apt-cache policy`, `dnf info`, `pacman -Si`).
2. The tool's official repo or installer (listed below), when the distro package is old or missing.
3. Homebrew on Linux only as a last resort and only if the user already uses it or agrees; it duplicates the system package manager.
Adding a third-party repo needs the user's OK each time.

## Install hints (id → where it is usually best from)
| id | usual best source |
|---|---|
| git curl jq ripgrep fd fzf make cmake | distro (`fd-find` on Debian, binary `fdfind`: symlink to `fd` in `~/.local/bin`) |
| gh | official GitHub CLI apt/dnf repo (distro copy is usually old) |
| gitleaks | GitHub release binary or distro/Homebrew if current |
| zoxide starship fastfetch btop | distro if recent, else official installer or release binary into `~/.local/bin` |
| uv | official installer (`curl -LsSf https://astral.sh/uv/install.sh | sh`, ask first); distro uv is usually stale |
| node | NodeSource / distro `nodejs` only if LTS-current, else the official binary tarball or a version manager (ask) |
| bun deno | official installers (`bun.sh/install`, `deno.land/install.sh`); ask first |
| rustup, cargo | official `rustup-init` (`sh.rustup.rs`); never the distro `rustc` for the main toolchain |
| go | official tarball from go.dev (distro Go is typically old), extract to `/usr/local/go` or `~/.local/go` |
| java | distro `openjdk-21-jdk` (or equivalent); set `JAVA_HOME` in `~/.zshrc.local` |
| ruby, kamal | distro ruby (or `ruby-install`), then `gem install kamal` (`--user-install` if no root) |
| docker | official Docker Engine repo for the distro (docs.docker.com/engine/install); then ask about adding the user to the `docker` group (it is root-equivalent) or rootless mode |
| cc lld | distro (`clang`, `lld`) |
| typst d2 | official release binary / installer; distro packages are rare or old |
| tesseract | distro (`tesseract-ocr`) |
| radare2 qemu squashfs | distro (`radare2`, `qemu-system-x86`, `squashfs-tools`) |
| 7zip | distro (`7zip` or `p7zip-full`); binary may be `7z`, `7zz` or `7za`: adjust the check |
| actionlint | release binary |

## Platform-only components
- **gui-apps:** desktop-dependent (X11/Wayland, headless servers have none). Ask what the user wants (terminal, browser, editor) and use the distro's package, Flatpak or AppImage. Skip entirely on headless machines.
- **os-defaults:** not applicable. Skip.

## Shell and services
- Shell: zsh if the user wants the repo's zsh dotfiles (`apt install zsh`, then `chsh -s "$(command -v zsh)"` with the user's OK). Otherwise bash: tell the user `dotfiles/unix/zshenv`'s PATH lines belong in `~/.profile`/`~/.bashrc`, and add them there.
- Non-interactive shells (SSH commands, Claude Code hooks) read only `~/.zshenv` (zsh) or `~/.profile`/`~/.bash_profile` (bash): keep PATH there.
- Background services: systemd user units (`~/.config/systemd/user/`, `systemctl --user enable --now`). Nothing in this repo needs one.

## Notes
- Immutable/atomic distros (Silverblue, NixOS, SteamOS): do not layer system packages without asking; prefer toolbox/distrobox or the user-local installers, and tell the user.
- Drift: the package manager's manually-installed list (`apt-mark showmanual`, `dnf history userinstalled`, `pacman -Qqe`).

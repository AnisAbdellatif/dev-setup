# Linux

Read after INSTRUCTIONS.md §1. Install hints and OS choices are in `linux.toml` (this file is prose only). The distro is the agent's call: read `/etc/os-release` (`ID`, `ID_LIKE`), pick that distro's package manager, and reason about it yourself. WSL is Linux: follow this file inside it; the Windows side is `windows.md`.

## Prerequisites
1. Confirm you can elevate: `sudo -n true`. If it needs a password, ask the user (never read or store it); if unavailable, install what you can in the home directory (user-local installers) and list the rest as manual.
2. Refresh package metadata (`apt update`, `dnf makecache`, `pacman -Sy`, ...). Ask before `sudo`.
3. Install a build baseline (the `native-build` component): `build-essential` (Debian), `@development-tools` (Fedora), `base-devel` (Arch), plus `curl`, `ca-certificates`, `pkg-config` and the TLS headers Rust or native modules need.

## Choosing the install source, per tool
In this order, preferring the newest maintained one:
1. The distro package, if its version is current enough (`apt-cache policy`, `dnf info`, `pacman -Si`).
2. The tool's official repo or installer (the `install` or `hint` field in `linux.toml`), when the distro package is old or missing.
3. Homebrew on Linux only as a last resort, and only if the user already uses it or agrees.
Adding a third-party repo needs the user's OK each time.

## Notes
- Shell: zsh if the user chose the repo's zsh dotfiles. Otherwise bash: put the PATH lines of `dotfiles/unix/zshenv` in `~/.profile` / `~/.bashrc` and tell the user.
- Non-interactive shells (SSH commands, Claude Code hooks) read only `~/.zshenv` (zsh) or `~/.profile` / `~/.bash_profile` (bash): keep PATH there.
- Choices `docker-group`, `docker-rootless`, `change-shell` are the user's call; never apply them unticked. The docker group is root-equivalent.
- GUI apps depend on the desktop (X11/Wayland); headless boxes have none. There are no GUI items in `linux.toml`: if the user wants some, find the distro package, Flatpak or AppImage and offer it.
- Background services: systemd user units (`~/.config/systemd/user/`, `systemctl --user enable --now`). Nothing in this repo needs one.
- Immutable/atomic distros (Silverblue, NixOS, SteamOS): do not layer system packages without asking; prefer toolbox/distrobox or the user-local installers, and tell the user.
- Drift: the package manager's manually-installed list (`apt-mark showmanual`, `dnf history userinstalled`, `pacman -Qqe`).

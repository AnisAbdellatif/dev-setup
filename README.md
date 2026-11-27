# dev-setup
A cross-platform (macOS, Linux, native Windows) dev environment, set up by an LLM agent following [`INSTRUCTIONS.md`](INSTRUCTIONS.md). Claude Code must already be installed on the machine.

## What's in it
- `INSTRUCTIONS.md`: the flow the agent follows (detect OS, interview, install, dotfiles, verify, drift check).
- `catalog.toml`: what should exist (tool ids, check commands, component groups). No install commands.
- `platforms/{macos,linux,windows}.md`: how to install each tool per OS, with the best method per tool. Linux leaves the distro to the agent.
- `dotfiles/`: git config, zsh (macOS/Linux) and PowerShell profile. Machine specifics stay out, in `~/.zshrc.local` / `$PROFILE.local.ps1`.
- `.githooks/pre-commit`: gitleaks scan.

## Deploy
```
claude "Set up this machine by following https://raw.githubusercontent.com/AnisAbdellatif/dev-setup/main/INSTRUCTIONS.md"   # add "dry run" to preview
```
The agent clones this repo to `~/dev/dev-setup` and asks which components to install (presets: `full`, `minimal`, `server`, `custom`).

## Make it yours
Fork it, replace the `AnisAbdellatif` URLs, edit `catalog.toml`, the platform files and `dotfiles/`. Read `INSTRUCTIONS.md` first: it installs software and runs shell commands on your machine. Windows package IDs and the Linux hints were written without a Windows/Linux machine to test on; the agent is told to verify each before installing.

Companion repo: [agentic-setup](https://github.com/AnisAbdellatif/agentic-setup) configures Claude Code itself. Run this one first on a new machine.

## License
[MIT](LICENSE).

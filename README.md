# dev-setup
A cross-platform (macOS, Linux, native Windows) dev environment, set up by an LLM agent following [`INSTRUCTIONS.md`](INSTRUCTIONS.md). Claude Code must already be installed on the machine.

## What's in it
- `INSTRUCTIONS.md`: the flow the agent follows (detect OS, selection, install, dotfiles, verify, drift check).
- `catalog.toml`: what can exist (tools with check commands, components, presets, shared choices). No install commands.
- `platforms/{macos,linux,windows}.toml`: how to install each tool per OS (best method per tool), GUI apps and OS-specific choices. `.md` next to them: prerequisites and caveats. Linux leaves the distro to the agent.
- `scripts/choose.py`: optional TUI (`uv run scripts/choose.py`, run it in your own terminal) where you pick presets, every tool and app, OS choices and git identity; it writes `~/.config/dev-setup/selection.json` for the agent. The tool list scrolls and filters as you type (space toggles, Ctrl-A all shown, Ctrl-G whole group, Enter done, Esc cancels). On Windows use PowerShell or Windows Terminal, not Git Bash. Without it the agent offers the same menu in chat.
- `scripts/validate.py`: stdlib check of the data files and of a selection file.
- Dotfiles are not here: they live in the separate [Dotfiles](https://github.com/AnisAbdellatif/Dotfiles) repo, which the agent checks out into `$HOME` (macOS/Linux) after installing the shell tools they need (oh-my-zsh, powerlevel10k, zsh plugins, a Nerd Font).
- `.githooks/pre-commit`: gitleaks scan.

## Deploy
```
claude "Set up this machine by following https://raw.githubusercontent.com/AnisAbdellatif/dev-setup/main/INSTRUCTIONS.md"   # add "dry run" to preview
```
The agent clones this repo to `~/dev/dev-setup` (or, with no `git`, downloads the repo as a tar/zip archive into a temp folder; no manual clone or download), then offers to open the TUI or to pick in chat (presets: `full`, `minimal`, `server`, `custom`). Everything is offered; nothing is installed before you approve the plan.

## Make it yours
Fork it, replace the `AnisAbdellatif` URLs, edit `catalog.toml` and `platforms/*.toml` (and point `dotfiles-url` at your own dotfiles repo), then run `python3 scripts/validate.py`. Read `INSTRUCTIONS.md` first: it installs software and runs shell commands on your machine. Windows package IDs and the Linux hints were written without a Windows/Linux machine to test on; the agent is told to verify each before installing.

Companion repo: [agentic-setup](https://github.com/AnisAbdellatif/agentic-setup) configures Claude Code itself. Run this one first on a new machine.

## License
[MIT](LICENSE).

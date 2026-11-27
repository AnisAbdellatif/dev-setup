# Dot-sourced from $PROFILE:   . "$HOME\dev\dev-setup\dotfiles\windows\profile.ps1"
# Persistent PATH belongs in the User environment (winget does that); this is interactive-only.
# Machine specifics: $PROFILE.local.ps1 (never committed).

if (Get-Command zoxide -ErrorAction SilentlyContinue) {
  Invoke-Expression (& { (zoxide init powershell | Out-String) })
}
if (Get-Command starship -ErrorAction SilentlyContinue) {
  Invoke-Expression (&starship init powershell)
}
if (Get-Command fastfetch -ErrorAction SilentlyContinue) { fastfetch }

$local = "$PROFILE.local.ps1"
if (Test-Path $local) { . $local }

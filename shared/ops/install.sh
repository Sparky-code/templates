#!/usr/bin/env bash
# Install (or reinstall) the launchd agent for {{ project_name }}.
#   ops/launchd/install.sh            install and load
#   ops/launchd/install.sh --remove   unload and remove
# Compatible with bash 3.2 (the macOS default).
set -euo pipefail

label="local.{{ project_name }}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
target="$HOME/Library/LaunchAgents/$label.plist"
domain="gui/$(id -u)"

launchctl bootout "$domain/$label" 2>/dev/null || true
if [[ "${1:-}" == "--remove" ]]; then
  rm -f "$target"
  echo "removed $label"
  exit 0
fi

[[ -f "$repo/.env" ]] || { echo "create $repo/.env first (copy .env.example)" >&2; exit 1; }
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs/{{ project_name }}"
sed -e "s#__REPO__#$repo#g" -e "s#__HOME__#$HOME#g" \
  "$repo/ops/launchd/$label.plist" >"$target"
plutil -lint "$target" >/dev/null
launchctl bootstrap "$domain" "$target"
echo "installed $label; logs in ~/Library/Logs/{{ project_name }}/"

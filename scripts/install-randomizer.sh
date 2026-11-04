#!/bin/bash
# Explicit opt-in: omarchy theme install does not execute repository scripts.
set -euo pipefail
scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_dir="${OMARCHY_PATH:-/usr/share/omarchy}/shell/plugins/background"
plugin="$HOME/.config/omarchy/plugins/crows.background"
case "${1:-}" in
  --remove)
    # Keep the files for easy recovery; disabling the clone restores its source.
    omarchy plugin disable crows.background
    exit
    ;;
  '') ;;
  *) echo "Usage: $0 [--remove]" >&2; exit 2 ;;
esac
for dependency in python3 omarchy omarchy-shell; do
  command -v "$dependency" >/dev/null || { echo "Missing dependency: $dependency" >&2; exit 1; }
done
[[ -f $source_dir/Background.qml ]] || {
  echo 'This add-on requires the Omarchy shell background plugin (Quickshell). Older swaybg/swww installations are not changed.' >&2
  exit 1
}
# Do not enable two replacements for the same built-in IPC target.
python3 - <<'CHECK'
import json
from pathlib import Path
root = Path.home() / '.config/omarchy'
config_file = root / 'shell.json'
config = json.loads(config_file.read_text()) if config_file.exists() else {}
disabled = config.get('disabledPlugins', [])
for entry in config.get('plugins', []):
    plugin_id = entry if isinstance(entry, str) else entry.get('id', '')
    if plugin_id in disabled or plugin_id == 'crows.background':
        continue
    manifest = root / 'plugins' / plugin_id / 'manifest.json'
    if manifest.exists():
        metadata = json.loads(manifest.read_text())
        if metadata.get('omarchy', {}).get('clonedFrom') == 'omarchy.background':
            raise SystemExit('Disable your existing background clone first: ' + plugin_id)
CHECK
mkdir -p -- "$(dirname -- "$plugin")"
stage=$(mktemp -d "$(dirname -- "$plugin")/.crows-build.XXXXXX")
trap 'rm -rf -- "$stage"' EXIT
# All compatibility checks finish before replacing an installed plugin.
python3 "$scripts/build-plugin.py" "$source_dir" "$stage/plugin"
if [[ -e $plugin ]]; then
  backup="$plugin.backup-$(date +%Y%m%d-%H%M%S)-$$"
  mv -- "$plugin" "$backup"
  echo "Previous plugin saved to $backup"
fi
mv -- "$stage/plugin" "$plugin"
omarchy-shell shell rescanPlugins >/dev/null
omarchy plugin enable crows.background
echo 'Randomizer enabled for Murder of Crows. Choose a wallpaper in the usual picker.'
echo "Disable and restore the stock renderer: bash '$scripts/install-randomizer.sh' --remove"

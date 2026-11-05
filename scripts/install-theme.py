#!/usr/bin/env python3
"""Install Murder of Crows and its theme-controlled wallpaper renderer together."""
import argparse
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
ID = 'crows.background'
KNOWN_PREVIOUS = 'sunnyoled.background'


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def enabled_clones(config):
    settings = json.loads((config / 'shell.json').read_text()) if (config / 'shell.json').exists() else {}
    disabled = settings.get('disabledPlugins', [])
    found = []
    for entry in settings.get('plugins', []):
        plugin_id = entry if isinstance(entry, str) else entry.get('id', '')
        if plugin_id in disabled or plugin_id == ID:
            continue
        manifest = config / 'plugins' / plugin_id / 'manifest.json'
        if manifest.exists() and json.loads(manifest.read_text()).get('omarchy', {}).get('clonedFrom') == 'omarchy.background':
            found.append(plugin_id)
    return found


def main(remove=False):
    home = Path.home()
    config = home / '.config/omarchy'
    plugin = config / 'plugins' / ID
    state = home / '.local/state/omarchy/murder-of-crows-integration.json'
    previous = json.loads(state.read_text()) if state.exists() else {'previousRenderers': []}
    if remove:
        run('omarchy', 'plugin', 'disable', ID)
        for plugin_id in previous.get('previousRenderers', []):
            run('omarchy', 'plugin', 'enable', plugin_id)
        print('Built-in wallpaper integration disabled; previous renderer restored. Theme retained.')
        return
    for command in ('omarchy', 'omarchy-shell'):
        if not shutil.which(command):
            raise RuntimeError('Missing required command: ' + command)
    source = Path(os.environ.get('OMARCHY_PATH', '/usr/share/omarchy')) / 'shell/plugins/background'
    if not (source / 'Background.qml').exists():
        raise RuntimeError('This theme integration requires the Omarchy Quickshell background renderer.')
    clones = enabled_clones(config)
    unknown = [item for item in clones if item != KNOWN_PREVIOUS]
    if unknown:
        raise RuntimeError('Existing custom renderer needs explicit migration: ' + ', '.join(unknown))
    if not (ROOT / 'backgrounds').is_dir():
        raise RuntimeError('Run install.sh from the complete theme checkout, including backgrounds/.')
    spec = importlib.util.spec_from_file_location('builder', SCRIPTS / 'build-plugin.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    # Complete source/compatibility checks before changing user configuration.
    with tempfile.TemporaryDirectory(prefix='crows-theme-') as temporary:
        stage = Path(temporary)
        builder.build(source, stage / 'plugin', SCRIPTS)
        target = config / 'themes/murder-of-crows'
        same_checkout = ROOT.resolve() == target.resolve()
        if not same_checkout:
            shutil.copytree(ROOT, stage / 'theme', ignore=shutil.ignore_patterns('.git', '__pycache__'))
        backup = home / '.local/state/omarchy/backups' / ('crows-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        backup.mkdir(parents=True)
        if (config / 'shell.json').exists():
            shutil.copy2(config / 'shell.json', backup / 'shell.json')
        if plugin.exists():
            shutil.copytree(plugin, backup / 'plugin')
        if not same_checkout and target.exists():
            shutil.copytree(target, backup / 'theme', symlinks=True)
        print('Backup:', backup)
        if not same_checkout:
            shutil.copytree(stage / 'theme', target, dirs_exist_ok=True)
        plugin.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage / 'plugin', plugin, dirs_exist_ok=True)
        # Preserve the already-working PU/Sunny theme using the shared renderer.
        # Its old plugin stays intact and can be restored with --remove.
        sunny = config / 'themes/sunny-oled'
        marker = sunny / 'wallpaper-randomizer.json'
        if KNOWN_PREVIOUS in clones and sunny.is_dir() and not marker.exists():
            marker.write_text('{"version": 1, "enabled": true}\n')
        previous['previousRenderers'] = sorted(set(previous.get('previousRenderers', []) + clones))
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(previous, indent=2) + '\n')
        try:
            run('omarchy-shell', 'shell', 'rescanPlugins')
            # Discovery is asynchronous; do not enable an unknown component.
            for _ in range(40):
                catalog = json.loads(run('omarchy', 'plugin', 'list', '--json'))
                if any(item.get('id') == ID for item in catalog):
                    break
                time.sleep(0.05)
            else:
                raise RuntimeError('Theme renderer was not discovered')
            for plugin_id in clones:
                run('omarchy', 'plugin', 'disable', plugin_id)
            run('omarchy', 'plugin', 'enable', ID)
            run('omarchy', 'theme', 'set', 'murder-of-crows')
        except Exception:
            # Restore renderer selection without overwriting unrelated UI settings.
            subprocess.run(['omarchy', 'plugin', 'disable', ID], capture_output=True)
            for plugin_id in previous['previousRenderers']:
                subprocess.run(['omarchy', 'plugin', 'enable', plugin_id], capture_output=True)
            raise
    print('Murder of Crows installed and active, with built-in independent wallpapers.')
    print('Use the usual wallpaper picker. Disable integration: bash install.sh --remove')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remove', action='store_true', help='restore the previous wallpaper renderer; keep theme')
    args = parser.parse_args()
    main(args.remove)

#!/usr/bin/env python3
"""Read the active theme's declarative randomizer settings and still images."""
import json
from pathlib import Path


def backgrounds(home):
    current = home / '.local/state/omarchy/current'
    try:
        theme = (current / 'theme.name').read_text().strip()
        if not theme or '/' in theme or theme in {'.', '..'}:
            return []
        settings = json.loads((current / 'theme/wallpaper-randomizer.json').read_text())
        if settings.get('version') != 1 or settings.get('enabled') is not True:
            return []
    except (OSError, ValueError, AttributeError):
        return []
    files = set()
    for directory in (current / 'theme/backgrounds',
                      home / '.config/omarchy/backgrounds' / theme):
        try:
            for path in directory.iterdir():
                if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}:
                    files.add(str(path.resolve()))
        except OSError:
            continue
    return sorted(files)


if __name__ == '__main__':
    print(json.dumps(backgrounds(Path.home())))

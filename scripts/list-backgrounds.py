#!/usr/bin/env python3
"""Return the active theme's still images; never execute paths from the theme."""
import json
from pathlib import Path


def backgrounds(home):
    current = home / '.local/state/omarchy/current'
    try:
        theme = (current / 'theme.name').read_text().strip()
    except OSError:
        return []
    if theme != 'murder-of-crows':
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

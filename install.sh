#!/bin/bash
# Install the complete theme, including its built-in multi-monitor integration.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$root/scripts/install-theme.py" "$@"

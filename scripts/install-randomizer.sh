#!/bin/bash
# Compatibility entry point: the randomizer is now part of the complete theme.
set -euo pipefail
scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec bash "$scripts/../install.sh" "$@"

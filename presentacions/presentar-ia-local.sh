#!/usr/bin/env bash
set -euo pipefail
presentation_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$presentation_dir"
exec python3 "$presentation_dir/centrar-portada.py" "$@"

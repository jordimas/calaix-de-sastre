#!/usr/bin/env bash
set -euo pipefail
presentation_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$presentation_dir"
exec presenterm "$presentation_dir/ia-local.md" "$@"

#!/usr/bin/env bash
set -euo pipefail

demo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
demo_workdir="$(mktemp -d /tmp/demo-qwen.XXXXXX)"
cd "$demo_workdir"

# Requereix Qwen CLI configurat amb el servidor local i el model carregat.
# El directori buit i --safe-mode eviten afegir el repositori i personalitzacions al prompt.
/usr/bin/time -f '\nTemps total de Qwen CLI: %e s' \
  qwen --safe-mode -m qwen3-coder-next \
  -p 'Segueix les instruccions del text rebut per stdin.' \
  -o text < "$demo_dir/demo-qwen-prompt.txt"

#!/usr/bin/env bash
set -euo pipefail
presentation_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$presentation_dir"
# Isolate presentation preferences from other Ptyxis windows.
export XDG_CONFIG_HOME="$presentation_dir/.terminal-config"
export GSETTINGS_BACKEND=keyfile
mkdir -p "$XDG_CONFIG_HOME"
gsettings set org.gnome.Ptyxis use-system-font false
gsettings set org.gnome.Ptyxis font-name 'Ubuntu Mono 28'
gsettings set org.gnome.Ptyxis restore-session false
exec ptyxis --standalone --fullscreen --title 'IA en local' -- \
  "$presentation_dir/presentar-ia-local.sh" "$@"

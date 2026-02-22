#!/usr/bin/env bash
# Create venv and install requirements. Run from project root.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

cd "$SCRIPT_DIR"

if [[ ! -f "$REQUIREMENTS" ]]; then
  echo "Error: requirements.txt not found." >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  echo "Created venv at $VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$REQUIREMENTS"
echo "Installed requirements from requirements.txt"

echo "Done. Use: $SCRIPT_DIR/search_short.sh [search_short.txt]  (uses venv automatically)"

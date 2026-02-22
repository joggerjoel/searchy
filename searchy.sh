#!/usr/bin/env bash
# Driver for search_short.py: reads search_short.txt and searches Serper API for the event
# across ticketing sites; only shows URLs when the result date matches the event date.
# Uses .venv if present (run ./setup.sh first).
# Usage: ./search_short.sh [file.txt] [--open]
#   --open  open each result URL in Google Chrome

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON="$VENV_PYTHON"
else
  PYTHON="python3"
fi

if [[ $# -eq 0 ]]; then
  set -- "search_short.txt"
fi
# Resolve file path for existence check (first arg that isn't --open)
SHORT_FILE="search_short.txt"
for a in "$@"; do
  if [[ "$a" != "--open" ]]; then
    SHORT_FILE="$a"
    break
  fi
done
if [[ ! -f "$SHORT_FILE" ]]; then
  echo "Error: File '$SHORT_FILE' not found." >&2
  exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/search_short.py" "$@"

#!/usr/bin/env bash
# Open Chrome on macOS or Windows. Usage: ./open-chrome.sh [url]

set -e

URL="${1:-}"

case "$(uname -s)" in
  Darwin)
    if [[ -n "$URL" ]]; then
      /usr/bin/open -a "Google Chrome" --new --args "$URL"
    else
      /usr/bin/open -a "Google Chrome"
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*)
    CHROME="${LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe"
    if [[ -n "$URL" ]]; then
      "$CHROME" "$URL"
    else
      "$CHROME" "about:blank"
    fi
    ;;
  *)
    echo "Unsupported OS. Use macOS or Windows." >&2
    exit 1
    ;;
esac

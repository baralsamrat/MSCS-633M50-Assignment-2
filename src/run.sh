#!/usr/bin/env bash
set -euo pipefail

# run_main.sh — Create venv, install deps, run QR generator
# Usage:
#   ./run_main.sh "https://your-url.com" [extra args]
#
# Example:
#   ./run_main.sh "https://example.com" --out qr.png --title "Biox Systems" --size 900

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <URL> [extra args]" >&2
  exit 1
fi

URL="$1"
shift || true

# Prefer python3
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

# Create venv if not exists
if [[ ! -d ".venv" ]]; then
  $PY -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Upgrade pip and install deps
pip install qrcode pillow

# Run the QR generator (expects main.py in same folder)
if [[ ! -f "main.py" ]]; then
  echo "❌ main.py not found in $(pwd)" >&2
  exit 1
fi

python main.py "$URL" "$@"
echo "✅ Done."

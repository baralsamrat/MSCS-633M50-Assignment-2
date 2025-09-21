
## ⚙️ Quick Start

### Option A — minimal install

```bash
# 1) (Recommended) use a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 2) Install deps
python -m pip install --upgrade pip
pip install qrcode pillow

# 3) Run (optimized version)
python main.py "https://your-url.com" \
  --out qr.png \
  --title "Biox Systems" \
  --subtitle "AI QR Code Generator" \
  --footer "Biox Systems • AI QR Code Generator • 1994→2025" \
  --logo path/to/logo.png \
  --size 900 \
  --border 4 \
  --pad 80
```

### Option B — macOS one-shot script

Save this file as `run.sh` (or use the copy in your repo):

```bash
#!/usr/bin/env bash
set -euo pipefail
# run.sh — Create venv (if needed), install deps, run QR generator
# Usage:
#   ./run.sh "https://your-url.com" [extra args]

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <URL> [extra args]" >&2
  exit 1
fi
URL="$1"; shift || true

PY=$(command -v python3 || command -v python)
[[ -d .venv ]] || "$PY" -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install qrcode pillow

if [[ -f main.py ]]; then
  python main.py "$URL" "$@"
else
  echo "❌ Place main.py or main.py in this folder." >&2
  exit 1
fi
echo "✅ Done."
```

Make it executable:

```bash
chmod +x run.sh
./run.sh "https://example.com" --out qr.png --title "Biox Systems"
```

---

## 🧰 CLI Options (optimized script)

```text
positional:
  url                          URL to encode into the QR code

options:
  --out qr_biox.png            Output PNG path
  --title "Biox Systems"       Title text ('' to hide)
  --subtitle "AI ..."          Subtitle text ('' to hide)
  --footer "..."               Footer text ('' to hide)
  --logo path/to/logo.png      Optional center logo (PNG with transparency)
  --dark "#000000"             Dark color of QR (hex or name)
  --light "#FFFFFF"            Background/light color (hex or name)
  --size 1024                  Target QR pixels (QR itself; canvas is larger)
  --border 4                   Quiet zone (modules) around QR
  --pad 80                     Outer canvas padding in px
```

---

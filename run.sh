#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  AI Smart Attendance System – Quick Launcher (Mac / Linux)
# ─────────────────────────────────────────────────────────────
set -e

echo ""
echo "  ⬡  AI Smart Attendance System"
echo "  ─────────────────────────────"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "  ❌  python3 not found. Install Python 3.8+ and try again."
  exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
  echo "  Creating virtual environment…"
  python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install core deps if flask missing
python -c "import flask" 2>/dev/null || {
  echo "  Installing core dependencies…"
  pip install flask pandas openpyxl numpy Pillow -q
}

# Run setup to ensure files exist
python setup.py

# Start server
echo ""
echo "  🚀  Starting server at http://127.0.0.1:5000"
echo "  Press Ctrl+C to stop."
echo ""
python app.py

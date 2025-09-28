#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3-venv
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
echo "Run: python -m uvicorn main:app --host 0.0.0.0 --port 8088"

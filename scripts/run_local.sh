#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python run_pipeline.py
PYTHONPATH=. python -m pytest -q

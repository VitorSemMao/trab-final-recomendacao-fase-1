#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install -r requirements.txt
python scripts/download_movielens_100k.py

echo "Dependencies installed and dataset prepared."

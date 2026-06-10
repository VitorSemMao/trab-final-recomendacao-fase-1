#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f "data/movielens-100k/u.item" ] || [ ! -f "data/movielens-100k/u.data" ]; then
  python scripts/download_movielens_100k.py
fi

python -m uvicorn app.main:app --reload

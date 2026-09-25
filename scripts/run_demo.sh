#!/usr/bin/env sh
set -eu

if [ ! -d .venv ]; then
  python -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python scripts/demo_seed.py
exec uvicorn app.main:app --reload

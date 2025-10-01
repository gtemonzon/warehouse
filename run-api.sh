#!/usr/bin/env bash
set -euo pipefail
if [ -f backend/.env ]; then
  export $(grep -v '^#' backend/.env | xargs) || true
fi
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

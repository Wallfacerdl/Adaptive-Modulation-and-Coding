#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/home/delongfu/miniconda3/envs/com_venv/bin/python}"

cd "$ROOT_DIR"
"$PYTHON_BIN" -m unittest tests/test_olla_policy.py tests/test_link_adaptation_integration.py

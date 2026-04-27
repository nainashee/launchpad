#!/usr/bin/env bash
# Build the auth layer with Linux-compatible wheels.
# Run from the repo root:  bash layers/auth/build.sh
#
# Uses --platform manylinux2014_x86_64 so the downloaded wheels work on
# Lambda (Amazon Linux 2) even when built on Windows or macOS.

set -euo pipefail

LAYER_DIR="$(dirname "$0")/python"

echo "Cleaning previous packages..."
# Remove everything except auth.py
find "$LAYER_DIR" -mindepth 1 ! -name "auth.py" -exec rm -rf {} + 2>/dev/null || true

echo "Installing Lambda-compatible packages into $LAYER_DIR ..."
pip install \
  --platform manylinux2014_x86_64 \
  --target "$LAYER_DIR" \
  --python-version 3.12 \
  --only-binary=:all: \
  --upgrade \
  -r "$(dirname "$0")/requirements.txt"

echo "Done. Layer contents:"
ls "$LAYER_DIR"

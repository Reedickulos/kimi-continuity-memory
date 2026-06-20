#!/bin/bash
# Run the Phase 0 wake locally and push results to GitHub.
# This is a fallback while GitHub Actions startup issues are resolved.

set -e

TOKEN=$(gh auth token)
WORKDIR=$(mktemp -d)
REPO="https://x-access-token:${TOKEN}@github.com/Reedickulos/kimi-continuity-memory.git"

echo "Cloning memory repo into ${WORKDIR}..."
git clone "${REPO}" "${WORKDIR}"
cd "${WORKDIR}"

echo "Installing dependencies..."
python3 -m pip install -q -r requirements.txt

echo "Running Phase 0 wake..."
python3 -m kimi_autonomy.phase0

echo "Cleaning up temporary clone..."
cd ..
rm -rf "${WORKDIR}"

echo "Wake complete."

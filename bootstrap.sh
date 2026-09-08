#!/usr/bin/env bash
set -euo pipefail

python3 scripts/validate_repo.py
python3 scripts/update_hashes.py --check

if [ ! -d .git ]; then
  git init
fi

git branch -M main
git add .
git status --short

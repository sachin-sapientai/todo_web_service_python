#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH_NAME="${1:-main}"
COMMIT_MSG="${2:-\"Add Django-based todo web service\"}"

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

git add .
git commit -m "$COMMIT_MSG" || echo "Nothing to commit."

echo "If not already set, add a remote with:"
echo "  git remote add origin <YOUR_GITHUB_REPO_URL>"
echo "Then push with:"
echo "  git push -u origin $BRANCH_NAME"


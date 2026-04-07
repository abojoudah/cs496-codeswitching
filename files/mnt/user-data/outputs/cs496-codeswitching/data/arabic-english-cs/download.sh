#!/usr/bin/env bash
# Download script for Arabic-English Code Switching Corpus (Kaggle 2021)
# Source: https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus
# License: Academic use only per Kaggle dataset terms

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Downloading Arabic-English CS Corpus from Kaggle..."
echo ""

# Check for kaggle CLI
if ! command -v kaggle &> /dev/null; then
  echo "The Kaggle CLI is required. Install it with:"
  echo "  pip install kaggle"
  echo ""
  echo "Then configure your API key:"
  echo "  1. Go to https://www.kaggle.com/settings/account"
  echo "  2. Click 'Create New Token' — downloads kaggle.json"
  echo "  3. Place it at ~/.kaggle/kaggle.json"
  echo "  4. chmod 600 ~/.kaggle/kaggle.json"
  echo ""
  echo "Then re-run this script."
  exit 1
fi

kaggle datasets download \
  -d islamkaloop/arabic-english-intra-word-code-switching-corpus \
  -p "$SCRIPT_DIR" \
  --unzip

echo ""
echo "Downloaded files:"
ls -lh "$SCRIPT_DIR"/*.txt "$SCRIPT_DIR"/*.csv 2>/dev/null || ls -lh "$SCRIPT_DIR"/
echo ""
echo "IMPORTANT: These files are excluded from git by .gitignore."
echo "Do not commit raw data files to the repository."
echo ""
echo "Citation:"
echo "  Islam Kaloop (2021). Arabic-English Intra-word Code Switching Corpus."
echo "  Kaggle. https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus"

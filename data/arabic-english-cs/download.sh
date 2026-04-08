#!/usr/bin/env bash
# Download script for Arabic-English CS Corpus (Kaggle 2021)
#
# OPTION 1 - Kaggle CLI:
#   1. pip install kaggle --break-system-packages
#   2. Get API key: kaggle.com -> Settings -> API -> Create New Token
#   3. mkdir -p ~/.kaggle && mv kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
#   4. bash download.sh
#
# OPTION 2 - Manual (easier for teammates):
#   1. Go to: https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus
#   2. Click Download
#   3. Unzip and place "AR-EN Intra-word CS Corpus.txt" in this folder

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v kaggle &> /dev/null; then
  echo "Kaggle CLI not found."
  echo "Please use manual download:"
  echo "https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus"
  exit 1
fi

kaggle datasets download \
  -d islamkaloop/arabic-english-intra-word-code-switching-corpus \
  -p "$SCRIPT_DIR" \
  --unzip

echo "Done."
ls -lh "$SCRIPT_DIR"

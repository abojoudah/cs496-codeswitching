#!/usr/bin/env bash
# Download script for Arabizi Dataset (WANLP 2022)
# Source: https://github.com/HaifaCLG/Arabizi
# License: Academic use (cite Shehadi & Wintner, 2022)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Downloading Arabizi Dataset (WANLP 2022)..."

if ! command -v git &> /dev/null; then
  echo "ERROR: git is required. Please install git and try again."
  exit 1
fi

# Clone into a temp folder then copy only the data files
TMP=$(mktemp -d)
git clone --depth 1 https://github.com/HaifaCLG/Arabizi "$TMP/Arabizi"

# Copy annotated data files
cp "$TMP/Arabizi/words_annotated.csv"  ./words_annotated.csv
cp "$TMP/Arabizi/sen_annotated.csv"    ./sen_annotated.csv
cp "$TMP/Arabizi/arabizi-reddit_new.zip" ./arabizi-reddit_new.zip
cp "$TMP/Arabizi/arabizi_tweet_ids_auto.csv" ./arabizi_tweet_ids_auto.csv

# Copy notebook and scripts for reference
mkdir -p ../arabizi-wanlp-scripts
cp "$TMP/Arabizi/langdetect_lstm_bert_crf.ipynb" ../arabizi-wanlp-scripts/
cp "$TMP/Arabizi/main.py"   ../arabizi-wanlp-scripts/
cp "$TMP/Arabizi/utils.py"  ../arabizi-wanlp-scripts/

rm -rf "$TMP"

echo ""
echo "Downloaded files:"
ls -lh "$SCRIPT_DIR"/*.csv "$SCRIPT_DIR"/*.zip 2>/dev/null
echo ""
echo "IMPORTANT: These files are excluded from git by .gitignore."
echo "Do not commit raw data files to the repository."
echo ""
echo "Citation:"
echo "  Shehadi & Wintner (2022). Identifying Code-switching in Arabizi."
echo "  WANLP @ ACL 2022. https://aclanthology.org/2022.wanlp-1.18"

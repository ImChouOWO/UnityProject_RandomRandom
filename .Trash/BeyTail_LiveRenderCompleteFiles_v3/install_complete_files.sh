#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "使用方式："
  echo "  ./install_complete_files.sh /Users/zhouchenghan/Desktop/iosAPP/beyblade"
  exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$SCRIPT_DIR/validate_complete_files.py" "$PROJECT_ROOT"

echo
echo "[OK] 目前專案已包含即時渲染修正"
echo "[NEXT] Xcode：Product > Clean Build Folder，然後 Command+B"

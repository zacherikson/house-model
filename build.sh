#!/usr/bin/env bash
# Rebuilds site/house.json from the plan PDF. Run from anywhere: ./build.sh
# Needs: python3 with numpy, scipy, pillow, pdfplumber  (pip install numpy scipy pillow pdfplumber)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$ROOT/source/plans/plans-review-set-2026-06-02.pdf" ]; then
  echo "Missing source/plans/plans-review-set-2026-06-02.pdf (kept out of git for privacy). Put the plans PDF there first."; exit 1
fi
mkdir -p "$ROOT/build" && cd "$ROOT/build"
cp ../pipeline/fixes/*.json .
P=../pipeline
# main floor = PDF page index 3 (sheet 5); foundation/basement = page index 2 (sheet 4)
python3 -I $P/walls.py 3 main_walls
python3 -I $P/openings.py 3 main_walls
python3 -I $P/export.py 3 main_walls main.json fix
python3 -I $P/walls_b.py bsmt
python3 -I $P/openings.py 2 bsmt
python3 -I $P/export.py 2 bsmt bsmt_export.json fix
python3 -I $P/combine.py
echo "Wrote site/house.json"

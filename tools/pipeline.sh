#!/bin/sh
# End-to-end: finalise every PT-8.0-re-saved original, build test variants of the converted files,
# and write a pttest plan for them.  Usage: sh tools/pipeline.sh <workdir with variants/ and runs/>
# Expects <workdir>/variants/PTSkills<n>_pt800.pka (from pttest --saveas) for n = 1..14.
set -e
W="$1"; R="$(cd "$(dirname "$0")/.." && pwd)"; PY="$R/.venv/bin/python"
mkdir -p "$R/build/canvas" "$W/variants" "$W/runs"
: > "$W/plan4.txt"; : > "$W/convert.log"
for o in "$R"/samples/originals/canvas/*PTSkills*.pka; do
  n=$(echo "$o" | sed -E 's/.*PTSkills([0-9]+)\.pka/\1/'); b=$(basename "$o" .pka)
  out="$R/build/canvas/${b}_v8.pka"
  "$PY" "$R/tools/convert.py" "$o" "$W/variants/PTSkills${n}_pt800.pka" "$out" >> "$W/convert.log"
  "$PY" "$R/tools/variants.py" solved "$out" "$W/variants/PTSkills${n}_v8solved.pka" > /dev/null
  cp "$out" "$W/variants/PTSkills${n}_v8.pka"
  for v in 8.0.0 9.0.1; do
    echo "$v $W/variants/PTSkills${n}_v8solved.pka $W/runs/PTSkills${n}_v8solved_${v}.json" >> "$W/plan4.txt"
    echo "$v $W/variants/PTSkills${n}_v8.pka $W/runs/PTSkills${n}_v8_${v}.json" >> "$W/plan4.txt"
  done
done
sort -k1,1 -s "$W/plan4.txt" -o "$W/plan4.txt"    # group by PT version: fewer version switches
grep -c . "$W/plan4.txt"

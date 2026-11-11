#!/bin/zsh
# Export the full-resolution iCloud Photos library to New_Data with osxphotos.
# Run weekly by launchd (com.jbakse.photos-export.plist); safe to run by hand too.
# See backup/README.md.
#
# - Photos stays on "Optimize Mac Storage"; osxphotos downloads missing originals itself.
# - Re-runs only export new or changed items (tracked in .osxphotos_export.db inside DEST).
# - Hidden photos are skipped: PhotoKit can't see the locked Hidden album, so they'd
#   always show up as "missing". Export them by hand into $DEST/_hidden. The script
#   notifies when the number of hidden photos changes.
# - Extra arguments are passed to `osxphotos export` (e.g. --from-date 2024-01-01).
set -uo pipefail

DEST="/Volumes/New_Data/iCloud Photos Export"
OSXPHOTOS="$HOME/.local/bin/osxphotos"

notify() {
  osascript -e "display notification \"$1\" with title \"Photos export\"" 2>/dev/null
  echo "NOTIFY: $1"
}

echo "=== $(date '+%F %T') photos export ==="

if [[ ! -d /Volumes/New_Data ]]; then
  echo "New_Data not mounted; skipping photos export."
  exit 0
fi

STATE="$HOME/.local/state/photos-export"   # outside New_Data: zsh under launchd can't write there
mkdir -p "$STATE"
REPORT="$DEST/_reports/export_$(date +%F).csv"
start=$(date +%Y-%m-%dT%H:%M:%S)
out=$(mktemp -t photos-export)
trap 'rm -f "$out"' EXIT

caffeinate -i "$OSXPHOTOS" export "$DEST" \
  --update \
  --download-missing --use-photokit \
  --not-shared --not-hidden \
  --directory "{created.year}/{created.mm}" \
  --sidecar xmp \
  --touch-file \
  --retry 3 \
  --report "$DEST/_reports/export_{today.date}.csv" --append \
  "$@" 2>&1 | tr '\r' '\n' | grep -v '━' | tee "$out"
rc=${pipestatus[1]}

summary=$(grep '^Processed:' "$out" | tail -1)
# count missing originals only; a few edited Live Photo clips never download and don't matter
# (read with osxphotos' own python: it has the New_Data permission, zsh/awk under launchd don't)
missing=$("$HOME/.local/share/uv/tools/osxphotos/bin/python" -I -c '
import csv, sys
rows = csv.DictReader(open(sys.argv[1], newline=""))
print(sum(1 for r in rows if r["datetime"] >= sys.argv[2] and r["missing"] == "1" and "_edited." not in r["filename"]))
' "$REPORT" "$start" 2>/dev/null)
errors=$(sed -nE 's/.*error: ([0-9]+).*/\1/p' <<< "$summary")

if (( rc != 0 )) || [[ -z $summary ]]; then
  notify "Export failed (exit $rc). See ~/Library/Logs/photos-export.log"
  exit 1
fi
if (( ${missing:-0} > 0 || ${errors:-0} > 0 )); then
  notify "${missing:-0} missing, ${errors:-0} errors. See ~/Library/Logs/photos-export.log"
fi

# hidden photos: tell the user when the count changes so they can export them by hand
hidden=$("$OSXPHOTOS" query --hidden --not-shared --count --quiet 2>/dev/null | tail -1)
last_file="$STATE/hidden_count"
last=$(cat "$last_file" 2>/dev/null || echo "")
echo "hidden photos in library: ${hidden:-?} (last run: ${last:-none})"
if [[ -n $hidden && $hidden != "$last" ]]; then
  [[ -n $last ]] && notify "Hidden photos changed ($last → $hidden). Export them by hand to _hidden."
  echo "$hidden" > "$last_file"
fi

echo "=== $(date '+%F %T') done ==="

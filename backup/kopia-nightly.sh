#!/bin/zsh
# Nightly Kopia snapshots to Backblaze B2. Run by launchd at 2:00
# (com.jbakse.kopia-nightly.plist); safe to run by hand. See backup/README.md.
#
# Uses the repository KopiaUI connected to (its config file and its bundled kopia
# binary), so the B2 key and repository password come from KopiaUI's setup/Keychain.
# Stops itself at 8:00; an interrupted upload resumes the next night.
set -uo pipefail

KOPIA="/Applications/KopiaUI.app/Contents/Resources/server/kopia"
CONFIG="$HOME/Library/Application Support/kopia/repository.config"
STOP_AT="${STOP_AT:-08:00}"   # override for a daytime run: STOP_AT=23:59 kopia-nightly.sh

# Sources, in order. Ones on a missing volume are skipped.
# (~ and ~/Library/Messages get added here in BACKUP_PLAN Phase 2.)
SOURCES=(
  "/Volumes/New_Data/iCloud Photos Export"
)

notify() {
  osascript -e "display notification \"$1\" with title \"Kopia backup\"" 2>/dev/null
  echo "NOTIFY: $1"
}

echo "=== $(date '+%F %T') kopia nightly ==="

# seconds until STOP_AT today (or 0 if already past)
deadline=$(date -j -f '%Y-%m-%d %H:%M' "$(date +%F) $STOP_AT" +%s)
failed=()

for src in $SOURCES; do
  if [[ $src == /Volumes/* && ! -d ${src%/*} ]]; then
    echo "$(date '+%T') skip (volume not mounted): $src"
    continue
  fi
  left=$(( deadline - $(date +%s) ))
  if (( left <= 0 )); then
    echo "$(date '+%T') past $STOP_AT; stopping before: $src"
    break
  fi
  echo "$(date '+%T') snapshot: $src (time left $((left/60)) min)"
  # run in the background so it can be stopped at the deadline
  caffeinate -i "$KOPIA" --config-file "$CONFIG" snapshot create "$src" --no-progress &
  pid=$!
  while kill -0 $pid 2>/dev/null; do
    if (( $(date +%s) >= deadline )); then
      echo "$(date '+%T') reached $STOP_AT; stopping (resumes tomorrow)"
      kill -INT $pid; wait $pid
      break 2
    fi
    sleep 30
  done
  wait $pid || failed+=("$src")
done

if (( ${#failed} )); then
  notify "Snapshot failed: ${failed[*]}. See ~/Library/Logs/kopia-nightly.log"
fi
echo "=== $(date '+%F %T') done ==="

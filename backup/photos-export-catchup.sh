#!/bin/zsh
# One-off helper for the FIRST photos export (photos-export.sh) when the internal
# drive can't hold all the iCloud originals at once.
#
# Photos caches every original it downloads inside the library on the internal
# drive and frees them only slowly ("purgeable" space is not freed on demand).
# So this exports one month at a time and waits for real free space before each
# month. Rounds repeat until nothing is missing or a round makes no progress.
#
# Usage: nohup caffeinate -i ~/dotfiles/backup/photos-export-catchup.sh \
#          >> ~/Library/Logs/photos-export-slices.log 2>&1 & disown
set -uo pipefail
DEST="/Volumes/New_Data/iCloud Photos Export"
REPORT="$DEST/_reports/export_2026-11-09.csv"   # first run's report (lists missing items)
PY="$HOME/.local/share/uv/tools/osxphotos/bin/python"
MIN_GB=${MIN_GB:-25}   # keep at least this much real free space for normal work (override: MIN_GB=12 ...)

free_gb() {
  "$PY" -I -c "
from Foundation import NSURL
ok,v,e=NSURL.fileURLWithPath_('/').getResourceValue_forKey_error_(None,'NSURLVolumeAvailableCapacityKey',None)
print(int(v/1e9))"
}

wait_for_space() {
  local a
  while true; do
    a=$(free_gb)
    (( a >= MIN_GB )) && return
    echo "$(date '+%F %T') only ${a} GB free; waiting for Photos to free space"
    /bin/sleep 900
  done
}

# months that still have a missing file (report rows marked missing whose file doesn't exist)
missing_months() {
  awk -F, 'NR>1 && $13==1{print $2}' "$REPORT" | sort -u | while read -r f; do
    [[ -e "$f" ]] || { p=(${(s:/:)f}); echo "${p[-3]}-${p[-2]}"; }
  done | sort -u
}

count_files() { /usr/bin/find "$DEST" -type f ! -name '*.xmp' ! -path '*/_reports/*' ! -name '.osxphotos*' | wc -l | tr -d ' '; }

round=0
while true; do
  round=$((round+1))
  months=( $(missing_months) )
  before=$(count_files)
  echo "$(date '+%F %T') round $round: ${#months} months with missing files; $before files exported"
  (( ${#months} == 0 )) && break
  for ym in $months; do
    y=${ym%-*}; m=${ym#*-}
    if [[ $m == 12 ]]; then next="$((y+1))-01-01"; else next="$y-$(printf %02d $((10#$m+1)))-01"; fi
    wait_for_space
    echo "$(date '+%F %T') $ym  (free $(free_gb) GB)"
    ~/dotfiles/backup/photos-export.sh --from-date "$y-$m-01" --to-date "$next" 2>&1 \
      | tr '\r' '\n' | grep -E '^Processed:|Error exporting' | sed 's/^/    /'
  done
  after=$(count_files)
  (( after == before )) && { echo "$(date '+%F %T') no progress this round; stopping"; break; }
done

wait_for_space
echo "$(date '+%F %T') final full pass"
~/dotfiles/backup/photos-export.sh 2>&1 | tr '\r' '\n' | grep -E '^Processed:' | sed 's/^/    /'
echo "$(date '+%F %T') done; $(count_files) files exported"

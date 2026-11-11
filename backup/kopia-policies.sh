#!/bin/zsh
# Apply Kopia policies to the repository (idempotent; re-run after changing).
# See backup/README.md.
set -euo pipefail
KOPIA="/Applications/KopiaUI.app/Contents/Resources/server/kopia"
CONFIG="$HOME/Library/Application Support/kopia/repository.config"
k() { "$KOPIA" --config-file "$CONFIG" "$@"; }

# global: retention 3 latest / 30 daily / 24 monthly / 5 annual, no hourly/weekly
k policy set --global \
  --keep-latest 3 --keep-hourly 0 --keep-daily 30 --keep-weekly 0 \
  --keep-monthly 24 --keep-annual 5 \
  --ignore-cache-dirs true

# photos export: already-compressed media, so no compression; skip Finder litter
k policy set "/Volumes/New_Data/iCloud Photos Export" \
  --compression none \
  --add-ignore .DS_Store

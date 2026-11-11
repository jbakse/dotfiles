# Backups

Two scheduled jobs, both run by launchd:

| Job | When | What |
| --- | --- | --- |
| **Photos export** (`com.jbakse.photos-export`) | Sundays 1:00 | Copies the iCloud Photos library, full resolution, to `/Volumes/New_Data/iCloud Photos Export/` with [osxphotos](https://github.com/RhetTbull/osxphotos). |
| **Kopia nightly** (`com.jbakse.kopia-nightly`) | Nightly 2:00, stops at 8:00 | Snapshots the photos export (and later `~`, Messages) to Backblaze B2 with [Kopia](https://kopia.io). |

So photos live in three places: iCloud, New_Data, and B2.

## Files

| File | What it is |
| --- | --- |
| `photos-export.sh` | The photos export. Run it by hand any time; only new or changed photos are copied. |
| `com.jbakse.photos-export.plist` | launchd job for the weekly export. |
| `photos-export-catchup.sh` | One-off helper used for the first export, which didn't fit on the internal drive. Exports month by month, waiting for free space. Only needed if a huge batch ever overflows the drive again. |
| `kopia-nightly.sh` | Snapshots each source to B2. Edit `SOURCES` to add more. |
| `com.jbakse.kopia-nightly.plist` | launchd job for the nightly Kopia run. |
| `kopia-policies.sh` | Retention, compression and ignore rules for the repository. Safe to re-run. |

Logs: `~/Library/Logs/photos-export.log`, `~/Library/Logs/kopia-nightly.log`. Both scripts post a macOS notification when something goes wrong.

## Photos export

- Photos stays on **Optimize Mac Storage**. osxphotos downloads originals it needs from iCloud. Photos caches each download inside its library and frees it only slowly; a weekly run is small enough not to matter, but a very large export can fill the internal drive (see `photos-export-catchup.sh`). Restarting the Mac makes Photos let go of some of that cache.
- Layout: `YYYY/MM/` folders, original file names, `.xmp` sidecars with keywords, titles and descriptions, file dates set to the capture date. Edited photos are exported too, as `NAME_edited.ext` next to the original.
- `.osxphotos_export.db` in the export folder tracks what's been exported. Don't delete it, or the next run starts over.
- `_reports/` has a CSV per day listing every file written or missed.
- **Not included:**
  - **Hidden photos.** The Hidden album is locked, so osxphotos can't read them. Export them by hand: open Hidden in Photos, select all, **File → Export → Export Unmodified Original** into `iCloud Photos Export/_hidden`. The weekly job notifies you when the number of hidden photos changes.
  - Shared-album photos and Messages "Shared with You" items, which aren't really in the library.
  - A few edited Live Photo motion clips (`*_edited.mov`) that iCloud won't hand over. The originals are exported; these are ignored when deciding whether to notify.
- Needs osxphotos (`uv tool install osxphotos`, in `setup.zsh`).

## Kopia

- The repository is the one set up in **KopiaUI**: B2 bucket `JCB-Kopia-Store`. The scripts use KopiaUI's config file (`~/Library/Application Support/kopia/repository.config`) and the `kopia` binary bundled inside KopiaUI.app, so there's no separate CLI install and no credentials in this repo. Keep the B2 key and repository password in 1Password: without the password the backup can never be read.
- Retention (`kopia-policies.sh`): latest 3, daily 30, monthly 24, annual 5.
- The photos export source has compression off (photos and video are already compressed) and ignores `.DS_Store`.
- To run during the day: `STOP_AT=23:59 ~/dotfiles/backup/kopia-nightly.sh`.
- Kopia warns that its native B2 storage type is deprecated. Someday, reconnect the repository in KopiaUI as **S3-compatible** (endpoint `s3.<region>.backblazeb2.com`, same bucket and key).

### Restoring

- **A few files:** open KopiaUI → Snapshots → pick the source and date → browse and download, or **Mount** it and copy in Finder.
- **Everything:** `kopia snapshot restore <snapshot-id> <target-dir>` (find IDs with `kopia snapshot list`). Use the binary in KopiaUI.app.
- **New Mac:** install KopiaUI (Brewfile), connect to the B2 repository with the key and password from 1Password, then install the launchd jobs below.

## Installing the jobs

```zsh
for job in photos-export kopia-nightly; do
  cp ~/dotfiles/backup/com.jbakse.$job.plist ~/Library/LaunchAgents/
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.jbakse.$job.plist
done
~/dotfiles/backup/kopia-policies.sh
```

The plists are copied rather than symlinked (launchd is unreliable with symlinks). After editing one, copy it again and reload:
`launchctl bootout gui/$(id -u)/com.jbakse.<job>` then `bootstrap` as above.

Run a job now: `launchctl kickstart gui/$(id -u)/com.jbakse.<job>`.

**Permissions:** the first run of each job raises macOS prompts (Photos library access, access to New_Data as a removable volume). Approve them. If a job later fails with "operation not permitted", check System Settings → Privacy & Security → Full Disk Access / Files and Folders. Paths change when osxphotos or KopiaUI is upgraded, so re-check after upgrades.

**Waking:** the jobs run at the next wake if the Mac is asleep. To make sure the nightly window is used: `sudo pmset repeat wakeorpoweron MTWRFSU 01:55:00`.

# Software plan

Everything on this Mac should be installed by something in this repo, so a new machine (or a cleanup six months from now) starts from a list instead of from memory.

## Where things go

| What | Where | Why |
| --- | --- | --- |
| GUI apps with a Homebrew cask | `Brewfile` (`cask "…"`) | One command installs and updates them. |
| Mac-only CLI tools (mole, uv, supabase) | `Brewfile` (`brew "…"`) | Homebrew has them first and they are tied to macOS. |
| Cross-platform CLI dev tools (eza, fzf, ffmpeg, node, pnpm…) | `devbox.json` | Nix via devbox. All `@latest`, no lock file in dotfiles, so a new machine gets current versions. |
| Claude Code | `npm install -g` in `setup.zsh` | The npm copy updates itself. Don't also add it to devbox. |
| Nix, devbox, Oh My Zsh | curl installers in `setup.zsh` | Bootstrap steps with no Homebrew package. |
| Apps with no cask (Steam/paid/vendor downloads) | `manual-installs.md` | So a rebuild doesn't forget them. |
| Microsoft 365, Xcode, apps you build yourself | nowhere | They manage themselves (Microsoft AutoUpdate, App Store, your repos). |

When something new gets installed, pick its row and record it there in the same sitting.

## Twice-yearly review

1. Rebuild the report and open it:
   ```
   ~/dotfiles/inventory/refresh.sh
   open ~/dotfiles/reports/software-inventory.html
   ```
2. Filter **Tracked: no**. For each item: add it to the right place above, or remove it.
3. Filter **Recommendations**, then go through the high ones (disk hogs, stale apps).
4. Update:
   ```
   brew update && brew upgrade && brew upgrade --cask --greedy
   devbox global update
   devbox version update
   ```
   Skip running apps, and ask before major version jumps (Blender, Xcode…).
5. Clean up: `brew cleanup --prune=all`, `nix-collect-garbage -d`, empty the Trash.
6. Rebuild the report again, then commit `Brewfile`, `devbox.json`, `setup.zsh` and `manual-installs.md`.

Working with Claude: "read plan.md, run inventory/refresh.sh and let's go through the report" picks this up.

## Gotchas

- `brew install --cask --adopt X` takes over an app you already have, but only if the versions match exactly. Update the app first if they don't.
- Casks with `auto_updates` (Chrome, Slack, Raycast…) only upgrade with `--greedy`. Homebrew often thinks they're older than they are.
- Casks that run a `.pkg` (docker-desktop, zoom, basictex) need `sudo`. Run them in a normal iTerm tab, not through Claude.
- Taps now need trust: `brew trust --formula supabase/tap/supabase`, or Homebrew silently ignores the formula.
- Prefer `brew uninstall --zap --cask X` or AppCleaner. Move personal data (saves, configs with keys) to the Trash instead of deleting it.
- `.npmrc` holds an npm auth token. Never commit it. Move the token to `~/.npmrc.local` or `${NPM_TOKEN}`.

## The report

`inventory/` builds `reports/software-inventory.html`, which git ignores. `refresh.sh` rescans everything each run: apps in `/Applications`, the Brewfile, `devbox.json`, npm globals, `~/.local/bin`, `bin/`, versions from the Homebrew catalog and npm, Spotlight launch dates, zsh history and disk usage. It takes about a minute.

Hand-written parts to review now and then:

- `desc.py`: one-line descriptions. New apps fall back to the Homebrew description.
- `build.py`:
  - `SPECIFIC`: per-app advice.
  - `LEFT`: leftover cache folders to check.
  - `LOCAL_BUILDS`: apps you build yourself.
  - `MENUBAR`: apps that are never "opened", so they aren't flagged as unused.
- `sizes.py` `EXTRA`: data folders outside `~/Library` that count toward an app's size.

## Open items (2026-10-27)

- Move the npm token out of `.npmrc`.
- USB Overdrive: update in-app to 5.4, then `brew install --cask --adopt usb-overdrive`.
- Trust or untap `supabase/tap`.
- Affinity 2 casks are deprecated. Affinity 3 is the free `affinity` cask.
- Pending major updates: Raycast 2, Steam, Xcode, PCoIPClient.
- Eagle: intentionally untracked.

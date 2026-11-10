# Software inventory

Builds a report of everything installed on this Mac and whether this dotfiles repo tracks it. Use it to answer "what is all this stuff, how did it get here, and do I still need it?"

The report is one HTML page, `~/dotfiles/reports/software-inventory.html`. It's generated from this machine's current state, so git ignores it.

## Run it

```sh
~/dotfiles/inventory/refresh.sh
open ~/dotfiles/reports/software-inventory.html
```

A run takes a few minutes, mostly measuring disk usage. Every run rescans from scratch, so run it again whenever you want fresh numbers.

## What's in the report

One row for each:

- **App:** everything in `/Applications`.
- **CLI tool:** Homebrew formulae, devbox/Nix packages, npm globals, `~/.local/bin` and this repo's `bin/` scripts.
- **Leftover:** cache or support folders worth checking.

Columns show how each item was installed, its version against the latest release, when you last used it (Spotlight launch dates and zsh history) and how much disk it takes. Click a row for details: where the files live, where the app was downloaded from, and recommendations with a command to run when there is one.

**Tracked** means a new machine would get the item back from this repo: through the `Brewfile`, `devbox.json`, `setup.zsh`, `manual-installs.md` or `bin/`.

## Using it

The filters along the top do most of the work:

- **Not tracked:** installed but missing from dotfiles. Add each one to the right place (see the table in `../plan.md`) or uninstall it.
- **Has high-priority recommendations:** the big wins, usually disk hogs.
- **Not used in 90 days:** candidates to remove.
- **Out of date:** things to update.

`../plan.md` has the full twice-yearly review checklist that this report supports.

## Editing it

| File | What it does |
| --- | --- |
| `refresh.sh` | Runs everything in order. Start here. |
| `collect.py` | Scans `/Applications` and matches apps to Homebrew casks. |
| `extra.py` | Reads download source and copyright for each app. |
| `sizes.py` | Measures disk usage, including caches in `~/Library`. |
| `build.py` | Combines everything into rows and writes the recommendations. |
| `desc.py` | One-line descriptions. New apps fall back to the Homebrew description. |
| `template.html` | The report page. The data is inlined into it. |
| `icon.swift` | Small tool that extracts app icons. It's compiled on the first run. |

Hand-written lists to touch up now and then:

- `desc.py`: descriptions.
- `build.py`, in the `SPECIFIC` list: per-app advice.
- `build.py`, in the `LEFT` list: leftover folders to check.
- `build.py`, in the `LOCAL_BUILDS` list: apps you build yourself.
- `build.py`, in the `MENUBAR` list: apps that are never "opened", so they aren't flagged as unused.

`data/`, `icons/` and the compiled `icon` binary are scratch output and are gitignored. The Homebrew catalog in `data/` is downloaded at most once a day.

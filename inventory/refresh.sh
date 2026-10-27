#!/bin/zsh
# Rescan this Mac and rebuild ~/dotfiles/reports/software-inventory.html
# Takes a few minutes (disk sizes). See ~/dotfiles/plan.md.
set -e
cd ${0:A:h}
mkdir -p data icons ~/dotfiles/reports
eval "$(devbox global shellenv)"

echo "→ Homebrew catalog"
for k in cask formula; do
  # refresh at most once a day
  if [[ ! -s data/$k.json || -n $(find data/$k.json -mtime +0) ]]; then
    curl -fsSL https://formulae.brew.sh/api/$k.json -o data/$k.json.new && mv data/$k.json.new data/$k.json
  fi
done

echo "→ Homebrew formulae"
# brew leaves skips formulae from untrusted taps, so also list every tap formula
{ brew leaves --installed-on-request; brew list --formula --full-name -1 | grep / | sed 's|.*/||' } | sort -u |
  while read f; do v=$(/bin/ls /opt/homebrew/Cellar/$f 2>/dev/null | tail -1); [[ -n $v ]] && echo "$f $v"; done > data/brew_versions.txt || true

echo "→ npm globals"
: > data/npm_latest.txt
for p in ~/.npm/lib/node_modules/{@*/*,[^@]*}(N/); do
  n=${p#$HOME/.npm/lib/node_modules/}
  echo "$n $(npm view $n version 2>/dev/null)" >> data/npm_latest.txt
done

echo "→ Nix closure sizes"
B=~/.local/share/devbox/global/default/.devbox/nix/profile/default/bin
: > data/nix_sizes.txt
for p in $(jq -r '.packages[]' ~/dotfiles/devbox.json); do
  n=${p%@*}; [[ $n == nodejs ]] && n=node
  [[ -e $B/$n ]] || continue
  echo "$n $(nix path-info -S $(readlink -f $B/$n | cut -d/ -f1-4) | awk '{print $2}')" >> data/nix_sizes.txt
done

echo "→ Apps"
python3 collect.py > /dev/null
python3 extra.py
[[ -x icon ]] || swiftc -O -o icon icon.swift
python3 -c "import json; [print(a['path']) for a in json.load(open('data/apps.json'))]" | tr '\n' '\0' | xargs -0 ./icon icons

echo "→ Disk usage"
python3 sizes.py > /dev/null

echo "→ Report"
python3 build.py | tail -1
python3 - <<'PY'
import os
d = open('data/items.json').read()
s = open('template.html').read()
open(os.path.expanduser('~/dotfiles/reports/software-inventory.html'), 'w').write(s.replace('__DATA__', d.replace('</', '<\\/')))
PY
echo "open ~/dotfiles/reports/software-inventory.html"

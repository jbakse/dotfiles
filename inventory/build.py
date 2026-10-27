import json, base64, os, re, datetime, subprocess
S = os.path.dirname(os.path.abspath(__file__))
exec(open(f'{S}/desc.py').read())
apps = json.load(open(f'{S}/data/apps.json'))
extra = json.load(open(f'{S}/data/extra.json'))
formula = {x['name']: x for x in json.load(open(f'{S}/data/formula.json'))}
def fv(n): return (formula.get(n) or {}).get('versions', {}).get('stable')
# zsh history: last use + count per command
hist = {}
_hts = []
for line in open(os.path.expanduser('~/.zsh_history'), 'rb').read().decode('utf-8', 'replace').splitlines():
    m = re.match(r': (\d+):\d+;(.*)', line)
    if not m: continue
    ts = int(m.group(1)); _hts.append(ts)
    for seg in re.split(r'\||&&|;', m.group(2)):
        w = seg.strip().split()
        if not w: continue
        c = w[0]
        if c in ('sudo', 'time', 'npx') and len(w) > 1: c = w[1]
        h = hist.setdefault(c, [0, 0]); h[0] += 1; h[1] = max(h[1], ts)
ALIAS = {'eza': ['eza', 'ls', 'lst'], 'bat': ['bat', 'less', 'more', 'browse'], 'fzf': ['fzf', 'browse'], 'fd': ['fd', 'big'], 'zoxide': ['z', 'zi', 'zoxide'],
 'butterfish': ['butterfish', 'bf'], 'git-l': ['git-l', 'glog'], 'git-clean-branches': ['git-clean-branches', 'gclean'], 'nodejs': ['node', 'npm'],
 '@anthropic-ai/claude-code': ['claude'], 'claude-code (nix)': [], '_removed_@fission-ai/openspec': ['openspec'], '_removed_@mariozechner/pi-coding-agent': ['pi'], 'vercel': ['vercel'],
 'pnpm': ['pnpm'], 'supervisor': ['supervisor'], 'Docker CLIs': ['docker', 'docker-compose', 'kubectl'], 'ollama (stale link)': ['ollama'], 'lucid (CLI)': ['Lucid2', 'lucid'],
 'git-filter-repo': ['git-filter-repo'], 'basictex': ['pdflatex', 'tlmgr', 'latex'], 'gh': ['gh'], 'tldr': ['tldr']}
def usage(name):
    keys = ALIAS.get(name, [name])
    cnt = sum(hist.get(k, [0, 0])[0] for k in keys); last = max([hist.get(k, [0, 0])[1] for k in keys] or [0])
    return cnt, (datetime.datetime.fromtimestamp(last).date().isoformat() if last else None)
def _d(t): return datetime.datetime.fromtimestamp(t).strftime('%b %-d, %Y')
HIST_RANGE = f'zsh history ({_d(min(_hts))} – {_d(max(_hts))})' if _hts else 'zsh history'
LOCAL_BUILDS = {'RepoRadar', 'Right Now', 'VibePulse'}  # apps you build yourself
items = []
def icon(path):
    f = f'{S}/icons/{os.path.basename(path)}.png'
    return 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode() if os.path.exists(f) else None
for a in apps:
    e = extra.get(a['name'], {})
    name = a['name']
    if name == 'Microsoft OneNote': a['pkg'] = 'com.microsoft.package.Microsoft_OneNote.app'
    m = a['method']
    if m == 'Homebrew': m = 'Brewfile' if a['in_brewfile'] else 'Homebrew (untracked)'
    elif m == 'Installer pkg': m = 'Vendor installer'
    if name == 'Claude Code URL Handler': m = 'Auto-created'
    if m == 'Direct download' and not e.get('quarantine') and not e.get('wherefrom') and not a['updater'] and not a['brew_available'] and name in LOCAL_BUILDS: m = 'Built locally'
    src = e.get('quarantine')
    if src: src = src.replace('\\x20', ' ')
    ver = a['version'].lstrip('v')
    if name == 'zoom.us': ver = ver.split(' ')[0]
    lu = a['last_used'][:10] if a['last_used'] else None
    tip = None
    if m == 'Homebrew (untracked)': tip = f'Installed with Homebrew but missing from the Brewfile. Add: cask "{a["cask"]}"'
    elif m == 'Brewfile': tip = 'Tracked in your Brewfile.'
    elif m in ('Direct download',) and a['brew_available']: tip = f'Available as a Homebrew cask. To bring it under management: brew install --cask --adopt {a["brew_available"]}, then add cask "{a["brew_available"]}" to the Brewfile.'
    elif m == 'Direct download': tip = 'No Homebrew cask exists. Note it in ~/dotfiles/manual-installs.md so a rebuild doesn\'t forget it.'
    elif m == 'App Store': tip = 'From the Mac App Store. Track it with mas in the Brewfile (brew "mas" plus mas "Name", id: …).'
    elif m == 'Vendor installer': tip = 'Installed by the vendor\'s .pkg. Microsoft 365 apps update through Microsoft AutoUpdate, so leaving them out of the Brewfile is reasonable.' if name.startswith('Microsoft') or name == 'OneDrive' else (f'Installed from the vendor .pkg. A cask exists ({a["brew_available"] or "zoom"}).' if a['brew_available'] else 'Installed from the vendor .pkg.')
    elif m == 'Built locally': tip = 'Not signed and no download record. Likely something you built.'
    elif m == 'Auto-created': tip = 'Created automatically by Claude Code. Nothing to manage.'
    items.append(dict(kind='App', name=name, icon=icon(a['path']), path=a['path'], id=a['bundle_id'], version=ver, latest=a['latest'], latest_source=a['latest_source'],
        method=m, tracked=m in ('Brewfile',), cask=a['cask'] or a['brew_available'], updater=a['updater'], source=src, pkg=a['pkg'],
        last_used=lu, uses=int(a['use_count']) if a['use_count'] else None, usage_source='Spotlight launch record' if lu else None, running=a['running'],
        added=(a['added'] or '')[:10] or None, desc=D.get(name, a.get('brew_desc') or ''), tip=tip, homepage=a.get('homepage')))
# CLI
bv = dict(l.split(' ', 1) for l in open(f'{S}/data/brew_versions.txt').read().strip().splitlines())
def cli(name, method, version, latest, path, desc_key=None, tracked=False, tip=None, latest_source=None, cmd=None):
    cnt, last = usage(cmd or name)
    items.append(dict(kind='CLI', name=name, icon=None, path=path, id=None, version=version, latest=latest, latest_source=latest_source,
        method=method, tracked=tracked, cask=None, updater=[], source=None, pkg=None, last_used=last, uses=cnt or None,
        usage_source=HIST_RANGE if last else None, running=False, added=None, desc=C.get(desc_key or name, ''), tip=tip, homepage=None))
bf = open(os.path.expanduser('~/dotfiles/Brewfile')).read()
for n, v in bv.items():
    tr = n in bf
    cli(n, 'Brewfile' if tr else 'Homebrew (untracked)', v, fv(n), f'/opt/homebrew/bin/{n}', tracked=tr, latest_source='Homebrew',
        tip='Tracked in your Brewfile.' if tr else f'Installed with Homebrew but missing from the Brewfile. Add: brew "{n}"')
lock = json.load(open(os.path.expanduser('~/.local/share/devbox/global/default/devbox.lock')))['packages']
dbjson = json.load(open(os.path.expanduser('~/dotfiles/devbox.json')))['packages']
DB = [(p.split('@')[0], None if p.startswith('tldr') else p.split('@')[0]) for p in dbjson if p.endswith('@latest')]
for n, f in DB:
    v = lock.get(f'{n}@latest', {}).get('version')
    cli(n, 'devbox (Nix)', v, fv(f) if f else None, '~/.local/share/devbox/global/…/bin/' + n, tracked=True, latest_source='upstream, via Homebrew catalog',
        tip='Tracked in devbox.json. Run devbox global update to pick up newer releases.')
for p in dbjson:
    if p.startswith('nodejs@') and p in lock:
        major = p.split('@')[1]
        cli('nodejs', 'devbox (Nix)', lock[p]['version'], fv(f'node@{major}') or fv('node'), '~/.local/share/devbox/global/…/bin/node', tracked=True, latest_source=f'upstream {major}.x, via Homebrew catalog', tip=f'Tracked in devbox.json ({p}). Run devbox global update.')
npm_latest = dict(l.split(' ', 1) for l in open(f'{S}/data/npm_latest.txt').read().strip().splitlines())
NM = os.path.expanduser('~/.npm/lib/node_modules')
NPM = []
for e in sorted(os.listdir(NM)) if os.path.isdir(NM) else []:
    if e.startswith('.'): continue
    NPM += [f'{e}/{x}' for x in sorted(os.listdir(f'{NM}/{e}')) if not x.startswith('.')] if e.startswith('@') else [e]
for n in NPM:
    if os.path.islink(f'{NM}/{n}'):
        cli(n, 'npm global', None, None, os.readlink(f'{NM}/{n}'), tip='npm link to a local project folder. Unlink with npm rm -g ' + n + ' if that project is dormant.')
        continue
    v = json.load(open(os.path.expanduser(f'~/.npm/lib/node_modules/{n}/package.json')))['version']
    tip = 'Global npm package. Nothing in dotfiles records it. Consider a list in dotfiles (or devbox) and reinstall from it.'
    if n == '@anthropic-ai/claude-code': tip = 'The only Claude Code install. It updates itself, and setup.zsh installs it on a new machine.'
    cli(n, 'npm global', v, npm_latest.get(n) or None, '~/.npm/lib/node_modules/' + n, latest_source='npm', tip=tip)
cli('devbox', 'curl installer', subprocess.run(['devbox', 'version'], capture_output=True, text=True).stdout.strip().splitlines()[-1], None, '/usr/local/bin/devbox', tip='Installed by Jetify\'s curl script (no Homebrew package); setup.zsh records it. Update with devbox version update.')
def ver_of(*cmd):
    try: return re.findall(r'\d+(?:\.\d+)+', subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout)[-1]
    except Exception: return None
cli('nix', 'curl installer', ver_of('nix', '--version'), None, '/nix/var/nix/profiles/default/bin/nix', tip='Installed by the Determinate Nix installer (no Homebrew package); setup.zsh records it. Bootstrap dependency for devbox.')
for f in sorted(os.listdir(os.path.expanduser('~/.local/bin'))) if os.path.isdir(os.path.expanduser('~/.local/bin')) else []:
    if f.startswith('.') or f in ('claude',): continue
    cli(f, 'curl installer', ver_of(os.path.expanduser(f'~/.local/bin/{f}'), '--version'), None, f'~/.local/bin/{f}', tip='Standalone binary in ~/.local/bin. Not tracked anywhere.')
if os.path.exists('/usr/local/bin/docker'): cli('Docker CLIs', 'Bundled with app', None, None, '/usr/local/bin/docker → Docker.app', tip='Comes with Docker Desktop. Managing the docker-desktop cask covers these.')
if os.path.exists('/usr/local/bin/Lucid2'): cli('lucid (CLI)', 'Bundled with app', None, None, '/usr/local/bin/Lucid2 → Lucid.app', tip='Comes with the Lucid app.')
if os.path.islink('/usr/local/bin/ollama'): cli('ollama (stale link)', 'Bundled with app', None, None, '/usr/local/bin/ollama → /Applications/Ollama.app (missing)', tip='Dangling symlink. Remove with sudo rm /usr/local/bin/ollama, or reinstall Ollama with brew install --cask ollama-app.')
_casks = json.load(open(f'{S}/data/cask.json'))
CLI_FONT_PATHS = {}
for t in re.findall(r'^cask "(font-[^"]+)"', bf, re.M):
    cr = f'/opt/homebrew/Caskroom/{t}'
    if os.path.isdir(cr):
        cv = next((c['version'] for c in _casks if c['token'] == t), None)
        cli(t, 'Brewfile', sorted(os.listdir(cr))[-1], cv, '~/Library/Fonts', tracked=True, latest_source='Homebrew', tip='Tracked in your Brewfile.')
        CLI_FONT_PATHS[t] = [('Cask', cr)]
for n in sorted(f for f in os.listdir(os.path.expanduser('~/dotfiles/bin')) if not f.startswith('.')):
    cli(n, 'dotfiles script', None, None, '~/dotfiles/bin/' + n, tracked=True, tip='Lives in your dotfiles repo.')
for it in items:
    if it['name'] == 'CHITUBOX': it['latest'] = None; it['latest_source'] = None; it['version'] = 'Basic 2025'
    if it['name'].startswith('font-'): it['kind'] = 'Font'
for it in items: it['tracked'] = it['method'] in ('Brewfile', 'devbox (Nix)', 'dotfiles script')
_setup = open(os.path.expanduser('~/dotfiles/setup.zsh')).read()
_manual = set(re.findall(r'^- \*\*(.+?)\*\*', open(os.path.expanduser('~/dotfiles/manual-installs.md')).read(), re.M))
for it in items:
    if it['name'] in _manual:
        it['tracked'] = True; it['tracked_via'] = 'manual-installs.md'
        it['recs'] = [r for r in it.get('recs', []) if r['title'] != 'Record it in your dotfiles']
for it in items:
    if it['name'] in ('devbox', 'nix') and it['name'] in _setup:
        it['tracked'] = True; it['tracked_via'] = 'setup.zsh'
for it in items:
    if it['method'] == 'npm global' and re.search(r'npm (install|i) -g .*' + re.escape(it['name']) + r'\b', _setup):
        it['tracked'] = True; it['tracked_via'] = 'setup.zsh'
json.dump(dict(generated=datetime.date.today().isoformat(), items=items), open(f'{S}/data/items.json', 'w'))
from collections import Counter
print(len(items), Counter(i['method'] for i in items))

# ---------- disk usage ----------
import glob as _g
H = os.path.expanduser('~')
def du(p):
    p = os.path.expanduser(p)
    if not os.path.exists(p): return 0
    r = subprocess.run(['du', '-sk', p], capture_output=True, text=True).stdout.split()
    return int(r[0]) * 1024 if r else 0
def parts_of(lst):
    ps = [{'label': l, 'path': p, 'bytes': du(p)} for l, p in lst]
    ps = [x for x in ps if x['bytes'] > 0]; ps.sort(key=lambda x: -x['bytes']); return ps
app_sizes = json.load(open(f'{S}/data/app_sizes.json'))
nix = {l.split()[0]: int(l.split()[1]) for l in open(f'{S}/data/nix_sizes.txt') if len(l.split()) > 1}
NIXBIN = {'nodejs': 'node'}
CLI_PATHS = {
 '@anthropic-ai/claude-code': [('~/.claude (settings, sessions, history)', '~/.claude')],
 'nodejs': [('npm download cache', '~/.npm/_cacache'), ('npx cache', '~/.npm/_npx')],
 'uv': [('uv cache', '~/.cache/uv'), ('uv tools and Pythons', '~/.local/share/uv')],
 'deno': [('Deno cache', '~/Library/Caches/deno'), ('~/.deno', '~/.deno')],
 'tldr': [('Page cache', '~/.tldrc')],
 'mole': [('Cache', '~/.cache/mole')],
 'devbox': [('Binary', '/usr/local/bin/devbox'), ('Cache', '~/.cache/devbox')],
 'nix': [('/nix/store (all packages, all generations)', '/nix/store'), ('Nix eval cache', '~/.cache/nix')],
 'agentsview': [('Binary', '~/.local/bin/agentsview'), ('Index and data', '~/.agentsview')],
 'pnpm': [('pnpm cache', '~/Library/Caches/pnpm')],
}
CLI_PATHS.update(CLI_FONT_PATHS)
for it in items:
    n = it['name']
    if it['kind'] == 'App':
        s = app_sizes.get(n); it['disk'] = s['total'] if s else None; it['disk_parts'] = s['parts'] if s else []; it['disk_note'] = s.get('note') if s else None
        continue
    lst = []
    if it['method'] in ('Brewfile', 'Homebrew (untracked)') and os.path.isdir(f'/opt/homebrew/Cellar/{n}'): lst.append(('Homebrew Cellar', f'/opt/homebrew/Cellar/{n}'))
    if it['method'] == 'npm global': lst.append(('npm package', f'~/.npm/lib/node_modules/{n}'))
    if it['method'] == 'dotfiles script': lst.append(('Script', f'~/dotfiles/bin/{n}'))
    lst += CLI_PATHS.get(n, [])
    ps = parts_of(lst)
    note = None
    if it['method'] == 'devbox (Nix)':
        b = nix.get(NIXBIN.get(n, n))
        if b: ps.insert(0, {'label': 'Nix closure (package plus its dependencies, some shared)', 'path': '/nix/store', 'bytes': b})
        note = 'Nix closures overlap, so shared libraries are counted under several packages. The real total is the nix store item.'
    if n == 'nix': note = f'Your current devbox packages need about {sum(nix.values())/1e9:.1f} GB including overlap. The rest is old generations and build leftovers that garbage collection can remove.'
    if n == 'nodejs': note = 'Includes the npm download cache, which every npm and npx install fills.'
    it['disk'] = sum(x['bytes'] for x in ps) or None; it['disk_parts'] = ps; it['disk_note'] = note
for it in items:
    for x in it.get('disk_parts', []): x['path'] = x['path'].replace(H, '~')

# leftovers: data with no installed owner, and general caches
LEFT = [
 ('Trash', 'Files in the Trash still take up disk space until it is emptied.', [('~/.Trash', '~/.Trash')], [('high', 'Empty the Trash', 'Review it first if you are unsure, then empty it from the Finder.', None)]),
 ('Playwright browsers', 'Chromium, Firefox and WebKit builds downloaded by Playwright and the Playwright MCP server for browser automation.', [('ms-playwright', '~/Library/Caches/ms-playwright'), ('ms-playwright-mcp', '~/Library/Caches/ms-playwright-mcp')],
   [('medium', 'Remove old browser builds', 'Each Playwright version downloads its own browsers and old ones are never removed. Projects re-download what they need.', 'rm -rf ~/Library/Caches/ms-playwright ~/Library/Caches/ms-playwright-mcp')]),
 ('Build tool caches', 'Download caches left by Electron, electron-builder, node-gyp and pip.', [('electron', '~/Library/Caches/electron'), ('electron-builder', '~/Library/Caches/electron-builder'), ('node-gyp', '~/Library/Caches/node-gyp'), ('pip', '~/Library/Caches/pip')],
   [('low', 'Clear the caches', 'All of these are rebuilt on demand.', 'rm -rf ~/Library/Caches/{electron,electron-builder,node-gyp,pip}')]),
 ('Homebrew cache', 'Downloaded bottles and cask installers kept after installing.', [('Homebrew cache', '~/Library/Caches/Homebrew')], [('low', 'Clean up old downloads', 'Removes cached downloads and outdated versions.', 'brew cleanup --prune=all')]),
 ('Vibe Kanban data', 'Data from Vibe Kanban, an AI-agent task board run with npx. No copy is installed now.', [('~/.vibe-kanban', '~/.vibe-kanban'), ('App Support', '~/Library/Application Support/ai.bloop.vibe-kanban')],
   [('medium', 'Delete if you are done with Vibe Kanban', None, 'rm -rf ~/.vibe-kanban ~/Library/Application\\ Support/ai.bloop.vibe-kanban')]),
 ('GitKraken CLI data', 'Data from the GitKraken CLI (gk). The CLI is not installed.', [('App Support', '~/Library/Application Support/GitKrakenCLI')], [('low', 'Delete orphaned data', None, 'rm -rf ~/Library/Application\\ Support/GitKrakenCLI')]),
 ('InsightFace models', 'Face-recognition models downloaded by a Python tool (InsightFace), usually through an image-generation or face-swap project.', [('~/.insightface', '~/.insightface')], [('low', 'Delete if that project is gone', 'The models re-download when needed.', 'rm -rf ~/.insightface')]),
 ('Cargo registry', 'Rust crate index and downloads. Rust/cargo is not installed, so this is left over.', [('~/.cargo', '~/.cargo')], [('low', 'Delete orphaned cargo data', None, 'rm -rf ~/.cargo')]),
 ('Hugging Face cache', 'Model files downloaded through the Hugging Face libraries.', [('~/.cache/huggingface', '~/.cache/huggingface')], []),
]
for name, desc, lst, recs in LEFT:
    ps = parts_of(lst)
    if not ps: continue
    for x in ps: x['path'] = x['path'].replace(H, '~')
    items.append(dict(kind='Leftover', name=name, icon=None, path=lst[0][1], id=None, version=None, latest=None, latest_source=None, method='Leftover data', tracked=False,
        cask=None, updater=[], source=None, pkg=None, last_used=None, uses=None, usage_source=None, running=False, added=None, desc=desc,
        tip=None, homepage=None, disk=sum(x['bytes'] for x in ps), disk_parts=ps, disk_note=None,
        recs=[dict(level=l, title=t, detail=d, cmd=c) for l, t, d, c in recs]))

# ---------- recommendations ----------
def gb(b): return f'{b/1e9:.1f} GB' if b >= 1e9 else f'{b/1e6:.0f} MB'
def vparts(v): return [int(x) for x in re.findall(r'\d+', str(v or ''))]
def behind(it):
    a, b = vparts(it['version']), vparts(it['latest'])
    if not a or not b: return None
    for i in range(max(len(a), len(b))):
        x, y = (a + [0]*9)[i], (b + [0]*9)[i]
        if x > y: return None
        if x < y: return ['major', 'minor', 'patch'][min(i, 2)]
    return None
cask_info = {c['token']: c for c in json.load(open(f'{S}/data/cask.json'))}
TODAY = datetime.date.today()
MENUBAR = {'Maccy', 'MonitorControl', 'Raycast', 'Reflex', 'VibePulse', 'Elgato Control Center', 'USB Overdrive', 'CameraController', 'Lucid', 'OneDrive', '1Password'}
SPECIFIC = {
 'Docker': [('high', 'Reclaim Docker disk space', 'Most of this is the Linux VM disk image holding images, containers and build cache. Pruning removes everything not used by a running container. You can also cap the disk size in Settings → Resources.', 'docker system prune -a --volumes')],
 'ChatGPT': [('high', 'Clear old Codex data', 'Much of this is usually Codex (the coding agent inside ChatGPT): ~/Library/Application Support/Codex, ~/.codex and runtime caches. Look in Application Support/Codex for old worktrees and sandboxes before deleting.', 'du -sh ~/Library/Application\\ Support/Codex/* | sort -h | tail')],
 'Google Chrome': [('medium', "Turn off Chrome's on-device AI model", 'OptGuideOnDeviceModel is a multi-GB Gemini Nano model. Set chrome://flags/#optimization-guide-on-device-model to Disabled and Chrome deletes it.', None),
                   ('low', 'Review Chrome profiles', 'Each Chrome profile keeps its own history and cache. Remove any you no longer use from the profile menu.', None)],
 'Lucid': [('high', 'Shrink the LucidLink cache', '~/.lucid is almost entirely the local file cache, which grows to its configured limit. Lower the cache size in LucidLink settings. The CLI can also do it; check Lucid2 help config for the exact option.', None)],
 'Claude': [('medium', 'Remove the Claude agent VM if you do not use it', 'vm_bundles is the Linux VM Claude uses for agent tasks. Deleting it frees the space; Claude downloads it again if you use those features.', 'rm -rf ~/Library/Application\\ Support/Claude/vm_bundles')],
 'Spotify': [('high', 'Clear the Spotify cache', 'The streaming cache grows large. Clear it in Spotify → Settings → Storage. Downloaded songs are separate and stay.', None)],
 'Xcode': [('medium', 'Update or replace Xcode', 'If Xcode is far behind, update it from the App Store. If you only need compilers and git, the Command Line Tools (xcode-select --install) are much smaller.', None),
           ('low', 'Clear Xcode build data', 'DerivedData and old device support files rebuild on demand.', 'rm -rf ~/Library/Developer/Xcode/DerivedData ~/Library/Developer/Xcode/iOS\\ DeviceSupport')],
 'Meshmixer': [('medium', "You probably don't need this", 'Autodesk discontinued Meshmixer and it has no recorded use here. Blender and your slicers cover mesh repair.', None)],
 'Microsoft Defender Shim': [('low', "You probably don't need this", 'It is only a placeholder that offers Defender for Endpoint. Microsoft 365 apps work without it.', None)],
 'Cider': [('medium', "You probably don't need this", 'Cider is an Apple Music client, but you listen with Spotify, and it has no recorded use.', None)],
 'tldr': [('medium', 'Swap tldr for tlrc', 'The nixpkgs tldr client pulls in about 1.4 GB of Haskell dependencies. tlrc is the official Rust client and is tiny. Replace tldr@latest with tlrc@latest in devbox.json.', 'devbox global rm tldr && devbox global add tlrc')],
 'nix': [('low', 'See what keeps the rest of the store', 'After nix-collect-garbage -d, what remains is held by GC roots, usually .devbox folders in project directories. Delete a project\'s .devbox folder and collect again to free its packages.', 'nix-store --gc --print-roots | grep -v /proc | cut -d" " -f1 | sort -u')],
 'nodejs': [('high', 'Clear the npm cache', 'The npm download cache only speeds up reinstalls.', 'npm cache clean --force')],
 'agentsview': [('low', 'Check the agentsview index', '~/.agentsview holds indexed agent sessions.', None)],
}
for it in items:
    if it['kind'] == 'Leftover': continue
    R = []
    n, m = it['name'], it['method']
    for r in SPECIFIC.get(n, []): R.append(r)
    if m == 'Homebrew (untracked)':
        line = f'cask "{it["cask"]}"' if it['kind'] == 'App' else f'brew "{n}"'
        R.append(('medium', 'Add to Brewfile', 'Installed with Homebrew, but a fresh setup would miss it.', f"echo '{line}' >> ~/dotfiles/Brewfile"))
    if m == 'Direct download' and it.get('cask') and n not in ('Meshmixer', 'Cider'):
        R.append(('medium', 'Use Homebrew to manage', f'A cask exists. --adopt takes over the copy you already have without reinstalling.', f"brew install --cask --adopt {it['cask']} && echo 'cask \"{it['cask']}\"' >> ~/dotfiles/Brewfile"))
    if m == 'Direct download' and not it.get('cask') and it['kind'] == 'App' and not it.get('tracked') and n not in ('Meshmixer', 'Microsoft Defender Shim'):
        R.append(('low', 'Record it in your dotfiles', 'No Homebrew cask exists. Add a line to ~/dotfiles/manual-installs.md so a rebuild includes it.', None))
    if m == 'App Store':
        R.append(('low', 'Track with mas', 'mas lets the Brewfile reinstall App Store apps.', f"echo 'mas \"{n}\", id: <app id>' >> ~/dotfiles/Brewfile   # find the id with: mas list"))
    if m == 'npm global' and it['version'] and not it.get('tracked'):
        R.append(('low', 'Record global npm packages', 'Nothing in dotfiles lists these. Keep a list (for example dotfiles/npm-globals.txt) and reinstall with xargs npm i -g < npm-globals.txt.', None))
    b = behind(it)
    if b in ('major', 'minor'):
        if m in ('Brewfile', 'Homebrew (untracked)'):
            c = cask_info.get(it.get('cask') or '')
            cmd = f"brew upgrade --cask {it['cask']}" if it['kind'] == 'App' else f'brew upgrade {n}'
            if c and c.get('auto_updates'): cmd = f"brew upgrade --cask --greedy {it['cask']}"
        elif m == 'npm global': cmd = f'npm i -g {n}@latest'
        elif m == 'devbox (Nix)': cmd = 'devbox global update'
        elif m == 'App Store': cmd = 'open macappstore://showUpdatesPage'
        else: cmd = None
        R.append(('high' if b == 'major' else 'medium', f'Update ({b} version behind)', f"{it['version']} installed, {it['latest']} available." + ('' if cmd else ' Use the app\'s own "Check for Updates".'), cmd))
    if it['kind'] == 'App' and not it['running'] and n not in MENUBAR and m not in ('Vendor installer', 'Auto-created') and not any(r[1].startswith("You") for r in R):
        lu = it['last_used']
        if lu is None or (TODAY - datetime.date.fromisoformat(lu)).days > 90:
            size = f" Removing it frees about {gb(it['disk'])}." if it.get('disk') else ''
            how = f"brew uninstall --zap --cask {it['cask']}" if m in ('Brewfile', 'Homebrew (untracked)') and it.get('cask') else None
            R.append(('low', 'Remove if unused', ('No recorded launch.' if lu is None else f'Last opened {lu}.') + size + ('' if how else ' AppCleaner (installed) also removes its Library files.'), how))
    order = {'high': 0, 'medium': 1, 'low': 2}
    R.sort(key=lambda r: order[r[0]])
    it['recs'] = [dict(level=l, title=t, detail=d, cmd=c) for l, t, d, c in R]
json.dump(dict(generated=datetime.date.today().isoformat(), items=items), open(f'{S}/data/items.json', 'w'))
print('recs:', sum(len(i['recs']) for i in items), 'disk:', gb(sum(i.get('disk') or 0 for i in items)))

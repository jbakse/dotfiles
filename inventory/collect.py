import json, os, plistlib, subprocess, re, glob, datetime, urllib.request, urllib.parse
S = os.path.dirname(os.path.abspath(__file__))
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout
casks = json.load(open(f'{S}/data/cask.json'))
app2cask = {}
for c in casks:
    for a in c.get('artifacts', []):
        if isinstance(a, dict) and 'app' in a:
            for n in a['app']:
                if isinstance(n, str): app2cask.setdefault(n, c)
                elif isinstance(n, dict) and 'target' in n: app2cask.setdefault(os.path.basename(n['target']), c)
installed_casks = set(sh('brew list --cask').split())
brewfile = open(os.path.expanduser('~/dotfiles/Brewfile')).read()
inbrewfile = set(re.findall(r'^cask "([^"]+)"', brewfile, re.M)) | set(x.split('/')[-1] for x in re.findall(r'^brew "([^"]+)"', brewfile, re.M))
# cask installed app names
inst_app = {}
for c in casks:
    if c['token'] in installed_casks:
        for a in c.get('artifacts', []):
            if isinstance(a, dict) and 'app' in a:
                for n in a['app']:
                    if isinstance(n, str): inst_app[n] = c
running = sh('ps -axo comm')
tok = {c['token']: c for c in casks}
OVERRIDE = {'zoom.us.app': 'zoom', 'Elgato Control Center.app': 'elgato-control-center', 'Flycast.app': 'flycast@master'}
for a, t in OVERRIDE.items():
    if t in installed_casks: inst_app[a] = tok.get(t) or {'token': t, 'version': None}
SKIP = {'Keynote', 'Numbers', 'Pages', 'GarageBand', 'iMovie'}
def mdls(p):
    out = sh(f'mdls -name kMDItemLastUsedDate -name kMDItemUseCount -name kMDItemDateAdded {json.dumps(p)}')
    r = {}
    for k in ('kMDItemLastUsedDate', 'kMDItemUseCount', 'kMDItemDateAdded'):
        m = re.search(k + r'\s*=\s*(.+)', out)
        v = m.group(1).strip() if m else None
        if v in (None, '(null)'): v = None
        r[k] = v
    return r
apps = []
paths = sorted(glob.glob('/Applications/*.app') + glob.glob('/Applications/*/*.app') + glob.glob(os.path.expanduser('~/Applications/*.app')))
for p in paths:
    if '/Applications/Utilities/' in p: pass
    try: info = plistlib.load(open(p + '/Contents/Info.plist', 'rb'))
    except Exception: info = {}
    bid = info.get('CFBundleIdentifier', '')
    if os.path.islink(p): continue
    name = os.path.basename(p)
    if name[:-4] in SKIP: continue
    pkgs = sh('pkgutil --pkgs')
    ver = str(info.get('CFBundleShortVersionString') or info.get('CFBundleVersion') or '')
    cask = inst_app.get(name)
    mas = os.path.exists(p + '/Contents/_MASReceipt/receipt')
    pkg = next((l for l in pkgs.split() if name[:-4].replace(' ', '_') in l or (bid.startswith('us.zoom') and l.startswith('us.zoom')) or (bid.startswith('com.lucidlink') and l=='com.lucidlink') or (bid.startswith('com.microsoft') and bid.split('.')[-1].lower() in l.lower())), '')
    updater = []
    if info.get('SUFeedURL') or os.path.exists(p + '/Contents/Frameworks/Sparkle.framework'): updater.append('Sparkle')
    if os.path.exists(p + '/Contents/Frameworks/Squirrel.framework'): updater.append('Squirrel/Electron')
    if os.path.exists(p + '/Contents/Resources/app-update.yml'): updater.append('electron-updater')
    if 'google' in bid.lower() and 'chrome' in bid.lower(): updater.append('Google Updater')
    if bid.startswith('com.microsoft'): updater.append('Microsoft AutoUpdate')
    if mas: method = 'App Store'
    elif cask: method = 'Homebrew'
    elif pkg: method = 'Installer pkg'
    else: method = 'Direct download'
    avail = cask or app2cask.get(name)
    latest = None; src = None
    if avail:
        latest = str(avail['version']).split(',')[0] if avail.get('version') else None; src = 'Homebrew cask catalog'
    if mas:
        try:
            j = json.load(urllib.request.urlopen('https://itunes.apple.com/lookup?bundleId=' + urllib.parse.quote(bid), timeout=10))
            if j['results']: latest = j['results'][0]['version']; src = 'App Store'
        except Exception: pass
    md = mdls(p)
    apps.append(dict(kind='app', name=name[:-4], path=p, bundle_id=bid, version=ver, method=method,
        cask=(cask or {}).get('token'), in_brewfile=bool(cask and cask['token'] in inbrewfile),
        brew_available=(avail or {}).get('token'), brew_desc=(avail or {}).get('desc'), homepage=(avail or {}).get('homepage'),
        pkg=pkg or None, mas=mas, updater=updater, latest=latest, latest_source=src,
        last_used=md['kMDItemLastUsedDate'], use_count=md['kMDItemUseCount'], added=md['kMDItemDateAdded'],
        running=(p + '/Contents/MacOS/') in running, apple=bid.startswith('com.apple.'),
        mtime=datetime.datetime.fromtimestamp(os.stat(p).st_mtime).isoformat()))
json.dump(apps, open(f'{S}/data/apps.json', 'w'), indent=1)
print(len(apps))

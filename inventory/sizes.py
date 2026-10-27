import json, os, glob, subprocess
from concurrent.futures import ThreadPoolExecutor
S = os.path.dirname(os.path.abspath(__file__))
H = os.path.expanduser('~')
apps = json.load(open(f'{S}/data/apps.json'))
LIBDIRS = ['Application Support', 'Caches', 'Containers', 'Group Containers', 'Preferences', 'Logs', 'Saved Application State', 'HTTPStorages', 'WebKit', 'Cookies', 'LaunchAgents', 'Application Scripts']
entries = {d: os.listdir(f'{H}/Library/{d}') if os.path.isdir(f'{H}/Library/{d}') else [] for d in LIBDIRS}
EXTRA = {
 'Google Chrome': ['Library/Application Support/Google', 'Library/Caches/Google'],
 'ChatGPT': ['Library/Application Support/Codex', 'Library/Caches/Codex', 'Library/Caches/com.openai.codex', '.codex', '.cache/codex-runtimes'],
 'LM Studio': ['.cache/lm-studio', '.lmstudio'],
 'Docker': ['.docker', '.container-platform'],
 'Visual Studio Code': ['Library/Application Support/Code', '.vscode'],
 'Windsurf': ['.windsurf', '.codeium'],
 'OpenCode': ['Library/Application Support/ai.opencode.desktop', 'Library/Caches/ai.opencode.desktop.ShipIt', 'Library/Caches/@opencodedesktop-updater', 'Library/Caches/@opencode-aidesktop-updater', '.local/share/opencode', '.cache/opencode', '.config/opencode'],
 'Zenflow': ['Library/Caches/zenflow-desktop-updater'],
 'Effect House': ['Library/Application Support/EffectHouse'],
 'CHITUBOX': ['Library/Application Support/Chitubox_2025'],
 'AnycubicSlicer': ['Library/Application Support/AnycubicSlicer-Beta', 'Library/Caches/com.anycubic.anycubicslicer'],
 'Meshmixer': ['Library/Application Support/Autodesk'],
 'Cider': ['Library/Application Support/sh.cider.genten'],
 'Lucid': ['.lucid'],
 'Affinity Photo 2': ['Library/Group Containers/6LVTQB9699.com.seriflabs'],
 'Microsoft Word': ['Library/Group Containers/UBF8T346G9.Office', 'Library/Group Containers/UBF8T346G9.ms', 'Library/Group Containers/UBF8T346G9.OfficeOsfWebHost'],
 'Arduino IDE': ['Library/Arduino15', '.arduinoIDE', 'Documents/Arduino'],
 'Xcode': ['Library/Developer'],
 'Blender': ['Library/Application Support/Blender', '.cache/cycles'],
 'OBS': ['Library/Application Support/obs-studio'],
 'Ledge': ['.ledge'],
 'Discord': ['Library/Application Support/discord'],
 'Flycast': ['.local/share/flycast', '.config/flycast'],
}
NOTES = {'Affinity Photo 2': 'Includes the Serif group container shared by all three Affinity apps.', 'Microsoft Word': 'Includes the Office group container shared by all Microsoft 365 apps.',
 'ChatGPT': 'Includes Codex data, since the Codex agent ships inside ChatGPT.app.', 'Xcode': 'Includes ~/Library/Developer (DerivedData, device support, simulators).'}
claimed = set()
plan = {}
for a in apps:
    name, bid = a['name'], a['bundle_id'].lower()
    keys = {name.lower(), name.lower().replace(' ', '')}
    paths = [('App bundle', a['path'])]
    for rel in EXTRA.get(name, []):
        p = f'{H}/{rel}'
        if os.path.exists(p) and p not in claimed: claimed.add(p); paths.append((rel, p))
    for d, es in entries.items():
        for e in es:
            el = e.lower(); base = el[:-6] if el.endswith('.plist') else el
            if bid and (bid in el) or base in keys or (d == 'Saved Application State' and base == bid + '.savedstate'):
                p = f'{H}/Library/{d}/{e}'
                if p not in claimed: claimed.add(p); paths.append((f'Library/{d}/{e}', p))
    plan[name] = paths
def du(p):
    r = subprocess.run(['du', '-sk', p], capture_output=True, text=True).stdout.split()
    return int(r[0]) * 1024 if r else 0
allp = sorted({p for v in plan.values() for _, p in v})
with ThreadPoolExecutor(8) as ex: sz = dict(zip(allp, ex.map(du, allp)))
out = {}
for name, paths in plan.items():
    parts = [{'label': l, 'path': p.replace(H, '~'), 'bytes': sz[p]} for l, p in paths]
    parts = [x for x in parts if x['bytes'] > 0 or x['label'] == 'App bundle']
    parts.sort(key=lambda x: -x['bytes'])
    out[name] = {'total': sum(x['bytes'] for x in parts), 'parts': parts, 'note': NOTES.get(name)}
json.dump(out, open(f'{S}/data/app_sizes.json', 'w'), indent=1)
for k, v in sorted(out.items(), key=lambda kv: -kv[1]['total'])[:25]: print(f"{v['total']/1e9:7.2f} GB  {k}  ({len(v['parts'])} parts)")

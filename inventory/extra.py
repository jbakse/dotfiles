# Download source, Where-From and copyright for each app in data/apps.json
import json, os, subprocess
S = os.path.dirname(os.path.abspath(__file__))
out = {}
for x in json.load(open(f'{S}/data/apps.json')):
    p = x['path']
    q = subprocess.run(['xattr', '-p', 'com.apple.quarantine', p], capture_output=True, text=True).stdout.strip()
    w = subprocess.run(['mdls', '-raw', '-name', 'kMDItemWhereFroms', p], capture_output=True, text=True).stdout.strip()
    c = subprocess.run(['plutil', '-extract', 'NSHumanReadableCopyright', 'raw', p + '/Contents/Info.plist'], capture_output=True, text=True).stdout.strip()
    out[x['name']] = {'quarantine': q.split(';')[2] if q.count(';') >= 2 else None, 'wherefrom': None if w == '(null)' else w, 'copyright': c or None}
json.dump(out, open(f'{S}/data/extra.json', 'w'), indent=1)

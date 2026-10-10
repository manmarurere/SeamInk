"""SeamInk (Penumbra auto version) launcher.

Serves seamink.html and answers, read-only, "which file does Penumbra currently use
for this game path?" for the collection the player uses. The page then loads the
body models, follows their material to the skin texture, and loads that.
Nothing is ever written. Only .mdl / .mtrl / .tex / .png files inside the
Penumbra mod folder can be read.
"""
import http.server
import json
import os
import socket
import sys
import threading
import time
import urllib.parse
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
SERVED_EXT = {'.mdl', '.mtrl', '.tex', '.png'}


def load_json(path):
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f)


# ---------------------------------------------------------------- Penumbra config
def penumbra_dirs():
    """Candidate Penumbra config folders (XIVLauncher, or one given with --penumbra)."""
    out = []
    for i, a in enumerate(sys.argv):
        if a == '--penumbra' and i + 1 < len(sys.argv):
            out.append(sys.argv[i + 1])
    appdata = os.environ.get('APPDATA', '')
    for launcher in ('XIVLauncher', 'XIVLauncherCN', 'XIVLauncher-KR'):
        out.append(os.path.join(appdata, launcher, 'pluginConfigs', 'Penumbra'))
    return [d for d in out if os.path.isdir(d)]


def find_mod_directory(cfg_dir):
    for p in (os.path.join(cfg_dir, 'config', 'penumbra.json'), os.path.join(os.path.dirname(cfg_dir), 'Penumbra.json'),
              os.path.join(os.path.dirname(cfg_dir), 'Penumbra.json.bak')):
        try:
            d = load_json(p).get('ModDirectory')
            if d and os.path.isdir(d):
                return d
        except Exception:
            pass
    return None


def read_collections(cfg_dir):
    cols = {}
    folder = os.path.join(cfg_dir, 'collections')
    for n in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not n.endswith('.json'):
            continue
        try:
            c = load_json(os.path.join(folder, n))
        except Exception:
            continue
        cid = str(c.get('Id') or n[:-5])
        c['_file'] = os.path.join(folder, n)
        cols[cid] = c
    return cols


def default_collection(cfg_dir, cols):
    try:
        a = load_json(os.path.join(cfg_dir, 'active_collections.json'))
    except Exception:
        a = {}
    for key in ('Yourself', 'Current', 'Default'):
        v = a.get(key)
        if v:
            for cid, c in cols.items():
                if v in (cid, c.get('Name')):
                    return cid
    return next(iter(cols), None)


def effective_settings(cols, cid, seen=None):
    """Mod settings of a collection, falling back to the collections it inherits from."""
    seen = seen or set()
    if cid not in cols or cid in seen:
        return {}
    seen.add(cid)
    own = dict(cols[cid].get('Settings') or {})
    for parent in cols[cid].get('Inheritance') or []:
        pid = next((k for k, c in cols.items() if parent in (k, c.get('Name'))), None)
        for mod, st in effective_settings(cols, pid, seen).items():
            own.setdefault(mod, st)
    return own


# ---------------------------------------------------------------- mod contents
def read_mod(mod_dir):
    """(name, default option, groups) of a Penumbra mod, whichever layout it uses."""
    meta = {}
    try:
        meta = load_json(os.path.join(mod_dir, 'meta.json'))
    except Exception:
        pass
    names = os.listdir(mod_dir)
    group_files = sorted(n for n in names if n.startswith('group_') and n.endswith('.json'))
    if group_files:
        groups = [load_json(os.path.join(mod_dir, n)) for n in group_files]
    elif meta.get('Groups'):
        groups = meta['Groups']
    else:
        groups = [load_json(os.path.join(mod_dir, n)) for n in sorted(n for n in names if n.startswith('group_') and n.endswith('.json.bak'))]
    default = meta.get('DefaultMod') or {}
    for n in ('default_mod.json', 'default_mod.json.bak'):
        if not default and n in names:
            default = load_json(os.path.join(mod_dir, n))
    return meta.get('Name') or os.path.basename(mod_dir), default, groups


def chosen_containers(group, value):
    """The option dicts a group setting selects."""
    opts = group.get('Options') or []
    kind = group.get('Type')
    if kind == 'Single':
        return [opts[value]] if 0 <= value < len(opts) else []
    if kind == 'Combining':
        conts = group.get('Containers') or []
        return [conts[value]] if 0 <= value < len(conts) else []
    if kind == 'Multi':
        return [o for i, o in enumerate(opts) if value >> i & 1]
    return []  # Imc and unknown kinds don't swap files


class Resolver:
    """Game path -> file, as Penumbra would pick it for one collection."""

    def __init__(self, mod_root, settings):
        self.files, self.swaps = {}, {}
        for folder, st in settings.items():
            if not st.get('Enabled'):
                continue
            mod_dir = os.path.join(mod_root, folder)
            if not os.path.isdir(mod_dir):
                continue
            try:
                name, default, groups = read_mod(mod_dir)
            except Exception as e:
                print('Skipped an unreadable mod / 読めないmodを飛ばしました:', folder, e)
                continue
            prio = int(st.get('Priority', 0))
            picks = [('', default)]
            for g in groups:
                value = (st.get('Settings') or {}).get(g.get('Name'), g.get('DefaultSettings', 0))
                picks += [(f"{g.get('Name')}: {c.get('Name', '')}", c) for c in chosen_containers(g, int(value or 0))]
            for label, c in picks:
                for gp, rel in (c.get('Files') or {}).items():
                    self._add(self.files, gp, prio, (folder, name, label, rel.replace('\\', '/')))
                for gp, target in (c.get('FileSwaps') or {}).items():
                    self._add(self.swaps, gp, prio, (folder, name, label, target))

    @staticmethod
    def _add(table, gp, prio, value):
        key = gp.replace('\\', '/').lower()
        if key not in table or prio > table[key][0]:
            table[key] = (prio, value)

    def resolve(self, gp, depth=0):
        key = gp.replace('\\', '/').lower()
        if key in self.files:
            folder, name, label, rel = self.files[key][1]
            return {'gamePath': key, 'found': True, 'folder': folder, 'mod': name, 'option': label, 'file': rel}
        if key in self.swaps and depth < 4:
            r = self.resolve(self.swaps[key][1][3], depth + 1)
            r['gamePath'] = key
            return r
        return {'gamePath': key, 'found': False}


STATE = {'cache': {}}


ERRORS = {  # code -> message for the console; the page translates the code itself
    'no_config': "Penumbra's settings folder was not found / Penumbraの設定フォルダが見つかりません (XIVLauncher\\pluginConfigs\\Penumbra)",
    'no_moddir': "Penumbra's mod folder (ModDirectory) was not found / Penumbraのmodフォルダが見つかりません",
    'no_collections': 'No Penumbra collections were found / Penumbraのコレクションが見つかりません',
}


class PenumbraError(RuntimeError):
    def __init__(self, code):
        super().__init__(ERRORS[code])
        self.code = code


def fail(code):
    return {'ok': False, 'code': code, 'error': ERRORS[code]}


def penumbra_info():
    dirs = penumbra_dirs()
    if not dirs:
        return fail('no_config')
    cfg = dirs[0]
    mod_root = find_mod_directory(cfg)
    if not mod_root:
        return fail('no_moddir')
    cols = read_collections(cfg)
    if not cols:
        return fail('no_collections')
    return {'ok': True, 'config': cfg, 'modDirectory': mod_root, 'default': default_collection(cfg, cols),
            'collections': [{'id': k, 'name': c.get('Name') or k} for k, c in cols.items()], '_cols': cols}


def resolver_for(cid):
    info = penumbra_info()
    if not info['ok']:
        raise PenumbraError(info['code'])
    cols = info['_cols']
    cid = cid if cid in cols else info['default']
    stamp = (cid, os.path.getmtime(cols[cid]['_file']))
    if STATE['cache'].get('stamp') != stamp:
        t = time.time()
        STATE['cache'] = {'stamp': stamp, 'resolver': Resolver(info['modDirectory'], effective_settings(cols, cid)), 'root': info['modDirectory']}
        print(f"Loaded collection / コレクションを読み込みました: {cols[cid].get('Name', cid)} ({time.time() - t:.1f}s)")
    return STATE['cache']['resolver'], STATE['cache']['root']


# ---------------------------------------------------------------- http
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_bytes(self, code, body, ctype):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, obj, code=200):
        self.send_bytes(code, json.dumps(obj, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path, q = urllib.parse.unquote(url.path), urllib.parse.parse_qs(url.query)
        try:
            if path in ('/', '/seamink.html'):
                with open(os.path.join(HERE, 'seamink.html'), 'rb') as f:
                    return self.send_bytes(200, f.read(), 'text/html; charset=utf-8')
            if path == '/api/penumbra':
                info = penumbra_info()
                info.pop('_cols', None)
                return self.send_json(info)
            if path == '/api/resolve':
                res, root = resolver_for((q.get('collection') or [''])[0])
                out = []
                for gp in q.get('path', []):
                    r = res.resolve(gp)
                    if r['found']:
                        r['localPath'] = os.path.join(root, r['folder'], r['file'].replace('/', os.sep))
                        r['url'] = '/file?' + urllib.parse.urlencode({'mod': r['folder'], 'rel': r['file']})
                    out.append(r)
                return self.send_json({'results': out})
            if path == '/file':
                _, root = resolver_for('')
                folder, rel = (q.get('mod') or [''])[0], (q.get('rel') or [''])[0]
                mod_dir = os.path.normpath(os.path.join(root, folder))
                full = os.path.normpath(os.path.join(mod_dir, rel))
                ok = (os.path.dirname(mod_dir) == os.path.normpath(root) and folder and
                      os.path.commonpath([mod_dir, full]) == mod_dir and
                      os.path.splitext(full)[1].lower() in SERVED_EXT and os.path.isfile(full))
                if not ok:
                    return self.send_bytes(404, b'not found', 'text/plain')
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(os.path.getsize(full)))
                self.end_headers()
                with open(full, 'rb') as f:
                    while chunk := f.read(1 << 20):
                        self.wfile.write(chunk)
                return
            self.send_bytes(404, b'not found', 'text/plain')
        except Exception as e:
            self.send_json({'ok': False, 'code': getattr(e, 'code', None), 'error': str(e)}, 500)


def free_port(start=8770):
    for port in range(start, start + 30):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise SystemExit('No free port found / 空いているポートが見つかりません')


def main():
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    port = int(nums[0]) if nums else free_port()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    url = f'http://127.0.0.1:{port}/'
    print(f'Opening SeamInk / SeamInk を開いています: {url}')
    print('If the browser does not open, paste the address above into Chrome or Edge.')
    print('ブラウザが開かない時は、上のアドレスを Chrome か Edge に貼り付けてください。')
    print('Close this window when you are done. / 使い終わったら、このウィンドウを閉じてください。')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == '__main__':
    main()

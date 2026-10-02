"""Finalise an activity that Packet Tracer 8.0.0 has re-saved from a PT 4.1 original.

PT does the heavy lifting on load: it converts the three networks to the current device model and
regenerates the grading tree from the converted answer network, carrying the graded (checked) items
over by name. This script takes that re-saved file and
  1. checks it against the original: same graded-item count, every original graded item has a
     modern counterpart (prints the legacy -> modern name mapping, flags anything unmapped),
  2. resets the activity timer (ELAPSED) and makes the state-on-open equal the Reset state,
  3. restores graded items that PT silently dropped during conversion: for each original graded
     item without a counterpart, the modern path is derived (port and property renames, static
     route naming) and, if that node exists in the regenerated tree, it is checked again,
  4. re-encodes it with our codec (round-trip verified) under the delivery name.
Instruction text is left exactly as PT carried it over.

Usage: python3 tools/convert.py <original_4.1.pka> <pt800_saved.pka> <out.pka>
"""
import copy, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from lib import load, dump, nets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'tools', 'pkacli.js')

def decode(pka, xml):
    subprocess.run(['node', CLI, 'decode', pka, xml], check=True, stdout=subprocess.DEVNULL)
    return load(xml)

def graded(root):
    """{path: nodeValue} of checkType=2 leaves, path without the top 'Network' node."""
    out = {}
    def walk(n, p):
        nm = n.find('NAME'); q = p + '>' + (nm.text or ''); kids = n.findall('NODE')
        if not kids and nm.get('checkType') == '2': out[q.split('>', 2)[-1]] = nm.get('nodeValue')
        for c in kids: walk(c, q)
    walk(root.find('COMPARISONS/NODE'), '')
    return out

# Name changes between the 4.1 and the 8.0 grading trees, as observed in PT 8.0's own conversion.
RENAMES = [
    (r'^(.+?)>Ports>FastEthernet>', r'\1>Ports>FastEthernet0>'),          # PC / server NIC
    (r'>Connects to FastEthernet$', '>Connects to FastEthernet0'),
    (r'>Ports>([^>]+)>Power$', r'>Ports>\1>Port Status'),                 # per-port power
    (r'>DNS Server>Domain Name>(.+)$', r'>DNS Server>Resource Records>\1>A Records>Address'),
    (r'>Routes>Static Routes>.+$', '>Routes>Static Routes>Route#'),       # route names are now Route<n> (matched by value)
    (r'>Ports>([^>]+)>Clock Rate$', r'>Ports>\1>Clock Rate'),
]
def modern_name(legacy):
    for pat, rep in RENAMES:
        legacy = re.sub(pat, rep, legacy)
    return legacy

def node_index(root):
    """{path: NODE element} for every node of the grading tree (path without the top 'Network')."""
    idx = {}
    def walk(n, p):
        nm = n.find('NAME'); q = p + '>' + (nm.text or '')
        idx[q.split('>', 2)[-1]] = n
        for c in n.findall('NODE'): walk(c, q)
    walk(root.find('COMPARISONS/NODE'), '')
    return idx

def wildcard(mask):
    return '.'.join(str(255 - int(o)) for o in mask.split('.'))

def candidates(legacy_path, legacy_value, idx):
    """Modern leaf paths that could carry this legacy graded item.
    Route-like lists (static routes, RIP and OSPF networks) are named Route<n> in modern trees and
    identified by value; OSPF networks switched from subnet mask to wildcard mask."""
    want = modern_name(legacy_path)
    parent, leaf = want.rsplit('>', 1)
    if '>Networks' in parent or parent.endswith('Static Routes'):
        if parent.endswith('Static Routes'): parent = parent  # already renamed by RENAMES
        values = {legacy_value or ''}
        if 'OSPF' in parent and legacy_value:
            parts = legacy_value.split()
            if len(parts) == 3: values.add(f'{parts[0]} {wildcard(parts[1])} {parts[2]}')
        if '>RIP>' in parent and not legacy_value:
            values.add(legacy_path.rsplit('>', 1)[1])
        hits = []
        for m, n in idx.items():
            if m.rsplit('>', 1)[0] != parent or n.findall('NODE'): continue
            v = n.find('NAME').get('nodeValue') or ''
            if any(v == x or (x and v.startswith(x + '-')) for x in values if x): hits.append(m)
        hits.sort(key=lambda m: ('(deprecated)' in m, m))      # prefer the non-deprecated node
        return hits
    return [want] if want in idx and not idx[want].findall('NODE') else []

def enable(node):
    node.find('NAME').set('checkType', '2')
    if not (node.findtext('COMPONENTS') or '').strip(): node.find('COMPONENTS').text = 'Other'
    if node.findtext('POINTS') in (None, ''): node.find('POINTS').text = '0'

def fix_parents(top):
    """Qt tri-state: 0 none, 1 some descendants, 2 all."""
    kids = top.findall('NODE')
    if not kids: return top.find('NAME').get('checkType')
    st = [fix_parents(k) for k in kids]
    v = '2' if all(x == '2' for x in st) else ('1' if any(x != '0' for x in st) else '0')
    top.find('NAME').set('checkType', v); return v

def check(orig_root, new_root):
    lg, mg = graded(orig_root), graded(new_root)
    report = {'legacy': len(lg), 'modern': len(mg), 'mapped': [], 'unmapped': [], 'extra': []}
    unused = set(mg)
    for lp in lg:
        want = modern_name(lp)
        cands = [m for m in unused if m == want or (want.endswith('Route#') and m.startswith(want[:-6]))]
        if cands:
            m = cands[0]; unused.discard(m); report['mapped'].append((lp, m, mg[m]))
        else:
            report['unmapped'].append(lp)
    report['extra'] = sorted(unused)
    return report

def convert(orig, saved, out):
    with tempfile.TemporaryDirectory() as td:
        o = decode(orig, os.path.join(td, 'o.xml')); n = decode(saved, os.path.join(td, 'n.xml'))
        assert n.tag == 'PACKETTRACER5_ACTIVITY', n.tag
        rep = check(o, n)
        lg = graded(o); idx = node_index(n); rep['restored'] = []; rep['lost'] = []
        for lp in rep['unmapped']:
            c = candidates(lp, lg[lp], idx)
            if c: enable(idx[c[0]]); rep['restored'].append((lp, c[0], idx[c[0]].find('NAME').get('nodeValue')))
            else: rep['lost'].append(lp)
        # PT checks "(deprecated) Route<n>" twins of route-like items; once the current node carries
        # the item, uncheck the deprecated twin so the item count equals the original's.
        rep['unchecked'] = []
        checked_now = {m for _, m, _ in rep['mapped']} | {m for _, m, _ in rep['restored']}
        for m in list(rep['extra']):
            if '(deprecated)' in m and m.replace('(deprecated) ', '') in checked_now:
                idx[m].find('NAME').set('checkType', '0'); rep['unchecked'].append(m); rep['extra'].remove(m)
        if rep['restored'] or rep['unchecked']: fix_parents(n.find('COMPARISONS/NODE'))
        rep['final'] = len(graded(n))
        nn = nets(n); assert len(nn) == 3
        n.replace(nn[0], copy.deepcopy(nn[1]))
        a = n.find('ACTIVITY'); a.set('ELAPSED', '0')
        x = os.path.join(td, 'out.xml'); open(x, 'wb').write(dump(n))
        subprocess.run(['node', CLI, 'encode', x, out], check=True, stdout=subprocess.DEVNULL)
    return rep

if __name__ == '__main__':
    orig, saved, out = sys.argv[1:4]
    rep = convert(orig, saved, out)
    print(f'{os.path.basename(out)}: graded legacy={rep["legacy"]} modern(PT)={rep["modern"]} '
          f'mapped={len(rep["mapped"])} restored={len(rep["restored"])} lost={len(rep["lost"])} '
          f'unchecked-deprecated={len(rep["unchecked"])} extra={len(rep["extra"])} final={rep["final"]}')
    for lp, m, v in rep['restored']: print(f'  RESTORED (PT dropped it): {lp}  ->  {m}  (expect {v!r})')
    for lp in rep['lost']: print('  LOST (no modern node):', lp)
    for m in rep['extra']: print('  EXTRA modern item (no legacy source):', m)
    for lp, m, v in rep['mapped']:
        if lp != m: print(f'  renamed: {lp}  ->  {m}  (expect {v!r})')

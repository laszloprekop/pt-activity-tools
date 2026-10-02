"""Make test variants of an activity file.

  solved:   the state on open (network 0) is replaced by the answer network (network 2), so
            Check Results must report 100% if the grading tree is consistent with the networks.
  fresh:    network 0 replaced by the reset network (network 1), timer reset (removes saved progress).

Works for legacy (PT 4.x, root PACKETTRACER_ACTIVITY) and modern (PACKETTRACER5_ACTIVITY) files;
the output keeps the container format of the input.

Usage: python3 tools/variants.py solved|fresh <in.pka> <out.pka>
"""
import copy, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from lib import load, dump, nets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'tools', 'pkacli.js')

def fmt(pka):
    out = subprocess.run(['node', CLI, 'info', pka], check=True, capture_output=True, text=True).stdout
    return 'legacy' if 'format: legacy' in out else 'modern'

def make(kind, src, dst):
    f = fmt(src)
    with tempfile.TemporaryDirectory() as td:
        xml = os.path.join(td, 'in.xml'); out = os.path.join(td, 'out.xml')
        subprocess.run(['node', CLI, 'decode', src, xml], check=True, stdout=subprocess.DEVNULL)
        root = load(xml); n = nets(root)
        assert len(n) == 3, 'expected 3 networks, got %d' % len(n)
        new = copy.deepcopy(n[2] if kind == 'solved' else n[1])
        root.replace(n[0], new)
        a = root.find('ACTIVITY')
        if a is not None and a.get('ELAPSED') is not None: a.set('ELAPSED', '0')
        open(out, 'wb').write(dump(root))
        subprocess.run(['node', CLI, 'encode' if f == 'modern' else 'encode-legacy', out, dst], check=True,
                       stdout=subprocess.DEVNULL)
    return f

if __name__ == '__main__':
    kind, src, dst = sys.argv[1:4]
    print(kind, make(kind, src, dst), '->', dst)

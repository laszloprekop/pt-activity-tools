#!/usr/bin/env python3
"""pka_fix: make old (Packet Tracer 4.x) activity files grade correctly in Packet Tracer 8.2+ and 9.x.

Packet Tracer 4.1 activity files (2007) store some graded items in a form that modern Packet Tracer
cannot grade, so Check Results stays red however correct the work is:

  1. Empty expected values: cable "Type", cable "Connects to ...", a PC's "DNS Server IP".
     PT 8.0.0 worked them out from the answer network; 8.2 and 9.x compare against the empty value.
  2. Old value formats: FastEthernet "Duplex"/"Bandwidth" stored as 1 (auto), OSPF
     "Passive Interface" stored as the interface name.
  3. OSPF network items: matched to the modern grading tree by an ID that uses a subnet mask where
     modern PT uses a wildcard mask, so modern PT silently drops them.

This script fixes all three from the file's own answer network and writes <name>_fixed.pka next to
the original. Nothing else in the file changes, and the original is never modified.
Standard library only; Python 3.8+.

Usage:
  python pka_fix.py <file.pka or folder> [...]     fix the files (a folder: every .pka in it)
  python pka_fix.py --check <file.pka> [...]       report what would be fixed, write nothing
"""
import os, re, sys, zlib
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- legacy container (PT 4.x/5.x)
# byte[i] ^= (len - i) & 0xff, then a 4-byte big-endian size and a zlib stream.

def decode_legacy(data):
    n = len(data)
    plain = bytes(b ^ ((n - i) & 0xFF) for i, b in enumerate(data))
    size = int.from_bytes(plain[:4], 'big')
    xml = zlib.decompress(plain[4:])
    if len(xml) != size: raise ValueError('size mismatch')
    return xml

def encode_legacy(xml):
    body = len(xml).to_bytes(4, 'big') + zlib.compress(xml)
    n = len(body)
    return bytes(b ^ ((n - i) & 0xFF) for i, b in enumerate(body))

# ---------------------------------------------------------------- XML with control characters
# Router banners hold ^C (0x03), stored raw or as &#x3;. Both are invalid XML 1.0: swap them for a
# placeholder while parsing and put the raw byte back on output (Packet Tracer accepts the byte).

_RAW = re.compile(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]')
_REF = re.compile(rb'&#(?:x0*([0-9A-Fa-f]{1,2})|0*(\d{1,2}));')

def parse(xml):
    s = xml.rstrip(b'\x00')
    s = _RAW.sub(lambda m: b'@@C%02X@@' % m.group(0)[0], s)
    def ref(m):
        c = int(m.group(1), 16) if m.group(1) else int(m.group(2))
        return b'@@C%02X@@' % c if (c < 0x20 and c not in (9, 10, 13)) else m.group(0)
    return ET.fromstring(_REF.sub(ref, s))

def serialize(root):
    out = ET.tostring(root, encoding='utf-8', xml_declaration=False)
    return re.sub(rb'@@C([0-9A-F]{2})@@', lambda m: bytes([int(m.group(1), 16)]), out)

# ---------------------------------------------------------------- the activity

def networks(root):
    return [c for c in root if c.tag in ('PACKETTRACER5', 'PACKETTRACER')]

def answer_network(root):
    return networks(root)[2]          # 0 = state on open, 1 = reset state, 2 = answer

def device_names(net):
    return [d.find('ENGINE').findtext('NAME') for d in net.iter('DEVICE')]

def find_device(net, name):
    for d in net.iter('DEVICE'):
        if d.find('ENGINE').findtext('NAME') == name: return d

def find_link(net, dev, port, other):
    names = device_names(net)
    for link in net.iter('LINK'):
        c = link.find('CABLE')
        if c is None: continue
        ends = [int(c.findtext('FROM')), int(c.findtext('TO'))]
        ports = [p.text for p in c.findall('PORT')]
        for i in (0, 1):
            if names[ends[i]] == dev and ports[i] == port and names[ends[1 - i]] == other:
                return link

def graded_items(root):
    """[(path, NODE)] of every graded leaf of the grading tree; path without the top 'Network'."""
    out = []
    def walk(node, path):
        name = node.find('NAME'); p = path + '>' + (name.text or ''); kids = node.findall('NODE')
        if not kids and name.get('checkType') == '2': out.append((p.split('>', 2)[-1], node))
        for k in kids: walk(k, p)
    walk(root.find('COMPARISONS/NODE'), '')
    return out

# Cable code of a link, as modern Packet Tracer stores it.
CABLE = {('eCopper', 'eStraightThrough'): '0 0',
         ('eCopper', 'eCrossOver'): '0 1',
         ('eSerial', None): '2'}

# A PC/server NIC was called "FastEthernet" in 4.x and is "FastEthernet0" now.
def modern_port(name):
    return 'FastEthernet0' if name == 'FastEthernet' else name

def empty_value(path, ans):
    """Expected value of an item whose stored value is empty, from the answer network."""
    parts = path.split('>'); leaf = parts[-1]
    if leaf.startswith('Connects to '):
        return 'Connects to ' + modern_port(leaf[len('Connects to '):])
    if leaf == 'Type' and len(parts) == 5 and parts[1] == 'Ports' and parts[3].startswith('Link to '):
        link = find_link(ans, parts[0], parts[2], parts[3][len('Link to '):])
        if link is None: return None
        return CABLE.get((link.findtext('TYPE'), link.find('CABLE').findtext('TYPE')))
    if leaf == 'DNS Server IP' and len(parts) == 2:
        d = find_device(ans, parts[0])
        return d.findtext('ENGINE/DNS_CLIENT/SERVER_IP') if d is not None else None
    return None

FAST_AUTO = {'Duplex': 'autoNegotiate=true isFullDuplex=true',
             'Bandwidth': 'autoNegotiate=true bandwidth=100000'}

def wildcard(mask):
    return '.'.join(str(255 - int(o)) for o in mask.split('.'))

def modern_value(path, value):
    """(new value, also set as ID?) for a stored value modern PT cannot use, else None."""
    parts = path.split('>'); leaf = parts[-1]
    if leaf in FAST_AUTO and value == '1' and len(parts) == 4 and parts[1] == 'Ports' \
            and parts[2].startswith('FastEthernet'):
        return FAST_AUTO[leaf], False
    if len(parts) >= 2 and parts[-2] == 'Passive Interface' and value == leaf:
        return '1', False
    if len(parts) >= 2 and parts[-2] == 'Networks' and '>OSPF>' in '>' + path:
        f = value.split()
        if len(f) == 3 and re.fullmatch(r'\d+\.\d+\.\d+\.\d+', f[1]) and int(f[1].split('.')[0]) >= 128:
            return f'{f[0]} {wildcard(f[1])} {f[2]}', True
    return None

# ---------------------------------------------------------------- warnings
# The fixes above cover what the 14 tested activities contain. Other files may hold old value
# formats this script can't see (a stored value looks fine until PT grades it). So every graded
# item of a kind that never occurred in the tested files is reported, plus known risky cases.

TESTED_KINDS = {
    'Console Line>Login', 'Console Line>Password', 'DNS Server IP', 'DNS Server>DNS Enable',
    'DNS Server>Domain Name><entry>', 'Default Gateway', 'HTTP Server>HTTP Enable', 'Host Name',
    'OSPF>Process ID <n>>Default Information', 'OSPF>Process ID <n>>Networks><entry>',
    'OSPF>Process ID <n>>Passive Interface><if>', 'Ports><port>>Bandwidth',
    'Ports><port>>Bandwidth Info', 'Ports><port>>Clock Rate', 'Ports><port>>Duplex',
    'Ports><port>>IP Address', 'Ports><port>>Link to <dev>>Connects to <port>',
    'Ports><port>>Link to <dev>>Type', 'Ports><port>>OSPF Cost', 'Ports><port>>Power',
    'Ports><port>>Subnet Mask', 'Power', 'RIP>Auto Summary', 'RIP>Networks><entry>', 'RIP>Version',
    'Routes>Static Routes><entry>', 'VTY Lines>VTY Line <n>>Login', 'VTY Lines>VTY Line <n>>Password',
}

def kind(path):
    """Item path with device, port, link and entry names generalized, e.g. 'Ports><port>>Duplex'."""
    parts = path.split('>')[1:]; out = []
    for i, x in enumerate(parts):
        prev = parts[i - 1] if i else ''
        if prev == 'Ports': x = '<port>'
        elif prev == 'Passive Interface': x = '<if>'
        elif prev in ('Networks', 'Static Routes', 'Domain Name', 'Resource Records'): x = '<entry>'
        elif x.startswith('Link to '): x = 'Link to <dev>'
        elif x.startswith('Connects to '): x = 'Connects to <port>'
        elif re.fullmatch(r'(Process ID|VTY Line) \d+', x): x = x.rsplit(' ', 1)[0] + ' <n>'
        out.append(x)
    return '>'.join(out)

def warnings(root):
    """[(path, reason)] for graded items the fixes may not cover."""
    out = []
    for path, node in graded_items(root):
        parts = path.split('>'); leaf = parts[-1]; value = node.find('NAME').get('nodeValue') or ''
        k = kind(path)
        if '>EIGRP>' in '>' + path and len(parts) >= 2 and parts[-2] == 'Networks':
            out.append((path, 'EIGRP network: probably the same subnet/wildcard mask mismatch as OSPF, not fixed'))
        elif leaf in FAST_AUTO and len(parts) == 4 and parts[1] == 'Ports' \
                and not (parts[2].startswith('FastEthernet') and value in ('1', FAST_AUTO[leaf])):
            out.append((path, f'{leaf} on {parts[2]} = {value!r}: only FastEthernet auto (1) is converted'))
        elif k == 'OSPF>Process ID <n>>Networks><entry>' and len(value.split()) != 3:
            out.append((path, f'OSPF network in an unexpected format {value!r}'))
        elif k not in TESTED_KINDS:
            out.append((path, 'kind of check not in the tested files: may need a rule, verify in PT'))
    return out

def fix(root):
    ans = answer_network(root); filled, converted, unknown = [], [], []
    for path, node in graded_items(root):
        name = node.find('NAME'); old = name.get('nodeValue')
        if not old:
            v = empty_value(path, ans)
            if v: name.set('nodeValue', v); filled.append(path)
            else: unknown.append(path)
            continue
        m = modern_value(path, old)
        if m:
            name.set('nodeValue', m[0])
            if m[1]: node.find('ID').text = m[0]
            converted.append(path)
    return filled, converted, unknown

# ---------------------------------------------------------------- command line

def process(src, check_only):
    data = open(src, 'rb').read()
    try:
        root = parse(decode_legacy(data))
        if root.tag != 'PACKETTRACER_ACTIVITY': raise ValueError(root.tag)
    except Exception:
        print(f'{src}: skipped, not an old (PT 4.x/5.x) activity file. Newer files need no fix.')
        return False
    version = root.findtext('VERSION')
    warn = warnings(root)                              # before fixing: judge the original values
    filled, converted, unknown = fix(root)
    print(f'{src}: PT {version}, {len(graded_items(root))} graded items, '
          f'filled {len(filled)}, converted {len(converted)}, unknown {len(unknown)}, warnings {len(warn)}')
    for p in unknown: print('   not handled (empty value of an unknown kind):', p)
    for p, why in warn: print(f'   WARNING {p}: {why}')
    if unknown or warn:
        print('   Check these in Packet Tracer: complete the activity (or load its answer network) and')
        print('   press Check Results. Anything still Incorrect needs a new rule in pka_fix.py.')
    if check_only: return True
    if not filled and not converted:
        print('   nothing to fix'); return True
    out_xml = serialize(root)
    if parse(decode_legacy(encode_legacy(out_xml))).tag != root.tag: raise RuntimeError('round trip')
    base, ext = os.path.splitext(src); out = base + '_fixed' + ext
    open(out, 'wb').write(encode_legacy(out_xml))
    print('   ->', out)
    return True

def main(argv):
    check = '--check' in argv
    args = [a for a in argv if a != '--check']
    if not args: print(__doc__); return 2
    files = []
    for a in args:
        if os.path.isdir(a):
            files += sorted(os.path.join(a, f) for f in os.listdir(a)
                            if f.lower().endswith('.pka') and not f.lower().endswith('_fixed.pka'))
        else: files.append(a)
    ok = all([process(f, check) for f in files])
    return 0 if ok else 1

if __name__ == '__main__':
    code = main(sys.argv[1:])
    if os.environ.get('PKA_FIX_PAUSE'): input('Press Enter to close')   # set by the .bat launcher
    sys.exit(code)

"""Print a readable summary of a Packet Tracer activity: version, instructions,
graded items (with expected values), and per-network devices, IPs and cables.

Usage: python3 tools/inspect_pka.py <file.pka | decoded.xml> [--no-text]
Works for both legacy (4.x/5.x) and modern (7.x/8.x) files.
"""
import html, os, re, subprocess, sys, tempfile
from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_xml(path):
    if path.endswith('.xml'):
        s = open(path, 'rb').read()
    else:
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as t: tmp = t.name
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'pkacli.js'), 'decode', path, tmp], check=True,
                       stdout=subprocess.DEVNULL)
        s = open(tmp, 'rb').read(); os.unlink(tmp)
    # Router banners use ^C (0x03), stored raw (modern) or as &#x3; (legacy). Both are invalid XML 1.0.
    s = re.sub(rb'&#x?0*3;', b'', s)
    s = re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]', b'', s)
    return s, etree.fromstring(s)

def main():
    path = sys.argv[1]; show_text = '--no-text' not in sys.argv
    raw, r = read_xml(path)
    print('PT version:', r.findtext('VERSION'))
    m = re.search(rb'<PAGE[^>]*>(.*?)</PAGE>', raw, re.S)
    if m and show_text:
        t = html.unescape(m.group(1).decode('utf-8', 'replace'))
        t = re.sub(r'<[^>]*>', ' ', t); t = re.sub(r'[ \t]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
        print('\n=== INSTRUCTIONS ===\n' + t.strip())
    print('\n=== GRADED ITEMS (checkType 2 leaves) ===')
    def walk(n, path):
        nm = n.find('NAME'); p = path + '>' + (nm.text or '')
        kids = n.findall('NODE')
        if not kids and nm.get('checkType') not in ('0', None):
            print('  ' + p.split('>', 2)[-1], '| expect:', nm.get('nodeValue'))
        for c in kids: walk(c, p)
    walk(r.find('COMPARISONS/NODE'), '')
    labels = ['state on open', 'state on Reset', 'answer key']
    for k, pt in enumerate([c for c in r if c.tag.startswith('PACKETTRACER')]):
        print(f'\n=== NETWORK {k} ({labels[k] if k < 3 else "?"}) ===')
        refs = {}; order = []
        for d in pt.iter('DEVICE'):
            e = d.find('ENGINE'); nm = e.findtext('NAME'); refs[e.findtext('SAVE_REF_ID')] = nm; order.append(nm)
            ips = [f"{p.findtext('IP')}/{p.findtext('SUBNET')}" for p in e.iter('PORT') if p.findtext('IP')]
            extra = ''
            if e.find('DNS_SERVER/ENABLED') is not None:
                extra = f" dns={e.findtext('DNS_SERVER/ENABLED')} http={e.findtext('HTTP_SERVER/ENABLED')}"
            print(f"  {e.find('TYPE').text:8} {nm:16} power={e.findtext('POWER')} gw={e.findtext('GATEWAY')} "
                  f"dns-client={e.findtext('DNS_CLIENT/SERVER_IP')} ips={ips}{extra}")
            for t in ('RUNNINGCONFIG',):
                c = e.find(t)
                if c is not None:
                    routes = [l.text for l in c.findall('LINE') if l.text and l.text.startswith('ip route')]
                    if routes: print('             routes:', routes)
        for l in pt.iter('LINK'):
            c = l.find('CABLE'); ports = [x.text for x in c.findall('PORT')]
            kind = [x.text for x in c.findall('TYPE')]
            def name(x):  # modern: save-ref-id; legacy: index into the device list
                if x in refs: return refs[x]
                return order[int(x)] if x and x.isdigit() and int(x) < len(order) else x
            a, b = name(c.findtext('FROM')), name(c.findtext('TO'))
            print(f"  cable {kind[-1] if kind else l.findtext('TYPE')}: {a} {ports[0]} <-> {b} {ports[1]}")

if __name__ == '__main__':
    main()

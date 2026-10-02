import re
from lxml import etree

# Router banners contain ^C (0x03). Modern files store it as a raw byte, legacy (4.x) files as the
# character reference &#x3;. Both are invalid in XML 1.0, so swap them for a placeholder before
# parsing and restore the raw byte on dump (PT's parser accepts the raw byte).
_RAW = re.compile(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]')
_REF = re.compile(rb'&#(?:x0*([0-9A-Fa-f]{1,2})|0*(\d{1,2}));')

def _placeholder(code):
    return b'@@C%02X@@' % code

def load(path):
    s = open(path, 'rb').read().rstrip(b'\x00')   # legacy files end with a NUL byte
    s = _RAW.sub(lambda m: _placeholder(m.group(0)[0]), s)
    def ref(m):
        code = int(m.group(1), 16) if m.group(1) else int(m.group(2))
        return _placeholder(code) if (code < 0x20 and code not in (9, 10, 13)) else m.group(0)
    s = _REF.sub(ref, s)
    return etree.fromstring(s)

def dump(root):
    out = etree.tostring(root, encoding='utf-8')
    return re.sub(rb'@@C([0-9A-F]{2})@@', lambda m: bytes([int(m.group(1), 16)]), out)

def nets(root):
    return [c for c in root if c.tag in ('PACKETTRACER5', 'PACKETTRACER')]

def dev(net, name):
    for d in net.iter('DEVICE'):
        if d.find('ENGINE').findtext('NAME') == name: return d

"""Rebuild legacy (PT 4.1) Skills Integration Challenge activities as PT 8.0-format XML.

Strategy (see HANDOFF.md): use the native 8.0 file 1.7.1 as a template. Its answer
network already contains the complete "standard lab" (R1-ISP, R2-Central, S1-Central,
PCs 1A/1B, Eagle_Server with DNS+HTTP). For each activity we:
  1. copy the template's answer network into both start networks (open + reset),
  2. apply per-activity "un-configure" edits to the start networks,
  3. switch on only the graded leaves in the COMPARISONS tree,
  4. replace the instruction HTML with the original activity's text (+ a note).

Usage (from the package root, after `npm install`):
    python3 tools/build.py            # all activities
    python3 tools/build.py 5.6.1      # one activity (substring match on the id)
Outputs: work/<id>.xml and build/<id>.pka
"""
import copy, html, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import load, dump, nets, dev, etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, 'samples', 'originals')
WORK = os.path.join(ROOT, 'work')
BUILD = os.path.join(ROOT, 'build')
CLI = os.path.join(ROOT, 'tools', 'pkacli.js')

def decode(pka, xml):
    if not os.path.exists(xml):
        subprocess.run(['node', CLI, 'decode', pka, xml], check=True)
    return xml

# ---------------------------------------------------------------- grading paths
# Separator is '>' because port names contain '/' (FastEthernet0/1).
L1A = '1A>Ports>FastEthernet0>Link to S1-Central'
L1B = '1B>Ports>FastEthernet0>Link to S1-Central'
LSV = 'Eagle_Server>Ports>FastEthernet0>Link to R1-ISP'
R2F = 'R2-Central>Ports>FastEthernet0/0>'
PC1B = [L1B + '>Type', L1B + '>Connects to FastEthernet0/2', '1B>Ports>FastEthernet0>IP Address',
        '1B>Ports>FastEthernet0>Subnet Mask', '1B>Default Gateway', '1B>DNS Server IP']
PC1A = [L1A + '>Type', L1A + '>Connects to FastEthernet0/1', '1A>Ports>FastEthernet0>IP Address',
        '1A>Ports>FastEthernet0>Subnet Mask', '1A>Default Gateway', '1A>DNS Server IP']
SV_LINK = [LSV + '>Type', LSV + '>Connects to FastEthernet0/0']
SV_IP = ['Eagle_Server>Ports>FastEthernet0>IP Address', 'Eagle_Server>Ports>FastEthernet0>Subnet Mask',
         'Eagle_Server>Default Gateway']
SV_SVC = ['Eagle_Server>DNS Server>DNS Enable',
          'Eagle_Server>DNS Server>Resource Records>eagle-server.example.com>A Records>Address',
          'Eagle_Server>HTTP Server>HTTP Enable']

# ---------------------------------------------------------------- start-state edits
def ref(d): return d.find('ENGINE').findtext('SAVE_REF_ID')

def remove_links(net, name):
    rid = ref(dev(net, name))
    for l in list(net.find('NETWORK/LINKS').findall('LINK')):
        if rid in (l.findtext('CABLE/FROM'), l.findtext('CABLE/TO')):
            l.getparent().remove(l)

def remove_device(net, name):
    """Device entry + its cables + its physical-workspace node (matched by UUID)."""
    d = dev(net, name)
    remove_links(net, name)
    guid = d.find('WORKSPACE/PHYSICAL').text.split(',')[-1]
    for u in list(net.iter('UUID_STR')):
        if u.text == guid:
            node = u.getparent(); node.getparent().remove(node)
    d.getparent().remove(d)

def clear_ip(net, name, dns=True):
    e = dev(net, name).find('ENGINE')
    for p in e.iter('PORT'):
        if p.findtext('IP'):
            p.find('IP').text = None; p.find('SUBNET').text = None
    e.find('GATEWAY').text = None
    if dns: e.find('DNS_CLIENT/SERVER_IP').text = None

def services_off(net):
    e = dev(net, 'Eagle_Server').find('ENGINE')
    d = e.find('DNS_SERVER'); d.find('ENABLED').text = '0'
    db = d.find('NAMESERVER-DATABASE')
    for rr in list(db): db.remove(rr)
    e.find('HTTP_SERVER/ENABLED').text = '0'

def power_off(net, name):
    dev(net, name).find('ENGINE/POWER').text = 'false'

def r2_unconfigure(net):
    """IOS devices rebuild state from RUNNINGCONFIG on load; edit config lines + port fields."""
    e = dev(net, 'R2-Central').find('ENGINE')
    p = [p for p in e.iter('PORT') if p.findtext('IP') == '172.16.255.254'][0]
    p.find('IP').text = None; p.find('SUBNET').text = None; p.find('POWER').text = 'false'
    for t in ('RUNNINGCONFIG', 'STARTUPCONFIG'):
        c = e.find(t); lines = c.findall('LINE')
        for i, l in enumerate(lines):
            if l.text == ' ip address 172.16.255.254 255.255.0.0':
                l.text = ' no ip address'
                j = i
                while lines[j + 1].text and lines[j + 1].text.startswith(' '): j += 1
                sd = etree.Element('LINE'); sd.text = ' shutdown'; sd.tail = lines[j].tail
                lines[j].addnext(sd)
            if l.text and l.text.startswith('ip route 0.0.0.0 0.0.0.0 10.10.10.6'):
                c.remove(l)

# ---------------------------------------------------------------- grading tree
def set_grading(root, paths):
    """checkType: 0 unchecked, 1 partial (some descendants), 2 checked (Qt tri-state)."""
    top = root.find('COMPARISONS/NODE')
    for nm in top.iter('NAME'):
        if nm.getparent().tag == 'NODE': nm.set('checkType', '0')
    for p in paths:
        n = top
        for seg in p.split('>'):
            nxt = [c for c in n.findall('NODE') if c.findtext('NAME') == seg]
            assert nxt, 'missing grading node: ' + p
            n = nxt[0]
        assert not n.findall('NODE'), 'not a leaf: ' + p
        n.find('NAME').set('checkType', '2')
        if not (n.findtext('COMPONENTS') or '').strip(): n.find('COMPONENTS').text = 'Other'
        if n.findtext('POINTS') in (None, ''): n.find('POINTS').text = '0'
    def fix(n):
        kids = n.findall('NODE')
        if not kids: return n.find('NAME').get('checkType')
        st = [fix(k) for k in kids]
        v = '2' if all(s == '2' for s in st) else ('1' if any(s != '0' for s in st) else '0')
        n.find('NAME').set('checkType', v); return v
    fix(top)

# ---------------------------------------------------------------- instructions
NOTE = ('<p><i>Rebuilt for Packet Tracer 8.0 and newer from the original 4.1 activity. '
        'Graded items and starting state match the original.</i></p>\n')

def page_html(xmlfile):
    s = open(xmlfile, 'rb').read().decode('utf-8', 'replace')
    h = html.unescape(re.search(r'<PAGE[^>]*>(.*?)</PAGE>', s, re.S).group(1))
    i = h.find('\n', h.find('</h2>')) + 1
    return h[:i] + NOTE + h[i:]

# ---------------------------------------------------------------- activities
def s271(net): remove_device(net, '1B')
def s351(net): remove_device(net, '1B'); remove_links(net, 'Eagle_Server'); services_off(net)
def s461(net):
    remove_links(net, '1A'); clear_ip(net, '1A')
    remove_links(net, 'Eagle_Server'); clear_ip(net, 'Eagle_Server', dns=False)
    services_off(net); power_off(net, 'Eagle_Server')
def s561(net): r2_unconfigure(net)

ACTIVITIES = {
    '2.7.1_Examining_Packets': ('2.7.1_PTSkills2_4.1.pka', s271, PC1B),
    '3.5.1_Configuring_Hosts_and_Services': ('3.5.1_PTSkills3_4.1.pka', s351, PC1B + SV_LINK + SV_SVC),
    '4.6.1_Application_and_Transport_Layers': ('4.6.1_PTSkills4_4.1.pka', s461,
                                               PC1A + ['Eagle_Server>Power'] + SV_LINK + SV_IP + SV_SVC),
    '5.6.1_Routing_IP_Packets': ('5.6.1_PTSkills5_4.1.pka', s561,
                                 [R2F + 'Port Status', R2F + 'IP Address', R2F + 'Subnet Mask',
                                  'R2-Central>Routes>Static Routes>Route0']),
}

def build(aid, src, start, grade, template_xml):
    legacy = decode(os.path.join(ORIG, src), os.path.join(WORK, aid + '.legacy.xml'))
    root = load(template_xml)
    n0, n1, ans = nets(root)          # 0 = state on open, 1 = state on Reset, 2 = answer key
    for old in (n0, n1):
        new = copy.deepcopy(ans); start(new); root.replace(old, new)
    set_grading(root, grade)
    a = root.find('ACTIVITY'); a.set('ELAPSED', '0')
    h = page_html(legacy)
    a.find('INSTRUCTIONS/PAGE').text = h
    a.find('INSTRUCTION_DIALOG/USER_NOTES').text = h
    out_xml = os.path.join(WORK, aid + '.xml')
    open(out_xml, 'wb').write(dump(root))
    subprocess.run(['node', CLI, 'encode', out_xml, os.path.join(BUILD, aid + '.pka')], check=True)

def build_clean_171(template_xml):
    """1.7.1 itself: reset the 'open' network to the 'reset' network (removes saved progress)."""
    root = load(template_xml); n = nets(root)
    root.replace(n[0], copy.deepcopy(n[1])); root.find('ACTIVITY').set('ELAPSED', '0')
    out_xml = os.path.join(WORK, '1.7.1_Introduction_to_Packet_Tracer.xml')
    open(out_xml, 'wb').write(dump(root))
    subprocess.run(['node', CLI, 'encode', out_xml, os.path.join(BUILD, '1.7.1_Introduction_to_Packet_Tracer.pka')], check=True)

if __name__ == '__main__':
    os.makedirs(WORK, exist_ok=True); os.makedirs(BUILD, exist_ok=True)
    tpl = decode(os.path.join(ORIG, '1.7.1_PTSkills1_8.0_template_with_saved_progress.pka'),
                 os.path.join(WORK, 'template_1.7.1.xml'))
    sel = sys.argv[1] if len(sys.argv) > 1 else ''
    if sel in '1.7.1': build_clean_171(tpl)
    for aid, (src, start, grade) in ACTIVITIES.items():
        if sel in aid:
            build(aid, src, start, grade, tpl); print('built', aid, len(grade), 'graded items')

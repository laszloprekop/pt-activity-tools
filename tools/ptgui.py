"""Drive a running Cisco Packet Tracer (macOS) through the Accessibility API, addressed by process id.

Why not AppleScript / System Events: every Packet Tracer version runs as a process named
"PacketTracer", and System Events re-resolves process references by name, so with two versions
running it silently talks to the wrong one. AXUIElementCreateApplication(pid) does not.

Usage (venv with pyobjc):
  .venv/bin/python tools/ptgui.py launch <8.0.0|8.2.2|9.0.1> <file.pka>   -> prints pid, does guest login
  .venv/bin/python tools/ptgui.py windows <pid>
  .venv/bin/python tools/ptgui.py dump <pid> [window-title-substring] [depth]
  .venv/bin/python tools/ptgui.py saveas <pid> </abs/path/out.pka>
  .venv/bin/python tools/ptgui.py check <pid> <screenshot.png>          -> presses Check Results, screenshots dialog
  .venv/bin/python tools/ptgui.py shot <pid> <out.png> [window-title-substring]
  .venv/bin/python tools/ptgui.py press <pid> <window-title-substring> <button-title>
  .venv/bin/python tools/ptgui.py quit <pid>
"""
import os, subprocess, sys, time
import ApplicationServices as AS
import Quartz
from AppKit import NSWorkspace, NSRunningApplication, NSApplicationActivateIgnoringOtherApps

APPS = {
    '7.2.2': '/Applications/Cisco Packet Tracer 7.7.2/Cisco Packet Tracer.app',   # folder name is a typo; installer says 7.2.2
    '8.0.0': '/Applications/Cisco Packet Tracer 8.0.0/Cisco Packet Tracer 8.0.app',
    '8.2.2': '/Applications/Cisco Packet Tracer 8.2.2/Cisco Packet Tracer 8.2.2.app',
    '9.0.1': '/Applications/Cisco Packet Tracer 9.0.1/Cisco Packet Tracer 9.0.1.app',
}
BUNDLE = {'7.2.2': 'com.netacad.PacketTracer7', '8.0.0': 'com.netacad.PacketTracer8.0.0', '8.2.2': 'com.netacad.PacketTracer8.2.2',
          '9.0.1': 'com.netacad.PacketTracer9.0.1'}

# ---------------------------------------------------------------- AX helpers
def attr(el, name):
    err, val = AS.AXUIElementCopyAttributeValue(el, name, None)
    return val if err == 0 else None

def role(el): return attr(el, 'AXRole') or ''
def title(el): return attr(el, 'AXTitle') or ''
def children(el): return list(attr(el, 'AXChildren') or [])
def value(el): return attr(el, 'AXValue')

def app(pid): return AS.AXUIElementCreateApplication(pid)

def windows(pid): return children_of_role(app(pid), 'AXWindow')

def children_of_role(el, r): return [c for c in children(el) if role(c) == r]

def find(el, pred, depth=12, _d=0):
    """Depth-first search for the first element satisfying pred."""
    if _d > depth: return None
    if pred(el): return el
    for c in children(el):
        f = find(c, pred, depth, _d + 1)
        if f is not None: return f
    return None

def find_all(el, pred, depth=12, _d=0, out=None):
    if out is None: out = []
    if _d > depth: return out
    if pred(el): out.append(el)
    for c in children(el): find_all(c, pred, depth, _d + 1, out)
    return out

def window(pid, sub):
    for w in windows(pid):
        if sub.lower() in title(w).lower(): return w
    return None

def press(el):
    err = AS.AXUIElementPerformAction(el, 'AXPress'); return err == 0

def set_value(el, v):
    return AS.AXUIElementSetAttributeValue(el, 'AXValue', v) == 0

def menu_item(pid, *path):
    """menu_item(pid, 'File', 'Save As ...')"""
    el = find(app(pid), lambda e: role(e) == 'AXMenuBar', depth=2)
    for i, name in enumerate(path):
        el = find(el, lambda e, n=name: role(e) in ('AXMenuBarItem', 'AXMenuItem') and title(e) == n, depth=3)
        if el is None: raise SystemExit('menu path not found at ' + name)
    return el

def dump(el, depth=6, _d=0, out=None):
    if out is None: out = []
    if _d > depth: return out
    r, t, v = role(el), title(el), value(el)
    vs = '' if v is None else (' value=%r' % (str(v)[:60],))
    if r not in ('AXGroup', 'AXScrollArea', 'AXSplitGroup', 'AXUnknown', 'AXLayoutArea') or t:
        out.append('  ' * _d + f'{r} {t!r}{vs}')
    for c in children(el): dump(c, depth, _d + 1, out)
    return out

# ---------------------------------------------------------------- keyboard via CGEvent to pid
KEYCODES = {'return': 36, 'tab': 48, 'escape': 53, 'g': 5, 's': 1, 'a': 0}
def key(pid, keycode, flags=0):
    for down in (True, False):
        ev = Quartz.CGEventCreateKeyboardEvent(None, keycode, down)
        Quartz.CGEventSetFlags(ev, flags)
        Quartz.CGEventPostToPid(pid, ev)
        time.sleep(0.05)

def type_text(pid, text):
    for ch in text:
        for down in (True, False):
            ev = Quartz.CGEventCreateKeyboardEvent(None, 0, down)
            Quartz.CGEventKeyboardSetUnicodeString(ev, len(ch), ch)
            Quartz.CGEventPostToPid(pid, ev)
            time.sleep(0.01)

# ---------------------------------------------------------------- screenshots
def window_ids(pid, sub=''):
    info = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    ids = []
    for w in info:
        if w.get('kCGWindowOwnerPID') == pid and sub.lower() in (w.get('kCGWindowName') or '').lower():
            ids.append((w['kCGWindowNumber'], w.get('kCGWindowName') or '', w.get('kCGWindowBounds')))
    return ids

def shot(pid, out, sub=''):
    ids = window_ids(pid, sub)
    if not ids:
        subprocess.run(['screencapture', '-x', out], check=True); return 'screen'
    wid = ids[0][0]
    subprocess.run(['screencapture', '-x', '-o', '-l', str(wid), out], check=True)
    return ids[0][1]

# ---------------------------------------------------------------- high level
def activate(pid):
    """Qt tool windows (PT Activity, dialogs) are hidden while the app is inactive, so activate first."""
    a = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
    if a is not None: a.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
    time.sleep(1)

def pid_of(version):
    """NSWorkspace's process list does not refresh without a run loop, so ask pgrep."""
    exe = 'Cisco Packet Tracer' if version.startswith('7.') else 'PacketTracer'
    r = subprocess.run(['pgrep', '-f', APPS[version] + '/Contents/MacOS/' + exe + '$'], capture_output=True, text=True)
    pids = [int(x) for x in r.stdout.split()]
    return max(pids) if pids else None

def launch(version, path):
    """Start PT <version> with <path>, do the guest login, wait for the main window. If that version
    is already running with this file open (e.g. a previous attempt), reuse it."""
    pid = pid_of(version)
    if pid:
        m = window(pid, 'Cisco Packet Tracer -')
        if m is None or not title(m).endswith(os.path.basename(path)):
            raise SystemExit(f'PT {version} already running (pid {pid}) with another file; quit it first')
    else:
        for _ in range(60):                  # a PT instance that is still shutting down would swallow the open
            if not pid_of(version): break
            time.sleep(1)
        pid = None
        for attempt in range(6):             # `open` right after a quit is sometimes swallowed: retry
            subprocess.run(['open', '-a', APPS[version], os.path.abspath(path)], check=True)
            for _ in range(40):
                time.sleep(1); pid = pid_of(version)
                if pid and (window(pid, 'Login') or window(pid, 'Cisco Packet Tracer -')): break
            if pid: break
            time.sleep(5)
        if not pid: raise SystemExit('PT did not start')
    activate(pid)
    for _ in range(90):                      # guest login: the web view exposes a "Guest Login" button
        w = window(pid, 'Login')
        if w is None: break
        b = find(w, lambda e: role(e) == 'AXButton' and 'guest' in title(e).lower(), depth=25)
        if b is not None and press(b): time.sleep(4)
        else: time.sleep(1)
    for _ in range(120):
        if window(pid, 'Cisco Packet Tracer -') and not window(pid, 'Login'): break
        time.sleep(1)
    time.sleep(4)
    return pid

def saveas(pid, out):
    """Save As into the folder the current file was opened from (the save panel defaults to it).
    The compact NSSavePanel treats a path in the name field as a literal name, so only the
    basename goes in; callers open the input file from the target folder."""
    activate(pid)
    out = os.path.abspath(out)
    if os.path.exists(out): os.remove(out)
    press(menu_item(pid, 'File', 'Save As ...'))
    for _ in range(30):
        w = window(pid, 'Save File')
        if w: break
        time.sleep(0.5)
    else: raise SystemExit('save panel did not appear')
    time.sleep(1)
    field = find(w, lambda e: role(e) == 'AXTextField', depth=6)
    set_value(field, os.path.basename(out)); time.sleep(0.5)
    press(find(w, lambda e: role(e) == 'AXButton' and title(e) == 'Save', depth=6))
    for _ in range(60):
        time.sleep(1)
        for x in windows(pid):   # confirmation boxes: "OK" after save, "Replace" on overwrite
            if title(x) in ('', 'Cisco Packet Tracer') and x is not window(pid, 'Cisco Packet Tracer -'):
                b = find(x, lambda e: role(e) == 'AXButton' and title(e) in ('Replace', 'OK', 'Yes'), depth=6)
                if b: press(b)
        if os.path.exists(out) and os.path.getsize(out) > 0 and not window(pid, 'Save File'):
            time.sleep(2); return out
    raise SystemExit('file was not written: ' + out)

def check(pid, out):
    activate(pid)
    w = window(pid, 'PT Activity')
    if w is None: raise SystemExit('PT Activity window not found')
    b = find(w, lambda e: role(e) == 'AXButton' and title(e) == 'Check Results', depth=10)
    if b is None: raise SystemExit('Check Results button not found')
    press(b); time.sleep(3)
    res = window(pid, 'Activity Results') or window(pid, 'Results')
    name = shot(pid, out, 'Results')
    txt = []
    if res is not None:
        for e in find_all(res, lambda e: role(e) in ('AXStaticText',), depth=8):
            v = value(e) or title(e)
            if v: txt.append(str(v))
    return name, txt

def quit_(pid):
    press(menu_item(pid, 'File', 'Exit')) if find(app(pid), lambda e: role(e)=='AXMenuItem' and title(e)=='Exit', depth=4) else None
    subprocess.run(['kill', str(pid)])

if __name__ == '__main__':
    cmd, *a = sys.argv[1:]
    if cmd == 'launch': print(launch(a[0], a[1]))
    elif cmd == 'windows':
        activate(int(a[0]))
        for w in windows(int(a[0])): print(repr(title(w)), role(w), attr(w, 'AXSubrole'))
    elif cmd == 'activate': activate(int(a[0]))
    elif cmd == 'dump':
        pid = int(a[0]); el = window(pid, a[1]) if len(a) > 1 else app(pid)
        print('\n'.join(dump(el, int(a[2]) if len(a) > 2 else 6)))
    elif cmd == 'saveas': print(saveas(int(a[0]), a[1]))
    elif cmd == 'check': print(check(int(a[0]), a[1]))
    elif cmd == 'shot': print(shot(int(a[0]), a[1], a[2] if len(a) > 2 else ''))
    elif cmd == 'press':
        w = window(int(a[0]), a[1]); b = find(w, lambda e: role(e) == 'AXButton' and title(e) == a[2], depth=12); print(press(b) if b else 'not found')
    elif cmd == 'quit': quit_(int(a[0]))
    elif cmd == 'pid': print(pid_of(a[0]))
    else: print(__doc__)

"""Windows counterpart of pttest.py: grade activities in Packet Tracer 9.0.1 and record the result.

One fresh Packet Tracer per file, with the file on the command line, so there is never an Open
dialog or a "save changes?" prompt. Needs a stored login ("Keep me logged in" ticked once), because
the login dialog would otherwise appear on every start. Everything goes through UI Automation
(no keystrokes or mouse), scoped to the PT process, so typing in other windows is harmless.
Don't click in Packet Tracer while it runs.

Usage: python tools/ptwin.py <out.json> [--probe "Dev>A>B"] <file.pka> [<file.pka> ...]
  --probe  also open that branch of the Assessment Items tree and record its rows
           (for checks deep in a long list, which PT does not expose until scrolled to)
"""
import json, os, subprocess, sys, threading, time
from pywinauto import Application

EXE = r"C:\Program Files\Cisco Packet Tracer 9.0.1\bin\PacketTracer.exe"

def log(*a): print(*a, flush=True)

def wait(fn, timeout, step=1.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = fn()
            if r: return r
        except Exception: pass
        time.sleep(step)

def press(ctrl):
    """Invoke in a thread: Invoke blocks while a modal window it opened is up."""
    threading.Thread(target=lambda: ctrl.invoke(), daemon=True).start()

def find(app, title_part):
    for w in app.windows():
        if title_part in w.window_text(): return w

def buttons(w, text):
    return [d for d in w.descendants(control_type='Button') if d.window_text() == text]

def read_branch(page, branch):
    """Collapse the tree, expand only Network>branch, return the rows under it."""
    def kids_named(name):
        return [d for d in page.descendants(control_type='TreeItem') if d.window_text() == name]
    for b in buttons(page, 'Expand/Collapse All'): press(b)          # collapse
    time.sleep(2)
    if len([d for d in page.descendants(control_type='TreeItem')]) > 40:
        for b in buttons(page, 'Expand/Collapse All'): press(b)      # it was collapsed: toggle twice
        time.sleep(2)
    node = None
    for part in ['Network'] + branch.split('>'):
        cands = kids_named(part)
        if not cands: return {'error': f'branch part not found: {part}'}
        node = cands[0]
        try: node.expand()
        except Exception: pass
        time.sleep(1)
    rows = [d.window_text() for d in node.descendants(control_type='TreeItem')]
    try: node.collapse()
    except Exception: pass
    for b in buttons(page, 'Expand/Collapse All'): press(b)
    time.sleep(2)
    return rows

def grade(path, probe=None):
    name = os.path.basename(path)
    p = subprocess.Popen([EXE, path], cwd=os.path.dirname(EXE))
    try:
        app = wait(lambda: Application(backend='uia').connect(process=p.pid), 60)
        if not app: return {'error': 'could not attach'}
        main = wait(lambda: find(app, name) or (find(app, 'Login') and 'login'), 120)
        if main == 'login': return {'error': 'login dialog: tick "Keep me logged in" once'}
        if not main: return {'error': 'file did not load'}
        btn = wait(lambda: next((b for w in app.windows() if w.handle != main.handle
                                 for b in buttons(w, 'Check Results')), None), 60)
        if not btn: return {'error': 'no Check Results button'}
        time.sleep(3)                                     # let the network settle
        press(btn)
        page = wait(lambda: next(c for c in main.children() if c.class_name() == 'CCheckAnswerPage'), 60)
        if not page: return {'error': 'no results page'}
        tab = next(d for d in page.descendants(control_type='TabItem') if d.window_text() == 'Assessment Items')
        tab.select(); time.sleep(2)
        def items(): return page.descendants(control_type='TreeItem')
        if not any(d.window_text() in ('Correct', 'Incorrect') for d in items()):
            for b in buttons(page, 'Expand/Collapse All'): press(b)
            time.sleep(2)
        if probe: probe_rows = read_branch(page, probe)
        it = [d.window_text() for d in items()]
        out = {'visible_correct': it.count('Correct'), 'visible_incorrect': it.count('Incorrect')}
        # Only rows on screen are exposed, so long lists are cut off. Filtered to incorrect
        # rows the list is short enough to read in full.
        for b in buttons(page, 'Show Incorrect Items'): press(b)
        time.sleep(2)
        if not any(d.window_text() == 'Incorrect' for d in items()):
            for b in buttons(page, 'Expand/Collapse All'): press(b)
            time.sleep(2)
        it = [d.window_text() for d in items()]
        out['incorrect_items'] = [it[i - 1] for i, t in enumerate(it) if t == 'Incorrect' and i]
        out['incorrect'] = len(out['incorrect_items'])
        if probe: out['probe'] = probe_rows
        return out
    finally:
        subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
        time.sleep(3)

if __name__ == '__main__':
    out, files = sys.argv[1], sys.argv[2:]
    probe = None
    if files and files[0] == '--probe': probe, files = files[1], files[2:]
    results = json.load(open(out)) if os.path.exists(out) else {}
    for f in files:
        f = os.path.abspath(f); n = os.path.basename(f); log('grade', n)
        try: r = grade(f, probe)
        except Exception as e: r = {'error': repr(e)}
        results[n] = r; log('  ->', r)
        json.dump(results, open(out, 'w'), indent=1)
        if 'login' in r.get('error', ''): sys.exit(r['error'])

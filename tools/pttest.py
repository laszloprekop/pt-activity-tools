"""Open an activity in a given Packet Tracer version, press Check Results, record what PT reports.

  .venv/bin/python tools/pttest.py <8.0.0|8.2.2|9.0.1> <file.pka> <out.json> [--saveas <name.pka>]

Writes JSON: {version, file, load_dialogs, score, item_count, rows:[[name,status,points,component,feedback]...],
              leaves:[[name,status,points]...], screenshot}. With --saveas, also saves the opened file from
PT into the same folder as <file.pka> under that name (PT converts old files to its own format on save).
Each run launches a fresh PT instance and quits it (guest login allows only a few saves per session).
"""
import json, os, re, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from ptgui import *

def texts(w, depth=8):
    out = []
    for e in find_all(w, lambda e: role(e) in ('AXStaticText', 'AXButton'), depth=depth):
        v = value(e) if role(e) == 'AXStaticText' else None
        t = str(v) if v else title(e)
        if t: out.append(f'{role(e)[2:]}:{t[:120]}')
    return out

def dialogs(pid, main_title):
    """Windows other than the main window and PT Activity: load warnings, message boxes."""
    out = []
    for w in windows(pid):
        t = title(w)
        if t.startswith('Cisco Packet Tracer -') or t.startswith('PT Activity') or t == 'Script Project Manager': continue
        out.append({'title': t, 'texts': texts(w)})
    return out

def results_rows(pid):
    """Rows of the Assessment Items table as [name, status, points, component, feedback].
    PT 8.0 exposes the tree as a flat run of AXGroup cells (5 per row); PT 9.x as AXOutline/AXRow/AXCell."""
    w = window(pid, 'Cisco Packet Tracer -')
    col = find(w, lambda e: role(e) == 'AXColumn' and title(e) == 'Assessment Items', depth=18)
    if col is not None:
        tree = attr(col, 'AXParent')
        cells = [title(c) for c in children(tree) if role(c) == 'AXGroup']
        return [cells[i:i + 5] for i in range(0, len(cells), 5)]
    for o in find_all(w, lambda e: role(e) == 'AXOutline', depth=18):
        rows = [c for c in children(o) if role(c) == 'AXRow']
        if rows and any(title(x) == 'Network' for r in rows[:1] for x in children(r)):
            return [[title(c) or (str(value(c)) if value(c) is not None else '') for c in children(r) if role(c) == 'AXCell'] for r in rows]
    return None

def run(version, path, out_json, saveas=None):
    path = os.path.abspath(path)
    pid = launch(version, path)
    rec = {'version': version, 'file': path, 'pid': pid}
    time.sleep(2)
    main = window(pid, 'Cisco Packet Tracer -')
    rec['main_title'] = title(main) if main else None
    rec['load_dialogs'] = dialogs(pid, rec['main_title'])
    for d in rec['load_dialogs']:          # dismiss message boxes so the test can continue
        wdl = window(pid, d['title']) if d['title'] else None
        for w in windows(pid):
            if title(w) == d['title']:
                b = find(w, lambda e: role(e) == 'AXButton' and title(e) in ('OK', 'Yes', 'Close', 'No'), depth=6)
                if b: press(b); d['dismissed_with'] = title(b)
    time.sleep(1)
    if saveas:
        rec['saved'] = saveas_(pid, os.path.join(os.path.dirname(path), saveas))
    # Check Results. The PT Activity window is only visible while PT is in front, so activate just for
    # the button press and hand focus back; the results live in the main window, readable in the background.
    place_windows(pid)
    activate(pid)
    act = window(pid, 'PT Activity')
    rec['activity_window'] = title(act) if act else None
    if act is None:
        restore_focus()
        rec['error'] = 'no PT Activity window'
    else:
        b = find(act, lambda e: role(e) == 'AXButton' and title(e) == 'Check Results', depth=10)
        press(b); restore_focus(); time.sleep(4)
        w = window(pid, 'Cisco Packet Tracer -')
        tab = find(w, lambda e: role(e) == 'AXRadioButton' and title(e) == 'Assessment Items', depth=14)
        if tab is None:                          # fall back: briefly in front
            activate(pid); tab = find(w, lambda e: role(e) == 'AXRadioButton' and title(e) == 'Assessment Items', depth=14); restore_focus()
        if tab is None: rec['error'] = 'no Assessment Items tab'
        else:
            press(tab); time.sleep(3)
            # PT's own totals: static texts 'Score' / 'Item Count' with values ': a/b' (order: score, item count)
            # 'Score : a/b' and 'Item Count : c/d' live deep in the results pane; take any element text
            vals = []; rec['slash_texts'] = []
            for e in find_all(w, lambda e: True, depth=30):
                for t in (title(e), value(e)):
                    t = '' if t is None else str(t)
                    m = re.match(r'^\s*:?\s*(\d+)\s*/\s*(\d+)\s*$', t)
                    if m: vals.append(m.group(1) + '/' + m.group(2)); rec['slash_texts'].append(role(e) + ':' + t)
            rec['totals'] = vals
            if len(vals) >= 2:
                rec['items_correct'], rec['items_total'] = [int(x) for x in vals[1].split('/')]
            rows = results_rows(pid) or []
            rec['rows_visible'] = rows
            # the outline only exposes rows on screen; the Incorrect filter makes the failures fit
            b2 = find(w, lambda e: role(e) == 'AXButton' and title(e) == 'Show Incorrect Items', depth=14)
            if b2 is not None:
                press(b2); time.sleep(2)
                best = []
                for _ in range(4):                      # the outline repopulates lazily; keep the longest read
                    rws = results_rows(pid) or []
                    if len(rws) > len(best): best = rws
                    time.sleep(1.5)
                rec['incorrect_rows'] = best
                rec['incorrect_items'] = [r[0] for r in rec['incorrect_rows'] if len(r) > 1 and r[1] == 'Incorrect']
            rec['leaves'] = [r[:3] for r in rows if len(r) >= 2 and r[1] in ('Correct', 'Incorrect')]
            rec['correct'] = rec.get('items_correct')
            rec['incorrect'] = (rec['items_total'] - rec['items_correct']) if 'items_total' in rec else None
            shotfile = out_json[:-5] + '.png'
            ids = window_ids(pid, 'Cisco Packet Tracer -')
            if ids: subprocess.run(['screencapture', '-x', '-o', '-l', str(ids[0][0]), shotfile]); rec['screenshot'] = shotfile
    restore_focus()
    subprocess.run(['kill', str(pid)]); time.sleep(2)
    json.dump(rec, open(out_json, 'w'), indent=1)
    return rec

def saveas_(pid, out):
    return saveas(pid, out)

if __name__ == '__main__':
    a = sys.argv[1:]
    sv = a[a.index('--saveas') + 1] if '--saveas' in a else None
    r = run(a[0], a[1], a[2], sv)
    print(json.dumps({k: v for k, v in r.items() if k not in ('rows',)}, indent=1))

"""Summarise tools/pttest.py runs: one row per (file, PT version) with PT's own item count
(correct/total), the expected graded-item count from the file's grading tree, load-time dialogs
and the names of items reported Incorrect.  When a run lacks the item count (older runs), it is
read from the run's screenshot with tools/ocr.py and written back into the JSON.
Usage: python3 tools/ptreport.py <runs-dir> [expected.json]"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
try:
    import ocr
except Exception:
    ocr = None

runs = sorted(glob.glob(os.path.join(sys.argv[1], '*.json')))
expected = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
rows = []
for r in runs:
    j = json.load(open(r))
    shot = os.path.join(os.path.dirname(r), os.path.basename(j['screenshot'])) if j.get('screenshot') else None
    if 'items_total' not in j and ocr and shot and os.path.exists(shot):
        t = ocr.totals(shot)
        if 'items' in t:
            a, b = t['items'].split('/'); j['items_correct'], j['items_total'] = int(a), int(b)
            j['correct'], j['incorrect'] = int(a), int(b) - int(a)
        if 'completed' in t: j['completed'] = t['completed']
        j['ocr'] = t
        json.dump(j, open(r, 'w'), indent=1)
    base = os.path.basename(j['file']); n = re.search(r'PTSkills(\d+)', base).group(1)
    exp = len(expected.get(n, [])) or None
    bad = j.get('incorrect_items') or [x[0] for x in j.get('leaves', []) if x[1] == 'Incorrect']
    rows.append((int(n), base, j['version'], j.get('correct'), j.get('incorrect'), exp, j.get('items_total'),
                 j.get('completed'), j.get('error'), bad, [d['title'] or '(untitled)' for d in j.get('load_dialogs', [])]))
rows.sort()
print(f"{'file':28} {'PT':6} {'ok':>3} {'bad':>3} {'exp':>4} {'tot':>4}  note")
for n, base, ver, ok, bad, exp, tot, done, err, badnames, dtitles in rows:
    note = err or ''
    if done is True: note += ' completed'
    if done is False: note += ' NOT-completed'
    if tot is not None and exp and tot != exp: note += f' ITEMS {tot}!={exp}'
    if badnames: note += ' incorrect: ' + ', '.join(badnames[:6]) + ('...' if len(badnames) > 6 else '')
    if dtitles: note += ' dialogs: ' + '; '.join(dtitles)
    print(f"{base:28} {ver:6} {ok if ok is not None else '-':>3} {bad if bad is not None else '-':>3} "
          f"{exp or '-':>4} {tot if tot is not None else '-':>4}  {note}")

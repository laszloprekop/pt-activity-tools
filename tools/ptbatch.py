"""Run tools/pttest.py over a plan file, one line per run:  <version> <file.pka> <out.json> [saveas-name]
Skips runs whose out.json exists. Kills stray PT instances of that version between runs."""
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import ptgui
plan = [l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
py = sys.executable
for row in plan:
    ver, f, out = row[:3]; extra = ['--saveas', row[3]] if len(row) > 3 else []
    if os.path.exists(out): print('skip', out); continue
    pid = ptgui.pid_of(ver)
    if pid: subprocess.run(['kill', str(pid)])
    for _ in range(60):
        if not ptgui.pid_of(ver): break
        time.sleep(1)
    t = time.time()
    r = subprocess.run([py, os.path.join(os.path.dirname(__file__), 'pttest.py'), ver, f, out] + extra,
                       capture_output=True, text=True, timeout=600)
    ok = os.path.exists(out)
    print(f'{ver} {os.path.basename(f)} {"ok" if ok else "FAILED"} {time.time()-t:.0f}s', flush=True)
    if not ok: print(r.stdout[-800:], r.stderr[-800:], flush=True)
    pid = ptgui.pid_of(ver)
    if pid: subprocess.run(['kill', str(pid)]); time.sleep(3)

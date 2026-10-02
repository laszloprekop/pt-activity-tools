# pt-activity-tools

Tools to decode, inspect, convert and test Cisco Packet Tracer `.pka` activity files, so that the course's old (PT 4.1) activities open and grade correctly in Packet Tracer 8.x and 9.x.

**Read `HANDOFF.md` first.** It documents the file formats, the grading tree, what each PT version does with the old files, the conversion pipeline and the test harness.

## Commands

```bash
npm install                                                    # twofish (pure JS)
/opt/homebrew/bin/python3.13 -m venv .venv && .venv/bin/pip install lxml pyobjc-framework-Cocoa pyobjc-framework-ApplicationServices pyobjc-framework-Quartz
node tools/pkacli.js info <file.pka>                           # format + PT version
node tools/pkacli.js decode <in.pka> <out.xml>
node tools/pkacli.js encode <in.xml> <out.pka>                 # modern format, verifies round trip
.venv/bin/python tools/inspect_pka.py <file.pka|xml> [--no-text]
.venv/bin/python tools/variants.py solved|fresh <in.pka> <out.pka>
.venv/bin/python tools/pttest.py <8.0.0|8.2.2|9.0.1> <file.pka> <out.json> [--saveas <name.pka>]
.venv/bin/python tools/convert.py <original.pka> <pt800-saved.pka> <out.pka>
.venv/bin/python tools/ptreport.py <runs-dir> [expected.json]
```

Use `.venv/bin/python`; the pyenv Python on this machine is broken (missing zlib).

## Rules

- Never modify `samples/originals/`.
- After any change to the codec or converter, re-run the conversion and the pttest checks for at least one file per PT version before claiming anything works.
- Edit XML through `tools/lib.py` (`load`/`dump`) so router banner control characters survive.
- GUI tests: one Packet Tracer version at a time, addressed by pid through `tools/ptgui.py`. Never script Packet Tracer through AppleScript/System Events by process name.
- Don't claim a file works in a PT version until a pttest run (or the user) has confirmed it.
- Keep instruction text exactly as in the original; no added notes.
- Writing style for docs, comments and messages: never use the em dash character. Use a comma, colon, parentheses or a separate sentence instead.

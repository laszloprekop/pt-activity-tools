# Handoff: Packet Tracer activity converter

## 1. Goal

László studies computer networking (Kurose and Ross, plus Cisco NetAcad "Skills Integration
Challenge" activities in Cisco Packet Tracer) in the LTU course Z0025E (Canvas course 614). The
course shares 14 `.pka` activity files (PTSkills 1 to 14) that were all saved by **Packet Tracer
4.1 (around 2007)**. They don't grade properly in current Packet Tracer.

**Project goal:** a repeatable tool that converts the old activities into a format that opens and
grades correctly in Packet Tracer 8.x and 9.x, with the instruction text unchanged, and a test
process that verifies every file in every version.

## 2. Status (2026-10-01)

Established with real Packet Tracer runs (sections 7 and 8), not by inspection alone:

- **All 14 originals are PT 4.1 legacy files.** They are in `samples/originals/canvas/` with their
  Canvas file ids in `SOURCE.md`. (The earlier "1.7.1 template" in `samples/originals/` is not an
  original: it is PTSkills1 after the student opened and saved it in PT 8.0.0.)
- **The container format is unchanged through 9.0.1.** Files saved by 9.0.1.0858 decode with the
  same Twofish/EAX scheme and the EAX tag verifies.
- **PT 8.0.0 converts a 4.1 activity well on load.** It rebuilds the grading tree from the converted
  answer network, carries the graded items over by name (including renames such as
  `FastEthernet` to `FastEthernet0`, `Power` to `Port Status`, `DNS Server>Domain Name>x` to
  `DNS Server>Resource Records>x>A Records>Address`, named static routes to `Route0`) and fills in
  the expected values. A "solved" copy of each original (state on open = answer network) reports
  "Item Count n/n" and "You completed the activity" in 8.0.0, with one exception: **OSPF network
  items** (`OSPF>Process ID 1>Networks>10.10.10.0 255.255.255.0 area0`) are dropped by both 8.0.0
  and 9.0.1 (PTSkills13: 80 of 89 kept, PTSkills14: 46 of 55), because the modern tree names them
  `Route<n>` with a wildcard mask value. Static routes and RIP networks survive through
  "(deprecated) Route<n>" twin nodes. `convert.py` restores the OSPF items by value. (An earlier
  reading that 8.0.0 dropped items in PTSkills 9 and 10 was an artefact: the results list only
  exposes the rows on screen to the Accessibility API; PT's own Item Count, read by OCR from the
  screenshot in `tools/ocr.py`, is the authoritative number.)
- **PT 9.0.1 fails to grade items whose expected value is empty in the 4.1 file.** The 4.1 tree
  stores `nodeValue=""` for link items (`Link to X>Type`, `Link to X>Connects to ...`), `DNS Server
  IP` on PCs, `Duplex`, and a few others. 9.0.1 keeps the empty value when it regenerates the tree
  and compares the student's value against it, so these items are *always* Incorrect. A solved copy
  of PTSkills8 (pure cabling) scores 0 of 20 in 9.0.1; PTSkills2 scores 3 of 6; PTSkills10 45 of 89.
  Items with a stored value (IP addresses, masks, gateways, OSPF networks) grade fine.
- **PT 8.2.2 has no guest mode.** Closing its login dialog ends with "Login Failed. Cisco Packet
  Tracer is shutting down." Scripted tests on 8.2.2 need a persisted login ("Keep me logged in").
  Not tested yet.
- **The fix that works:** let PT 8.0.0 open and re-save the original (it does the device and tree
  conversion), then `tools/convert.py` restores the graded items 8.0.0 dropped, resets the timer and
  re-encodes. The resulting file has VERSION 8.0.0.0212, stored expected values for every item, and
  therefore grades in 9.0.1 as well (a file the student saved in 9.0.1 from such a converted file
  kept all graded items and values).

**Deliverables:** `converted/<canvas name>_v8.pka` (14 files, README inside). Test results per file
and version: `tests/results.md`, raw run records `tests/runs/*.json`, conversion mapping report
`tests/convert.log`. Every converted file reaches its full item count in 8.0.0 and 9.0.1 when its
opening state is the answer network, and starts at 0 as delivered (PTSkills13: 9 items are
satisfied by the original's starting network in every version).

## 3. Package layout and quick start

```
HANDOFF.md                  this document
CLAUDE.md                   short project notes for Claude Code
package.json                Node dependency: twofish (pure JS)
.venv/                      Python 3.13 venv: lxml, pyobjc (create with the commands below)
tools/pka.js                codec: modern (Twofish/EAX) and legacy (XOR) containers
tools/pkacli.js             CLI: decode | encode | encode-legacy | info
tools/lib.py                XML load/dump (control characters, legacy &#x3; refs, trailing NUL)
tools/inspect_pka.py        readable summary: instructions, graded items, networks, cables
tools/variants.py           solved / fresh test variants of any activity (legacy or modern)
tools/convert.py            finalise a PT-8.0-re-saved activity (restore dropped items, timer, encode)
tools/ptgui.py              drive Packet Tracer on macOS through the Accessibility API (by pid)
tools/pttest.py             open a file in a PT version, press Check Results, record every item
tools/ptbatch.py            run pttest over a plan file
tools/ptreport.py           table of pttest results against the expected graded-item counts
tools/ocr.py                macOS Vision OCR of a results screenshot (Score, Item Count, completed)
tools/pipeline.sh           finalise all conversions, build their test variants and a test plan
tools/build.py              older template rebuild of PTSkills 1 to 5 (kept; superseded by convert.py)
samples/originals/canvas/   the 14 Canvas originals (never modify) + SOURCE.md
samples/originals/          the five files from the first chat session (1.7.1 is a PT 8.0 re-save)
samples/rebuilt/            the five template rebuilds from the first chat session
converted/                  the 14 converted deliverables, <canvas name>_v8.pka (+ README)
build/canvas/               scratch output of tools/pipeline.sh (ignored); identical to converted/
tests/results.md            results table of every pttest run; tests/runs/ holds the JSON records
```

```bash
npm install
/opt/homebrew/bin/python3.13 -m venv .venv && .venv/bin/pip install lxml pyobjc-framework-Cocoa pyobjc-framework-ApplicationServices pyobjc-framework-Quartz
node tools/pkacli.js info samples/originals/canvas/1_482161921_LSG01_PTSkills3.pka
.venv/bin/python tools/inspect_pka.py samples/originals/canvas/1_482161921_LSG01_PTSkills3.pka
.venv/bin/python tools/variants.py solved <in.pka> <out.pka>
.venv/bin/python tools/pttest.py 8.0.0 <file.pka> <out.json> [--saveas <name.pka>]
.venv/bin/python tools/convert.py <original.pka> <pt800-saved.pka> build/canvas/<name>_v8.pka
```

The system Python (pyenv 3.9) is broken on this Mac (missing zlib dylib); use the venv.

## 4. File formats

`.pka` (activity) and `.pkt` (network) share the same container. Two generations.

### 4.1 Legacy (PT 4.x, 5.x)

```
plain = byte[i] XOR ((len - i) & 0xFF)     for i in 0..len-1
plain = 4-byte big-endian uncompressed size + zlib stream (78 9C)
```
`encodeLegacy` / `decodeLegacy` in `tools/pka.js`. Root `<PACKETTRACER_ACTIVITY>`, networks
`<PACKETTRACER>`, `<VERSION>4.1</VERSION>`. The XML ends with a NUL byte and encodes `^C` in
router banners as `&#x3;` (both handled by `lib.py`).

### 4.2 Modern (verified on 8.0.0.0212 and 9.0.1.0858)

1. Deobfuscate: `s1[i] = in[len - 1 - i] XOR ((len - i*len) & 0xFF)` (reverses byte order).
2. Decrypt: Twofish-128, key `0x89` x16, EAX mode with nonce `0x10` x16; last 16 bytes are the tag.
3. Deobfuscate: `p[i] ^= (len - i) & 0xFF`.
4. Decompress: 4-byte big-endian size + zlib.

Encoding is the exact reverse; `pkacli.js encode` verifies the round trip. PT 8.0.0 also writes the
plain XML of every save to `Contents/MacOS/XMLDUMP.xml` inside its app bundle (a debug leftover).

## 5. XML structure (modern)

Root `<PACKETTRACER5_ACTIVITY>`: `VERSION`, three `PACKETTRACER5` networks (**[0] state on open,
[1] state after Reset Activity, [2] answer key**), `COMPARISONS` (grading tree), `INITIALSETUP`,
`LOCKINGTREE`, `OPTIONS`, `ACTIVITY` (attributes `ENABLED`, `PASS`, `ELAPSED`; children
`INSTRUCTIONS/PAGE` and `INSTRUCTION_DIALOG/USER_NOTES` with the same instruction HTML), and
more. 9.0.1 adds `START_TIMESTAMP` and about 370 new tree nodes (NTP, PTP, ACL filters).

### 5.1 The grading tree (`COMPARISONS`)

- A tree of `NODE`s with `NAME` (attributes `checkType`, `nodeValue`), `ID`, `COMPONENTS`,
  `POINTS`, child `NODE`s. PT regenerates it from the answer network on load and carries over
  which leaves are checked, matching by name.
- Devices are matched by name. `checkType`: `0` unchecked, `1` some descendants, `2` checked
  (graded leaves are `checkType="2"` leaves; ancestors are tri-state).
- `nodeValue` is the expected value. **9.0.1 compares against it; 8.0.0 recomputes it.** This is
  the whole 9.x problem with the 4.1 files (section 2).
- Paths use `>` as separator in our tools because port names contain `/`.

### 5.2 Legacy to modern name changes (as performed by PT 8.0.0)

| 4.1 name | 8.0 name |
|---|---|
| `<PC or server>>Ports>FastEthernet>...` | `...>Ports>FastEthernet0>...` |
| `...>Connects to FastEthernet` (link to a PC) | `...>Connects to FastEthernet0` |
| `...>Ports>X>Power` | `...>Ports>X>Port Status` |
| `Eagle_Server>DNS Server>Domain Name>host` | `...>DNS Server>Resource Records>host>A Records>Address` |
| `...>Routes>Static Routes>0.0.0.0/0: 10.10.10.6(0)` (value `0.0.0.0-0-10.10.10.6-0`) | `...>Static Routes>Route0` (value `0.0.0.0-0-10.10.10.6-0-1`) |

`tools/convert.py` (`RENAMES`) applies the same renames to find modern nodes for items 8.0.0 dropped.

## 6. Gotchas

1. **Control characters** (`^C` in banners): raw 0x03 in modern files, `&#x3;` in legacy files;
   `lib.py` swaps both for a placeholder and restores the raw byte on dump.
2. lxml collapses `<X></X>` to `<X/>`. Harmless: converted files open and grade.
3. **Two PT versions running at once:** every version is a process named `PacketTracer`.
   AppleScript/System Events resolves processes by name and will act on the wrong one (this
   happened once and saved a stray copy of a file). `tools/ptgui.py` uses the Accessibility API by
   pid instead. Run one version at a time anyway.
4. **Guest login:** 8.0.0 and 9.0.1 have a "Guest Login" button in a web view (found by title through
   AX) and allow only a few saves per session, so each test launches a fresh PT. 8.2.2 has no guest.
5. **Qt tool windows** (PT Activity, dialogs) are hidden while the app is inactive; activate by pid
   before reading them. The compact save panel treats a path in the name field as a literal name.
6. `open -a` issued while the previous PT instance is still exiting is swallowed; `ptgui.launch`
   waits and retries.
7. **IOS devices rebuild state from `RUNNINGCONFIG` on load**; PC and server settings live in fields.

## 7. Conversion pipeline

For each original `O`:

1. `pttest.py 8.0.0 O out.json --saveas O_pt800.pka`: PT 8.0.0 opens the 4.1 file, converts the
   networks and the tree, saves the modern file (and the run records what Check Results shows).
2. `convert.py O O_pt800.pka converted/<name>_v8.pka` (or `tools/pipeline.sh <workdir>` for all): verifies every original graded item has a
   modern counterpart, restores the ones 8.0.0 dropped when their node exists in the regenerated
   tree, prints the mapping and anything that cannot be graded any more, sets `ELAPSED=0`, makes
   network [0] equal network [1], re-encodes. Instructions are left exactly as PT carried them over.
3. Test (section 8).

## 8. Test harness and plan

`pttest.py` launches a PT version with a file, does the guest login, dismisses dialogs, presses
Check Results, opens Assessment Items, reads every row (name, Correct/Incorrect, points) through
the Accessibility API, screenshots the results view, and quits PT. `ptbatch.py` runs a plan file;
`ptreport.py` summarises runs against the file's own graded-item count.

For every file and every version the checks are:

1. **Solved variant** (`variants.py solved`) scores 100 % and the item count equals the original's.
   Any Incorrect row in a solved file is a defect of the file for that version.
2. **Fresh file** opens without a dialog, Check Results lists all items as Incorrect (0 %).
3. Save from that version and decode with `pkacli.js info` (container check).

Manual checks still worth doing once per version: instructions readable, Reset Activity, do one
activity by hand to 100 %.

## 9. Open questions

- 8.2.2 behaviour (needs a persisted login).
- PTSkills9: 8.0.0 maps the legacy static route to `Routes>(deprecated) Static Routes>(deprecated)
  Route0`; `convert.py` additionally checks `Routes>Static Routes>Route0`. Both are graded; verify
  neither stays Incorrect in 9.0.1.

## 10. Ground rules

- These are Cisco NetAcad course materials: personal and course study only; don't publish them.
- Never modify `samples/originals/`.
- Keep the instruction text as PT carries it over; no added notes.
- Never use the em dash character in docs, comments or messages.

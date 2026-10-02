# Handoff: Packet Tracer activity converter

## 1. Goal

László studies computer networking (Kurose and Ross, plus Cisco NetAcad "Skills Integration Challenge" activities in Cisco Packet Tracer) in the LTU course Z0025E (Canvas course 614). The course shares 14 `.pka` activity files (PTSkills 1 to 14) that were all saved by **Packet Tracer 4.1 (around 2007)**. They don't grade properly in current Packet Tracer.

**Project goal:** a repeatable tool that converts the old activities into a format that opens and grades correctly in Packet Tracer 8.x and 9.x, with the instruction text unchanged, and a test process that verifies every file in every version.

## 2. Status (2026-10-01)

Established with real Packet Tracer runs (sections 7 and 8), not by inspection alone:

- **All 14 originals are PT 4.1 legacy files.** They are in `samples/originals/canvas/` with their Canvas file ids in `SOURCE.md`. (The earlier "1.7.1 template" in `samples/originals/` is not an original: it is PTSkills1 after the student opened and saved it in PT 8.0.0.)
- **The container format is unchanged through 9.0.1.** Files saved by 9.0.1.0858 decode with the same Twofish/EAX scheme and the EAX tag verifies.
- **PT 8.0.0 converts a 4.1 activity well on load.** It rebuilds the grading tree from the converted answer network, carries the graded items over by name (including renames such as `FastEthernet` to `FastEthernet0`, `Power` to `Port Status`, `DNS Server>Domain Name>x` to `DNS Server>Resource Records>x>A Records>Address`, named static routes to `Route0`) and fills in the expected values. A "solved" copy of each original (state on open = answer network) reports "Item Count n/n" and "You completed the activity" in 8.0.0, with one exception: **OSPF network items** (`OSPF>Process ID 1>Networks>10.10.10.0 255.255.255.0 area0`) are dropped by both 8.0.0 and 9.0.1 (PTSkills13: 80 of 89 kept, PTSkills14: 46 of 55), because the modern tree names them `Route<n>` with a wildcard mask value. Static routes and RIP networks survive through "(deprecated) Route<n>" twin nodes. `convert.py` restores the OSPF items by value. (An earlier reading that 8.0.0 dropped items in PTSkills 9 and 10 was an artefact: the results list only exposes the rows on screen to the Accessibility API; PT's own Item Count, read by OCR from the screenshot in `tools/ocr.py`, is the authoritative number.)
- **PT 9.0.1 fails to grade items whose expected value is empty in the 4.1 file.** The 4.1 tree stores `nodeValue=""` for link items (`Link to X>Type`, `Link to X>Connects to ...`), `DNS Server IP` on PCs, `Duplex`, and a few others. 9.0.1 keeps the empty value when it regenerates the tree and compares the student's value against it, so these items are *always* Incorrect. A solved copy of PTSkills8 (pure cabling) scores 0 of 20 in 9.0.1; PTSkills2 scores 3 of 6; PTSkills10 45 of 89. Items with a stored value (IP addresses, masks, gateways, OSPF networks) grade fine.
- **PT 8.2.2 behaves exactly like 9.0.1** on every file (tested 2026-10-02 after the user logged in once with "Keep me logged in"; 8.2.2 has no guest mode, closing its login dialog quits the program). Same failing items on the originals, same OSPF loss, all converted files pass.
- **The fix that works, and the recommended one:** `pka-fix/pka_fix.py` corrects the 4.1 file directly (fills empty expected values from the answer network, rewrites old value formats, rewrites OSPF network IDs with wildcard masks) and keeps the 4.1 format, so the result opens and grades fully in 7.2.2, 8.0.0, 8.2.2 and 9.0.1. Output: `fixed/`. The earlier route (PT 8.0.0 re-save plus `tools/convert.py`, output `converted/`) also grades in 8.x and 9.x but produces 8.0-format files that 7.x cannot open.

**Deliverables:** `fixed/<canvas name>_fixed.pka` (14 files, README inside) is the recommended set, also published as the zip of GitHub release v1.0 (https://github.com/laszloprekop/pt-activity-tools/releases/tag/v1.0): produced by `pka-fix/pka_fix.py`, still in the 4.1 format, tested to grade fully in 7.2.2, 8.0.0, 8.2.2 and 9.0.1. `converted/<canvas name>_v8.pka` is the superseded set produced through a PT 8.0.0 re-save; it grades in 8.0.0, 8.2.2 and 9.0.1 but does not open in 7.x, so it is kept only as an independent cross-check. Test results: `tests/results.md`, raw records in `tests/runs*/`, conversion mapping report `tests/convert.log`.

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
fixed/                      the 14 recommended deliverables, <canvas name>_fixed.pka (+ README), made by pka-fix
converted/                  superseded set in 8.0 format, <canvas name>_v8.pka; kept as a cross-check of fixed/, not for students
pka-fix/                    pka_fix.py: fixes 4.1 files directly, no Packet Tracer needed (+ Windows .bat)
build/canvas/               scratch output of tools/pipeline.sh (ignored); identical to converted/
tests/results.md            results table of every pttest run; tests/runs/ holds the JSON records
docs/ptskills-compatibility-audit.html  source of the published audit page (https://claude.ai/artifact/FZkfnjgyWBaGhKg2aQmxYq)
docs/packet-tracer-ui-settings.md  how to stop PT rearranging windows and changing font sizes (Mac and Windows)
study/                      lab group knowledge: draft answers and notes per lab (study/README.md)
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
`encodeLegacy` / `decodeLegacy` in `tools/pka.js`. Root `<PACKETTRACER_ACTIVITY>`, networks `<PACKETTRACER>`, `<VERSION>4.1</VERSION>`. The XML ends with a NUL byte and encodes `^C` in router banners as `&#x3;` (both handled by `lib.py`).

### 4.2 Modern (verified on 8.0.0.0212 and 9.0.1.0858)

1. Deobfuscate: `s1[i] = in[len - 1 - i] XOR ((len - i*len) & 0xFF)` (reverses byte order).
2. Decrypt: Twofish-128, key `0x89` x16, EAX mode with nonce `0x10` x16; last 16 bytes are the tag.
3. Deobfuscate: `p[i] ^= (len - i) & 0xFF`.
4. Decompress: 4-byte big-endian size + zlib.

Encoding is the exact reverse; `pkacli.js encode` verifies the round trip. PT 8.0.0 also writes the plain XML of every save to `Contents/MacOS/XMLDUMP.xml` inside its app bundle (a debug leftover).

## 5. XML structure (modern)

Root `<PACKETTRACER5_ACTIVITY>`: `VERSION`, three `PACKETTRACER5` networks (**[0] state on open, [1] state after Reset Activity, [2] answer key**), `COMPARISONS` (grading tree), `INITIALSETUP`, `LOCKINGTREE`, `OPTIONS`, `ACTIVITY` (attributes `ENABLED`, `PASS`, `ELAPSED`; children `INSTRUCTIONS/PAGE` and `INSTRUCTION_DIALOG/USER_NOTES` with the same instruction HTML), and more. 9.0.1 adds `START_TIMESTAMP` and about 370 new tree nodes (NTP, PTP, ACL filters).

### 5.1 The grading tree (`COMPARISONS`)

- A tree of `NODE`s with `NAME` (attributes `checkType`, `nodeValue`), `ID`, `COMPONENTS`, `POINTS`, child `NODE`s. PT regenerates it from the answer network on load and carries over which leaves are checked, matching by name.
- Devices are matched by name. `checkType`: `0` unchecked, `1` some descendants, `2` checked (graded leaves are `checkType="2"` leaves; ancestors are tri-state).
- `nodeValue` is the expected value. **9.0.1 compares against it; 8.0.0 recomputes it.** This is the whole 9.x problem with the 4.1 files (section 2).
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

1. **Control characters** (`^C` in banners): raw 0x03 in modern files, `&#x3;` in legacy files; `lib.py` swaps both for a placeholder and restores the raw byte on dump.
2. lxml collapses `<X></X>` to `<X/>`. Harmless: converted files open and grade.
3. **Two PT versions running at once:** every version is a process named `PacketTracer`. AppleScript/System Events resolves processes by name and will act on the wrong one (this happened once and saved a stray copy of a file). `tools/ptgui.py` uses the Accessibility API by pid instead. Run one version at a time anyway.
4. **Guest login:** 8.0.0 and 9.0.1 have a "Guest Login" button in a web view (found by title through AX) and allow only a few saves per session, so each test launches a fresh PT. 8.2.2 has no guest.
5. **Qt tool windows** (PT Activity, dialogs) are hidden while the app is inactive; activate by pid before reading them. The compact save panel treats a path in the name field as a literal name.
6. `open -a` issued while the previous PT instance is still exiting is swallowed; `ptgui.launch` waits and retries.
7. **IOS devices rebuild state from `RUNNINGCONFIG` on load**; PC and server settings live in fields.

## 7. Conversion pipeline

For each original `O`:

1. `pttest.py 8.0.0 O out.json --saveas O_pt800.pka`: PT 8.0.0 opens the 4.1 file, converts the networks and the tree, saves the modern file (and the run records what Check Results shows).
2. `convert.py O O_pt800.pka converted/<name>_v8.pka` (or `tools/pipeline.sh <workdir>` for all): verifies every original graded item has a modern counterpart, restores the ones 8.0.0 dropped when their node exists in the regenerated tree, prints the mapping and anything that cannot be graded any more, sets `ELAPSED=0`, makes network [0] equal network [1], re-encodes. Instructions are left exactly as PT carried them over.
3. Test (section 8).

**GUI tests and focus.** `tools/ptgui.py` opens Packet Tracer in the background (`open -g`), moves its windows to the built-in Retina display (`PT_DISPLAY=builtin`, default; `external` for the other screen) and brings it to the front only for the guest login and the Check Results click, then hands focus back to the user's app (measured: about 2.5 s of focus per 55 s test). Screenshots on the Retina panel are 2x, which the OCR of the item counter needs; at 1x it misread 15/15 as 116/15. `tools/ptreport.py` rejects impossible counts and falls back to the Incorrect list.

**Compatibility of the two outputs with 7.x.** The `_v8` files (8.0 format) do not open in 7.2.2: Packet Tracer cannot read files saved by a newer version, and 7.2.2 fails silently with an empty workspace. The `pka-fix` output keeps the 4.1 container and grades fully in 7.2.2, 8.0.0, 8.2.2 and 9.0.1, so it is the more portable deliverable.

## 7b. Second conversion route: pka-fix (no Packet Tracer needed)

`pka-fix/pka_fix.py` (merged from PR #1, standard-library Python 3.8+, with a Windows drag-and-drop `.bat`) applies the same corrections directly to the 4.1 file and keeps the 4.1 container: it fills the empty expected values (link Type, Connects to, PC DNS Server IP) from the answer network, rewrites FastEthernet Duplex/Bandwidth `1` and OSPF Passive Interface values to the modern format, and rewrites OSPF network item IDs with wildcard masks so modern PT matches them to the "(deprecated) Route<n>" twins. Use it when PT 8.0.0 is not available (Windows guest mode refusing to save, or only 9.x installed). `tools/ptwin.py` is the Windows counterpart of `pttest.py` (pywinauto, PT 9.0.1).

Verification: on the 14 originals it reports 0 unknown and 0 warnings, and the number of filled values per file equals the items measured as never-passing in 9.0.1. The PR author reports in-app results for 9.0.1 (all solved copies 0 Incorrect, fresh copies start Incorrect) and 8.0.0 (solved 9, 13, 14 green; 13/14 keep 89 and 55 items). 8.2.2 (tested here 2026-10-02): all 13 solved copies reach their full item count, fresh copies start at 0; see tests/results.md.

## 8. Test harness and plan

`pttest.py` launches a PT version with a file, does the guest login, dismisses dialogs, presses Check Results, opens Assessment Items, reads every row (name, Correct/Incorrect, points) through the Accessibility API, screenshots the results view, and quits PT. `ptbatch.py` runs a plan file; `ptreport.py` summarises runs against the file's own graded-item count.

For every file and every version the checks are:

1. **Solved variant** (`variants.py solved`) scores 100 % and the item count equals the original's. Any Incorrect row in a solved file is a defect of the file for that version.
2. **Fresh file** opens without a dialog, Check Results lists all items as Incorrect (0 %).
3. Save from that version and decode with `pkacli.js info` (container check).

Manual checks still worth doing once per version: instructions readable, Reset Activity, do one activity by hand to 100 %.

## 8b. Packet Tracer versions (what each brings)

From Cisco's What's New page, Packet Tracer Network's release summaries and the runs on this Mac ("observed"):

- **8.0.0 (January 2021):** guest login with a session timer and three saves per session (observed). Mac users reported modules that cannot be dragged into slots, CLI keyboard input problems and a library error as standard user. Translates the 4.1 files well except OSPF network items (observed).
- **8.0.1 / 8.1 (2021):** maintenance fixes; guest login removed (account required); 8.1 added Tutored Activities (`.pksz`), an instructor feedback dialog, Windows 11 support, accessibility and security fixes.
- **8.2 / 8.2.1 / 8.2.2 (2022 to June 2024):** ASA 5506-X, IoT boards and home gateway, `show ip ospf interface brief`, proxy settings in the login window, CLI auto-focus; 8.2.2 fixed DLL-conflict crashes on Windows plus accessibility, usability and security bugs. No guest mode (observed: closing the login dialog quits the program).
- **9.0.0 / 9.0.1 (2025):** industrial networking devices and 11 OT protocols, more realistic fibre, accessibility (screen reader, keyboard focus), "streamlined authentication"; 9.0.1 adds security and stability fixes. Guest login works again (observed). Keeps stored expected values of old files instead of recomputing them (observed), which is why the 4.1 originals fail there.

**Since which version are the 4.1 files broken?** Known good: 7.2.2 and 8.0.0 (both recompute expected values on load; 7.2.2 audited 2026-10-02, see tests/results.md). Known broken: 8.2.2 and 9.0.1 (compare against the stored empty value; 8.2.2 fails the same items as 9.0.1). Not testable here: 8.0.1, 8.1.0, 8.2.0, 8.2.1 (not installed, no longer offered by Cisco). Most likely 8.1.0, which introduced the Tutored Activities engine and reworked assessment feedback; that is a guess. Versions 5.x to 7.x were not run; by reasoning Error 1 appeared only after 8.0 (8.0.0 still recomputes the values, which was the 4.1 behaviour).

**When did the route-check names change (Error 2)?** Dated from public activity files on GitHub, each carrying the version that saved it (scan script: the ad-hoc Python in the session, inputs listed below):

| Saved by | File | What its grading tree shows |
|---|---|---|
| 6.0.1.0011 | 2.2.2.4 Configuring IPv4 Static and Default Routes (afsanhq99/CSE-labs-Github) | `Routes>Static Routes>Route0` with value `172.31.0.0-24-172.31.1.193-0-1`, no "(deprecated)" twins. The 2007 descriptive names are already gone. |
| 7.1.1.0138 | 8.1.3.3 Configuring DHCPv4 (same repo) | `EIGRP>Autonomous System 1>Networks>Route0` = `192.168.20.0 0.0.0.255` (wildcard), no twins. |
| 7.2.2.0418 | 11.5.5, 11.7.5, 11.9.3, 4.7.1 (gulo-martin/Digital-commons-academic-hub, qddung/backup) | first files with `(deprecated) Route0` twins next to every static route and EIGRP network. |
| 8.0.0, 8.2.0, 8.2.1 | 1.0.5, 2.2.5.5, 7.3.1.8, 9.2.3.6, 13.2.7, 17.7.7 | twins everywhere; activities authored in 6.x and re-saved by 8.2.0 carry the graded flag on the "(deprecated)" twin (as our converted PTSkills did before `convert.py` moved it). |

Reading: the RouteN naming existed by 6.0.1 (static routes) and before 7.2 for OSPF (8.0's `(deprecated) Route0` twin under `OSPF>...>Networks` is the pre-7.2 node and is already called Route0). The "(deprecated)" mechanism arrived in 7.2.x: Cisco Community, September 2018, "Packet Tracer 7.2 Activity Wizard not recognizing static routes" (saved activities lost their static-route matches after reopen; fixed by the twins in 7.2.1/7.2.2). So the 4.1 OSPF names ("10.10.10.0 255.255.255.0 area0") most likely stopped matching in 5.x or 6.0, at the same rework that renamed static routes; no 5.x/6.x file with OSPF checks was found to observe it directly. Side note: from 7.3.1 OSPF is hidden from the Activity Wizard answer tree by default (Options, Preferences, Answer Tree). Measured on 2026-10-02: Packet Tracer 7.2.2 already loses the OSPF items of PTSkills 13 and 14 (80 of 89 and 46 of 55 kept), so Error 2 predates 7.2.2.

Sources: https://community.cisco.com/t5/cisco-bug-discussions/cisco-packet-tracer-7-2-activity-wizard-not-recognizing-static/td-p/3712416 , https://community.cisco.com/t5/routing/packet-tracer-activity-wizard-ospf-missing/td-p/4266467

None of the new devices matter for these labs (1841 routers, 2960 switches, PCs, one server). The differences that matter are login, stability fixes and the grading engine.

Sources: https://tutorials.ptnetacad.net/help/default/whatsNew.htm , https://www.packettracernetwork.com/features.html , https://www.packettracernetwork.com/features/packet-tracer-9-new-features.html

## 9. Open questions

- PTSkills9: 8.0.0 maps the legacy static route to `Routes>(deprecated) Static Routes>(deprecated) Route0`; `convert.py` additionally checks `Routes>Static Routes>Route0`. Both are graded; verify neither stays Incorrect in 9.0.1.

## 10. Ground rules

- These are Cisco NetAcad course materials: personal and course study only; don't publish them.
- Never modify `samples/originals/`.
- Keep the instruction text as PT carries it over; no added notes.
- Never use the em dash character in docs, comments or messages.

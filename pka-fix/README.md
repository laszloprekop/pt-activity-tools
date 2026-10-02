# pka_fix: old Packet Tracer activities that never reach 100 %

If Check Results in Packet Tracer 8.2 or 9.x stays red on cables, DNS server or OSPF even though your work is right, the activity file is probably from Packet Tracer 4.x (around 2007). This script fixes the file, so it grades correctly in current Packet Tracer.

## Use it

You need Python 3.8 or newer (https://www.python.org/downloads/). Nothing else to install.

**Windows:** drag one or more `.pka` files, or a folder, onto `pka_fix.bat`.

**Any system:**

```
python pka_fix.py MyActivity.pka            # writes MyActivity_fixed.pka next to it
python pka_fix.py path/to/folder            # every .pka in the folder
python pka_fix.py --check MyActivity.pka    # only report what it would fix
```

Then open the `_fixed.pka` in Packet Tracer and do the activity there. Your original file is never changed.

Files that aren't from PT 4.x/5.x are skipped with a message: newer files don't have this problem.

## What it fixes

Packet Tracer 4.1 stored some grading information in a form current Packet Tracer can't use:

| Problem | Seen as | Fix |
|---|---|---|
| Expected value missing for cable **Type**, cable **Connects to ...** and a PC's **DNS Server IP** | These items are Incorrect whatever you do | Filled in from the activity's own answer network, as Packet Tracer 8.0.0 did |
| **Duplex** / **Bandwidth** stored as `1` (auto) on FastEthernet ports | Incorrect on correct ports | Rewritten in the current format |
| OSPF **Passive Interface** stored as the interface name | Incorrect | Rewritten in the current format |
| OSPF **network** items match nothing in the current grading tree | Silently missing: fewer checks than the lab sheet lists | Their ID is rewritten with a wildcard mask, so Packet Tracer keeps them |

Nothing else in the file is touched: not the instructions, devices, addresses, cabling or points.

The output lists `filled`, `converted`, `unknown` and `warnings` per file:

- `unknown`: an item with an empty value of a kind the script doesn't recognise. It is left as it was.
- `WARNING`: an item the fixes may not cover. Either a known risky case (EIGRP networks, Duplex/Bandwidth on other ports than FastEthernet or with other values than auto, an OSPF network in an unexpected format), or any kind of check that never occurred in the tested files.

If you get either, check that activity before relying on it: complete it (or ask your teacher for a solved copy), press Check Results, and see whether anything correct is still marked Incorrect. If so, the file needs a new rule; please report it with the line from the output.

## Limits

- **Tested only on the 14 activities below.** Other PT 4.x activities very likely use the same formats; PT 5.x files are untested.
- **Old value formats can hide behind a stored value.** An item that has a value but in an old format looks fine to the script until Packet Tracer grades it (that's how the Duplex/Bandwidth case was found). The warnings flag every kind of check outside the tested set, but within a tested kind an unusual value can still slip through.
- **Not fixed:** EIGRP networks, Duplex/Bandwidth other than FastEthernet auto, cable types other than copper straight-through, copper crossover and serial. They are reported, not guessed.
- **Only PT 4.x/5.x files.** Newer activities are skipped; they have other, unrelated issues.
- **Grading only.** Instructions, timer and connectivity tests are unchanged, and like any converted file, PT 9.x doesn't show the "completed" message.

## How well it is tested

Tested on the 14 "PTSkills" Skills Integration Challenge activities of LTU course Z0025E (Cisco NetAcad Exploration material), on 2026-10-02:

- Every value it writes was compared with what Packet Tracer 8.0.0 itself writes when it converts the same files. All the same, except a few route and DNS-record items that 9.0.1 converts correctly by itself.
- In Packet Tracer 9.0.1, a copy of each fixed activity with the answer network loaded has no Incorrect items, and each fixed activity starts with its items Incorrect, as it should.

Other activities from the same era very likely have the same problems, but only these 14 were tested. Item kinds not seen in them are reported as `unknown` instead of guessed.

## Background

The diagnosis is in `../HANDOFF.md` and the audit of these files. The main pipeline converts by letting Packet Tracer 8.0.0 re-save each original and then running `tools/convert.py`; `pka_fix` makes the same corrections directly in the 4.1 file, so it needs no Packet Tracer 8.0.0 and runs anywhere Python does. `tools/ptwin.py` is the Windows test harness used to check it in PT 9.0.1.

Course activity files are Cisco NetAcad / course material: fix your own copies, don't redistribute the activities.

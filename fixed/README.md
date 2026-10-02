# Fixed activities (recommended download)

One file per Canvas original, same name plus `_fixed`. These are the files to hand out and to open, whatever Packet Tracer version you use.

Produced by `pka-fix/pka_fix.py` from the originals in `samples/originals/canvas/`. The script fills in the expected answers the 2007 files leave empty (cable type, cable port, a PC's DNS server), rewrites old value formats, and gives the OSPF network checks of PTSkills 13 and 14 the ID modern Packet Tracer expects. The file stays in the original 4.1 format, so every version from 7.2 up can open it. Instructions, devices, addresses, cabling and points are unchanged. PTSkills5 needs no fix; its file is the original under the `_fixed` name, so the set is complete.

Tested (2026-10-02 and 2026-10-03), solved copy reaches the full item count and fresh copy starts at 0 (PTSkills 13 and 14 start with 9 and 2 checks the original start network already meets):

| Packet Tracer | Result |
|---|---|
| 7.2.2 | all 14 pass (tests/runs_722) |
| 8.0.0 | all 14 pass (tests/runs_800fix) |
| 8.2.2 | all 14 pass (tests/runs_pkafix) |
| 9.0.1 | all 14 pass (reported by the pka-fix author in PR #1) |

Regenerate: `python3 pka-fix/pka_fix.py <folder with the originals>`, then copy the `_fixed.pka` files here.

Course material of Cisco NetAcad and LTU Z0025E: for course use only, do not publish.

| File | Activity |
|---|---|
| 1_482161921_LSG01_PTSkills1_fixed.pka | 1.7.1 Introduction to Packet Tracer |
| 1_482161921_LSG01_PTSkills2_fixed.pka | 2.7.1 Examining Packets |
| 1_482161921_LSG01_PTSkills3_fixed.pka | 3.5.1 Configuring Hosts and Services |
| 1_482161921_LSG01_PTSkills4_fixed.pka | 4.6.1 Analyzing the Application and Transport Layers |
| 1_482161921_LSG01_PTSkills5_fixed.pka | 5.6.1 Routing IP Packets (original, no fix needed) |
| 1_482161921_LSG01_PTSkills6_fixed.pka | 6.8.1 Planning Subnets and Configuring IP Addresses |
| 1_482161921_LSG01_PTSkills7_fixed.pka | 7.6.1 Data Link Layer Issues |
| 1_482161921_LSG01_PTSkills8_fixed.pka | 8.5.1 Connecting Devices and Exploring the Physical View |
| 1_482161921_LSG01_PTSkills9_fixed.pka | 9.9.1 Switched Ethernet |
| 1_482161921_LSG01_PTSkills10_fixed.pka | 10.7.1 Network Planning and Interface Configuration |
| 0_683853438_LSG01_PTSkills11_fixed.pka | 5.6.1a Basic RIP Configuration |
| 0_683853438_LSG01_PTSkills12_fixed.pka | 7.5.1 RIPv2 Basic Configuration Lab |
| 0_683853438_LSG01_PTSkills13_fixed.pka | 11.6.1 Basic OSPF Configuration Lab |
| 0_683853438_LSG01_PTSkills14_fixed.pka | 11.6.2 Challenge OSPF Configuration Lab |

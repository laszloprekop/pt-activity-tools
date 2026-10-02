# Test results (2026-10-01)

Every row is one run of `tools/pttest.py`: Packet Tracer of that version opened the file as guest,
pressed Check Results, and the Assessment Items table and PT's own "Item Count" (read from the
screenshot with `tools/ocr.py`) were recorded. The JSON of every run is in `tests/runs/`.

File name suffixes: `_orig` = the Canvas original as is; `_solved` = the original with the opening
state replaced by its answer network (every item must pass); `_v8` = the converted file from
`converted/` as is (every item must fail at start, except items the original already satisfies);
`_v8solved` = the converted file with the answer network as opening state.

Columns: ok = items PT reports Correct, bad = Incorrect, exp = graded items in the original's
grading tree, tot = PT's Item Count denominator. "ITEMS a!=b" marks files where PT lost items.

Summary:

- Originals in 8.0.0: all items kept and gradeable, except the 9 OSPF network items of PTSkills13
  and PTSkills14, which 8.0.0 drops (tot 80 of 89 and 46 of 55).
- Originals in 9.0.1: items with an empty expected value in the 4.1 tree are always Incorrect
  (PTSkills1 2 of 2, PTSkills2 3 of 6, PTSkills3 5 of 11, PTSkills4 5 of 15, PTSkills6 16 of 49,
  PTSkills7 6 of 33, PTSkills8 20 of 20, PTSkills9 24 of 40, PTSkills10 44 of 89, PTSkills11 7 of
  57, PTSkills12 16 of 22, PTSkills14 1 of 46), and the OSPF items are dropped as in 8.0.0.
- Converted files (`converted/*_v8.pka`) in 8.0.0 and 9.0.1: every solved run reaches the full
  item count ("completed"), every fresh run starts at 0 (PTSkills13: 9 items are satisfied by the
  original's starting network in every version; PTSkills14 in 9.0.1 shows 2 satisfied at start,
  8.0.0 shows 0; not investigated).
- 9.0.1 adds the activity's connectivity tests to its Item Count (PTSkills14: 57/55).
- 8.2.2: not tested (no guest mode; needs a persisted Cisco login on this machine).
- Five rows carry a `manual_check` note in their JSON where the OCR misread the counter and the
  screenshot was checked by eye.

```
file                         PT      ok bad  exp  tot  note
PTSkills1_orig.pka           8.0.0    0   2    2    2   incorrect: Connects to FastEthernet0/1, Connects to FastEthernet0/0
PTSkills1_solved.pka         8.0.0    2   0    2    2  
PTSkills1_solved.pka         9.0.1    0   2    2    2   incorrect: Connects to FastEthernet0/1, Connects to FastEthernet0/0
PTSkills1_v8.pka             8.0.0    0   2    2    2   NOT-completed incorrect: Connects to FastEthernet0/1, Connects to FastEthernet0/0
PTSkills1_v8.pka             9.0.1    0   2    2    2   incorrect: Connects to FastEthernet0/1
PTSkills1_v8solved.pka       8.0.0    2   0    2    2   completed
PTSkills1_v8solved.pka       9.0.1    2   0    2    2  
PTSkills2_orig.pka           8.0.0    0   6    6    6   incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask
PTSkills2_solved.pka         8.0.0    6   0    6    6  
PTSkills2_solved.pka         9.0.1    3   3    6    6   incorrect: Type
PTSkills2_v8.pka             8.0.0    0   6    6    6   NOT-completed incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask
PTSkills2_v8.pka             9.0.1    0   6    6    6   incorrect: Type, Connects to FastEthernet0/2, IP Address, Subnet Mask, Default Gateway, DNS Server IP
PTSkills2_v8solved.pka       8.0.0    6   0    6    6   completed
PTSkills2_v8solved.pka       9.0.1    6   0    6    6  
PTSkills3_orig.pka           8.0.0    0  11   11   11   incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask...
PTSkills3_solved.pka         8.0.0   11   0   11   11   completed
PTSkills3_solved.pka         9.0.1    6   5   11   11   incorrect: Type, Connects to FastEthernet0/2, DNS Server IP, Connects to FastEthernet0/0
PTSkills3_v8.pka             8.0.0    0  11   11   11   NOT-completed incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask...
PTSkills3_v8.pka             9.0.1    0  11   11   11   incorrect: Type, Connects to FastEthernet0/2, IP Address, Subnet Mask, Default Gateway, DNS Server IP...
PTSkills3_v8solved.pka       8.0.0   11   0   11   11   completed
PTSkills3_v8solved.pka       9.0.1   11   0   11   11  
PTSkills4_orig.pka           8.0.0    0  15   15   15   incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/1, Type, Subnet Mask...
PTSkills4_solved.pka         8.0.0   15   0   15   15   completed
PTSkills4_solved.pka         9.0.1   10   5   15   15   incorrect: Type, Connects to FastEthernet0/1, DNS Server IP, Type, Connects to FastEthernet0/0
PTSkills4_v8.pka             8.0.0    0  15   15   15   NOT-completed incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/1, Type, Subnet Mask...
PTSkills4_v8.pka             9.0.1    0  15   15   15   incorrect: Type, Connects to FastEthernet0/1, IP Address, Subnet Mask, Default Gateway, DNS Server IP...
PTSkills4_v8solved.pka       8.0.0   15   0   15   15   completed
PTSkills4_v8solved.pka       9.0.1   15   0   15   15  
PTSkills5_orig.pka           8.0.0    0   4    4    4   incorrect: IP Address, Port Status, Subnet Mask, Route0
PTSkills5_solved.pka         8.0.0    4   0    4    4   completed
PTSkills5_solved.pka         9.0.1    4   0    4    4  
PTSkills5_v8.pka             8.0.0    0   4    4    4   NOT-completed incorrect: IP Address, Port Status, Subnet Mask, Route0
PTSkills5_v8.pka             9.0.1    0   4    4    4   incorrect: Port Status, IP Address, Subnet Mask, Route0
PTSkills5_v8solved.pka       8.0.0    4   0    4    4   completed
PTSkills5_v8solved.pka       9.0.1    4   0    4    4  
PTSkills6_orig.pka           8.0.0    0  49   49   49   incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/1, Type, Port Status...
PTSkills6_solved.pka         8.0.0   49   0   49   49   completed
PTSkills6_solved.pka         9.0.1   33  16   49   49   incorrect: Type, Connects to FastEthernet0, Type, Connects to Serial0/0/0, Type, Connects to FastEthernet0/24...
PTSkills6_v8.pka             8.0.0    0  49   49   49   NOT-completed incorrect: Default Gateway, DNS Server IP, IP Address, Connects to FastEthernet0/1, Type, Port Status...
PTSkills6_v8.pka             9.0.1    0  49   49   49   incorrect: Port Status, Type, Connects to FastEthernet0, IP Address, Subnet Mask, Port Status...
PTSkills6_v8solved.pka       8.0.0   49   0   49   49   completed
PTSkills6_v8solved.pka       9.0.1   49   0   49   49  
PTSkills7_orig.pka           8.0.0    0  33   33   33   incorrect: Default Gateway, DNS Server IP, IP Address, Port Status, Subnet Mask, Default Gateway...
PTSkills7_solved.pka         8.0.0   33   0   33   33   completed
PTSkills7_solved.pka         9.0.1   27   6   33   33   incorrect: Type, Connects to Serial0/0/0, Type, Connects to Serial0/0/0, DNS Server IP, DNS Server IP
PTSkills7_v8.pka             8.0.0    0  33   33   33   NOT-completed incorrect: Default Gateway, DNS Server IP, IP Address, Port Status, Subnet Mask, Default Gateway...
PTSkills7_v8.pka             9.0.1    0  33   33   33   incorrect: IP Address, Subnet Mask, Port Status, Type, Connects to Serial0/0/0, IP Address...
PTSkills7_v8solved.pka       8.0.0   33   0   33   33   completed
PTSkills7_v8solved.pka       9.0.1   33   0   33   33  
PTSkills8_orig.pka           8.0.0    0  20   20   20   incorrect: Connects to FastEthernet0/1, Type, Connects to FastEthernet0/2, Type, Connects to FastEthernet0/0, Type...
PTSkills8_solved.pka         8.0.0   20   0   20   20   completed
PTSkills8_solved.pka         9.0.1    0  20   20   20   incorrect: Type, Connects to FastEthernet0, Type, Connects to Serial0/0/0, Type, Connects to FastEthernet0/24...
PTSkills8_v8.pka             8.0.0    0  20   20   20   NOT-completed incorrect: Connects to FastEthernet0/1, Type, Connects to FastEthernet0/2, Type, Connects to FastEthernet0/0, Type...
PTSkills8_v8.pka             9.0.1    0  20   20   20   incorrect: Type, Connects to FastEthernet0, Type, Connects to Serial0/0/0, Type, Connects to FastEthernet0/24...
PTSkills8_v8solved.pka       8.0.0   20   0   20   20   completed
PTSkills8_v8solved.pka       9.0.1   20   0   20   20  
PTSkills9_orig.pka           8.0.0    0  40   40   40   incorrect: Default Gateway, DNS Server IP, Duplex, IP Address, Connects to FastEthernet0/1, Type...
PTSkills9_solved.pka         8.0.0   40   0   40   40   completed
PTSkills9_solved.pka         9.0.1   16  24   40   40   incorrect: Bandwidth, Duplex, Type, Connects to FastEthernet0/24, Duplex, Type...
PTSkills9_v8.pka             8.0.0    0  40   40   40   NOT-completed incorrect: Default Gateway, DNS Server IP, Duplex, IP Address, Connects to FastEthernet0/1, Type...
PTSkills9_v8.pka             9.0.1    0  40   40   40   incorrect: Port Status, Bandwidth, Duplex, Type, Connects to FastEthernet0/24, IP Address...
PTSkills9_v8solved.pka       8.0.0   40   0   40   40   completed
PTSkills9_v8solved.pka       9.0.1   40   0   40   40  
PTSkills10_orig.pka          8.0.0    0  89   89   89   incorrect: Default Gateway, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask, Default Gateway...
PTSkills10_solved.pka        8.0.0   89   0   89   89   completed
PTSkills10_solved.pka        9.0.1   45  44   89   89   incorrect: Type, Connects to FastEthernet0/1, Type, Connects to Serial0/0/0, Type, Connects to Serial0/0/1...
PTSkills10_v8.pka            8.0.0    0  89   89   89   NOT-completed incorrect: Default Gateway, IP Address, Connects to FastEthernet0/2, Type, Subnet Mask, Default Gateway...
PTSkills10_v8.pka            9.0.1    0  89   89   89   incorrect: Port Status, Type, Connects to FastEthernet0/1, IP Address, Subnet Mask, Port Status...
PTSkills10_v8solved.pka      8.0.0   89   0   89   89   completed
PTSkills10_v8solved.pka      9.0.1   89   0   89   89  
PTSkills11_orig.pka          8.0.0    0  57   57   57   incorrect: Default Gateway, IP Address, Subnet Mask, Default Gateway, IP Address, Subnet Mask...
PTSkills11_solved.pka        8.0.0   57   0   57   57   completed
PTSkills11_solved.pka        9.0.1   50   7   57   57   incorrect: Connects to FastEthernet0/1, Connects to Serial0/0/0, Connects to Serial0/0/1, Connects to FastEthernet0/1, Connects to Serial0/0/0, Connects to FastEthernet0/1...
PTSkills11_v8.pka            8.0.0    0  57   57   57   NOT-completed incorrect: Default Gateway, IP Address, Subnet Mask, Default Gateway, IP Address, Subnet Mask...
PTSkills11_v8.pka            9.0.1    0  57   57   57   incorrect: Port Status, Connects to FastEthernet0/1, IP Address, Subnet Mask, Port Status, Connects to Serial0/0/0...
PTSkills11_v8solved.pka      8.0.0   57   0   57   57   completed
PTSkills11_v8solved.pka      9.0.1   57   0   57   57  
PTSkills12_orig.pka          8.0.0    0  22   22   22   incorrect: Type, Type, Type, Type, Type, Type...
PTSkills12_solved.pka        8.0.0   22   0   22   22   completed
PTSkills12_solved.pka        9.0.1    6  16   22   22   incorrect: Connects to Serial0/0/0, Connects to Serial0/0/0, Type, Connects to Serial0/0/1, Type, Type
PTSkills12_v8.pka            8.0.0    0  22   22   22   NOT-completed incorrect: Type, Type, Type, Type, Type, Type...
PTSkills12_v8.pka            9.0.1    0  22   22   22  
PTSkills12_v8solved.pka      8.0.0   22   0   22   22   completed
PTSkills12_v8solved.pka      9.0.1   22   0   22   22  
PTSkills13_orig.pka          8.0.0    9  71   89   80   ITEMS 80!=89 incorrect: Default Gateway, Default Gateway, Password, Host Name, IP Address, Port Status...
PTSkills13_solved.pka        8.0.0   80   0   89   80   completed ITEMS 80!=89
PTSkills13_solved.pka        9.0.1   80   0   89   80   ITEMS 80!=89
PTSkills13_v8.pka            8.0.0    9  80   89   89   NOT-completed incorrect: Default Gateway, Default Gateway, Password, Host Name, Route0, Route1...
PTSkills13_v8.pka            9.0.1    9  80   89   89   incorrect: IP Address, Subnet Mask, Port Status, IP Address, Subnet Mask, Bandwidth Info...
PTSkills13_v8solved.pka      8.0.0   89   0   89   89   completed
PTSkills13_v8solved.pka      9.0.1   89   0   89   89  
PTSkills14_orig.pka          8.0.0    0  46   55   46   ITEMS 46!=55 incorrect: Host Name, FastEthernet0/0, IP Address, Port Status, Subnet Mask, Clock Rate...
PTSkills14_solved.pka        8.0.0   46   0   55   46   completed ITEMS 46!=55
PTSkills14_solved.pka        9.0.1   45   1   55   46   ITEMS 46!=55 incorrect: FastEthernet0/0, FastEthernet0/0, FastEthernet0/0
PTSkills14_v8.pka            8.0.0    0  55   55   55   NOT-completed incorrect: Host Name, Route0, Route1, Route2, FastEthernet0/0, IP Address...
PTSkills14_v8.pka            9.0.1    2  53   55   55   incorrect: Port Status, IP Address, Subnet Mask, Port Status, IP Address, Subnet Mask...
PTSkills14_v8solved.pka      8.0.0   55   0   55   55   completed
PTSkills14_v8solved.pka      9.0.1   55   0   55   55  
```

# Lab 2: PTSkills 1 to 5, newcomer guide and draft answers

Written 2 October 2026 from the Canvas page "9.5 Lab 2 (Submit your report)" (course 614, assignment 3042) and from the instruction text inside the five activity files. Report: one PDF per group, due 2 October 2026, 5 points (1 per activity). For each activity the report needs a screenshot of Check Results with the Assessment Items tab, plus the answers to the questions. Use the repaired `_v8` files from `converted/` in Packet Tracer 8.2.x or 9.x; the Canvas originals cannot reach 100 % there.

The answers are drafts. Rewrite them in the group's own words.

## Words you will meet

- **Activity (.pka file)**: a Packet Tracer file that holds a half-built network, the instructions, and a hidden checklist. The Check Results button compares your network with the checklist.
- **Realtime mode**: the network runs at normal speed, like real equipment.
- **Simulation mode**: the network runs step by step; every packet is shown as an envelope you can open.
- **PDU**: "protocol data unit", Packet Tracer's word for one packet or frame. "Add Simple PDU" sends one test ping.
- **Ping**: a small test message (ICMP echo request). If the other side answers, the path works.
- **Frame, packet, segment**: the same data at three layers. A frame carries MAC addresses (layer 2, inside one LAN), a packet carries IP addresses (layer 3, across networks), a segment or datagram carries port numbers (layer 4, TCP or UDP).
- **MAC address**: the fixed hardware address of a network card, like 0001.4300.E101. Used inside one LAN.
- **IP address and subnet mask**: the logical address and the rule that says which addresses are on the same network. 172.16.1.1 with mask 255.255.0.0 means "everything starting with 172.16 is my network".
- **Default gateway**: the router a PC sends to when the destination is outside its own network.
- **DNS**: the phone book that turns a name (eagle-server.example.com) into an IP address.
- **HTTP**: the protocol a browser uses to ask a web server for a page.
- **ARP**: the question "who has this IP address, tell me your MAC?" that a device must ask before it can send a frame inside the LAN.
- **Route**: one line in a router's table: "to reach network X, send to Y".
- **Default route**: the catch-all route 0.0.0.0/0, "send everything else to Y".

## The lab network (same in all five activities)

| Device | Port | IP address | Mask | Default gateway |
|---|---|---|---|---|
| R1-ISP (router) | Fa0/0 | 192.168.254.253 | 255.255.255.0 | none |
| R1-ISP | S0/0/0 | 10.10.10.6 | 255.255.255.252 | none |
| R2-Central (router) | Fa0/0 | 172.16.255.254 | 255.255.0.0 | none |
| R2-Central | S0/0/0 | 10.10.10.5 | 255.255.255.252 | none |
| S1-Central (switch) | VLAN 1 | 172.16.254.1 | 255.255.0.0 | 172.16.255.254 |
| PC 1A | NIC | 172.16.1.1 | 255.255.0.0 | 172.16.255.254 |
| PC 1B | NIC | 172.16.1.2 | 255.255.0.0 | 172.16.255.254 |
| Eagle Server | NIC | 192.168.254.254 | 255.255.255.0 | 192.168.254.253 |

How it hangs together: the two PCs and the switch form one LAN (172.16.0.0/16). R2-Central is that LAN's door to the outside. A serial cable joins R2-Central to R1-ISP (the tiny network 10.10.10.4/30). Eagle Server sits on R1-ISP's other side (192.168.254.0/24) and runs the DNS and web services. Cables: PC to switch and switch to router are straight-through; server to router is crossover (two "equal" devices); router to router is serial.

Packet Tracer basics used everywhere:

- Hover the mouse over a device to see its addresses and port states.
- Click a device to open it. Routers and switches have Physical, Config and CLI tabs. PCs have Physical, Config and Desktop tabs. Servers have Physical, Config and Services tabs (older versions: Config only).
- The device list is at the bottom left; the cable list is under the lightning-bolt icon. The gold lightning bolt is "auto connect": it picks the right cable.
- The Realtime / Simulation switch is at the bottom right. In Simulation mode the Capture / Forward button moves packets one step at a time, and the Event List shows every step.
- A test ping: click the closed envelope icon on the right toolbar (Add Simple PDU), click the sender, click the receiver. The result appears in the PDU List window at the bottom right. "Fire" sends it again.

---

## PTSkills 1: Introduction to Packet Tracer

**What you achieve:** you learn where everything is in Packet Tracer and you finish the cabling of the lab network. Two cables are missing at the start: Eagle Server is not connected to R1-ISP, and PC 1A is not connected to S1-Central. Those two cables are the two checked items.

Steps, in order:

1. Look around. The big white area is the Logical Workspace where devices live. Bottom left: device groups (routers, switches, end devices, connections). Hover over a group to see its name, click it to see the devices in it. Why: you will need to find PCs and cables yourself in the later activities.
2. Open the connections group (the lightning bolt). The first cable type, the gold lightning bolt, is "auto connect". Why: it chooses straight-through, crossover or serial for you, so you cannot pick the wrong cable while you are learning.
3. With auto connect, click Eagle Server, then R1-ISP. A cable appears. Why: without it the server is cut off from the whole network. Unlocks: one checked item.
4. With auto connect, click PC 1A, then S1-Central. Why: without it PC 1A cannot talk to anything. Unlocks: the second checked item.
5. Wait until the link lights at both ends of the new cables turn green. Why: a link light is the physical layer saying "this cable works". Orange means "still coming up"; red means a bad cable or a port that is turned off.
6. Hover over each device and read the pop-up. A router shows an address and state per port, a switch shows VLAN membership per port, a PC and a server show their address, MAC and gateway. Why: this is the fastest way to check an address without opening anything.
7. Click each device type once and look at its tabs (Physical, Config, CLI for routers and switches; Physical, Config, Desktop for PCs). Close them again. Why: the next activities ask you to change settings in these tabs.
8. Press Check Results (bottom of the instructions window). The Assessment Items tab must show both link items Correct and 100 %. Take the screenshot.

Questions hidden in the activity: none; the text only asks you to explore. The reflection suggests the built-in "My First PT Lab" under Help, Contents, which is worth one evening if Packet Tracer is new to you.

**Report question: explain the difference between a router and a switch.**

*In brief:* A switch joins devices inside one network and forwards frames by MAC address. A router joins different networks and forwards packets by IP address, using a routing table. Every router port is in a different network; all switch ports are in the same one. A router rebuilds the frame at every hop and blocks broadcasts; a switch passes frames on unchanged and floods broadcasts. In the lab, S1-Central is the switch inside 172.16.0.0/16 and R2-Central is the router that leads out of it.

A switch connects devices inside one network. It forwards frames by MAC address, using a table it builds by watching which address appears on which port. All its ports are in the same network; in the lab, S1-Central's ports are all in VLAN 1 (172.16.0.0/16), and the switch only has an IP address so you can manage it (172.16.254.1). A switch passes frames on unchanged and sends broadcasts out of every port.

A router connects different networks. Every port of a router is in a different network, and the router forwards packets by IP address using its routing table. R2-Central joins the LAN 172.16.0.0/16 (port Fa0/0, 172.16.255.254) to the serial link 10.10.10.4/30 (port S0/0/0, 10.10.10.5); R1-ISP joins that link to the server network 192.168.254.0/24. When a router forwards a packet it throws away the old frame, lowers the TTL by one, and builds a new frame for the next hop, so the MAC addresses change at every router while the IP addresses stay the same. A router does not pass broadcasts on. In Packet Tracer you can see the difference when you hover: a router shows an IP address per port, a switch shows VLAN membership and no port addresses.

---

## PTSkills 2: Examining Packets

**What you achieve:** you build a PC from scratch, then watch a ping travel through the network step by step. At the start PC 1B does not exist. The six checked items are all about 1B: its cable type, which switch port it uses, its IP address, mask, gateway and DNS server.

Steps, in order:

1. Drag a PC (End Devices group, "PC-PT") onto the workspace near the switch. Why: PC 1B is missing from the network.
2. Click the new PC, Config tab, Display Name: type `1B` (exactly, no quotes, capital B). Why: Check Results finds devices by name. A PC called "PC0" scores nothing even if everything else is right.
3. Still in Config: Global settings, Gateway 172.16.255.254 and DNS Server 192.168.254.254. Then the FastEthernet0 port: IP 172.16.1.2, mask 255.255.0.0. (The Desktop tab, IP Configuration, does the same.) Why each value: the IP and mask put the PC into the LAN; the gateway tells it which router leads outside; the DNS server tells it where to ask for names. Unlocks: four checked items.
4. Connect 1B to S1-Central with a straight-through cable (the solid black line in the connections group), from the PC's FastEthernet0 to the switch's **FastEthernet0/2**. Why: the checklist wants exactly port Fa0/2 and exactly a straight-through cable. Auto connect also works here. Unlocks: the last two items.
5. Press Check Results. It should say 100 %. Take the screenshot now.
6. Wait until the link light on the new cable is green (the switch takes about half a minute to put the port into service).
7. Add Simple PDU: click the closed envelope on the right toolbar, click PC 1B, click Eagle Server. Look at the PDU List window at the bottom right: the first ping says **Failed**. Why: see the question below. Double-click **Fire** in the PDU List: the second ping says **Successful**.
8. Switch to Simulation mode (bottom right). Press Capture / Forward repeatedly and watch the envelope travel 1B, switch, R2-Central, R1-ISP, server and back. Click the envelope or the coloured square in the Event List to open it. Why: this is the point of the activity, seeing that the ping is a frame inside a frame, with addresses that change at the routers.
9. Task 4 asks you to experiment: send other pings (1A to 1B, 1B to R2-Central, server to 1A) and watch them. Why: pings inside the LAN never reach a router; pings to the server pass two routers.

Questions hidden in the activity and short answers:

- Task 2: "The first time ... it will show as Failed, this is because of the ARP process." Why? See the report question below.
- Task 4: "Try creating different combinations of test packets." What changes? A ping between 1A and 1B only crosses the switch, so no router and no change of MAC address. A ping to the server crosses two routers and the MAC addresses change twice. A ping to a wrong address is dropped at the first router that has no route.

**Report question: why does the first one-shot ping fail (ARP)?**

*In brief:* A ping must be put into an Ethernet frame, and a frame needs the MAC address of the next device. PC 1B does not yet know the MAC address of its gateway, so it first broadcasts an ARP request. While waiting for the ARP reply, the ping that triggered it is dropped, which shows as Failed. R1-ISP does the same lookup for the server's MAC. The second ping works because the ARP tables are now filled.

A ping is an ICMP echo request. It travels inside an IP packet, and the IP packet travels inside an Ethernet frame. To build the frame, PC 1B needs the MAC address of the next device. Eagle Server is in another network, so the frame has to go to the default gateway 172.16.255.254, and the PC does not yet know that router's MAC address. So it first sends an ARP request as a broadcast ("who has 172.16.255.254?"), and R2-Central answers with its MAC. While the PC waits for that answer, the ping that caused the lookup is thrown away, which is what many real operating systems do too. That is the Failed. The same lookup also happens at R1-ISP, which must ask for Eagle Server's MAC before it can deliver. The second ping succeeds because every ARP table along the path is now filled. In Simulation mode you can see it: the first run shows ARP frames (destination FFFF.FFFF.FFFF) before any ICMP, the second run shows only ICMP. ARP entries are forgotten after a few minutes, so a ping can fail again later for the same reason.

Screenshot for the report: the Event List of the first ping with ARP lines above the ICMP line.

---

## PTSkills 3: Configuring Hosts and Services

**What you achieve:** you repair the network (PC 1B missing again, server not cabled, server services switched off) and then watch how a web address becomes a web page. Eleven checked items: the six 1B items from PTSkills 2, the server's cable type and router port, DNS on, a DNS record for eagle-server.example.com, and HTTP on.

Steps, in order:

1. Add PC 1B exactly as in PTSkills 2 (name `1B`, IP 172.16.1.2, mask 255.255.0.0, gateway 172.16.255.254, DNS 192.168.254.254, straight-through cable to S1-Central Fa0/2). Unlocks six items.
2. Connect Eagle Server to R1-ISP port **FastEthernet0/0** with a **crossover** cable (the dashed line in the connections group). Why crossover: server and router both "send on the same pins"; a straight cable between them would not link up, and the checklist checks the cable type. Unlocks two items.
3. Click Eagle Server, Services tab (older versions: Config tab), HTTP: set HTTP to On. Why: without it the server is not a web server and the browser gets nothing. Unlocks one item.
4. Services tab, DNS: set DNS service to On, then add a record: Name `eagle-server.example.com`, Type A Record, Address 192.168.254.254, press Add. Why: this is the phone book entry; without it the name cannot be turned into an address and the browser fails before any web traffic. Unlocks two items.
5. Press Check Results: 100 %. Screenshot.
6. Realtime test: Add Simple PDU from 1B to Eagle Server; the first attempt fails (ARP, as in PTSkills 2), Fire again, success. Then press **Delete** in the PDU List window to remove this test packet before the next task. Why: the simulation in the next step gets confusing if the old ping is replayed too.
7. Switch to Simulation mode. On PC 1B open Desktop, Web Browser, type `eagle-server.example.com`, press Go. Press Capture / Forward until the page appears. Why: now you watch two conversations: first DNS (name to address), then HTTP (page). If "Buffer Full" appears, press View Previous Events.
8. Open the envelopes when they are at PC 1B and at Eagle Server (click the coloured square in the Event List; look at Inbound PDU Details and Outbound PDU Details). Why: you see the DNS question and answer, then the TCP handshake, then the HTTP request and the page.

Questions hidden in the activity:

- "Note that when you add a simple PDU, it appears in the PDU List Window as part of Scenario 0." What is a scenario? A named set of test packets. New makes another set, Delete removes the packets of the current one. Use it to keep tests apart.
- The reflection is the report question below.

**Report question: what happens when you type a URL into a browser and a page comes back? Which client-server interactions are involved?**

*In brief:* First the PC asks the DNS server for the address behind the name (one UDP question, one UDP answer). Then the browser opens a TCP connection to that address on port 80 with a three-way handshake. It sends HTTP GET and the server answers HTTP 200 OK with the page. The connection is then closed. Two client-server pairs are involved: DNS client to DNS server, and HTTP client to HTTP server, both started by the client.

Two separate conversations, both started by the PC.

1. Name lookup (DNS). The browser asks the PC's DNS client to find the address of eagle-server.example.com. The PC sends a DNS query in a UDP datagram to port 53 of its DNS server, 192.168.254.254, which is Eagle Server. The server looks up its record and answers: 192.168.254.254.
2. Page transfer (HTTP). Now the browser opens a TCP connection to that address on port 80. First the three-way handshake: SYN from the PC, SYN-ACK from the server, ACK from the PC. Then the browser sends "HTTP GET /" and the server answers "HTTP 200 OK" with the HTML of the page, which the browser draws. Finally both sides close the connection (FIN, ACK).

So there is a DNS client talking to a DNS server over UDP, and an HTTP client talking to an HTTP server over TCP. Both are request and reply, and the client always asks first. Underneath, every packet travels 1B, S1-Central, R2-Central, R1-ISP, Eagle Server and back, with ARP filling in MAC addresses where needed.

Diagram: draw PC 1B on the left and Eagle Server on the right as two vertical lines, then arrows from top to bottom: DNS query (right), DNS reply (left), SYN (right), SYN-ACK (left), ACK (right), HTTP GET (right), HTTP 200 OK (left), FIN/ACK (both). A photo of this on paper is fine for the report.

---

## PTSkills 4: Analyzing the Application and Transport Layers

**What you achieve:** the same repair as PTSkills 3 but on the other side (the server has been replaced and is blank, PC 1A has lost its addresses), and then a closer look at the same web request with the transport layer visible. Fifteen checked items: six for 1A, and for the server: power on, cable type, router port, IP, mask, gateway, DNS on, DNS record, HTTP on.

Steps, in order:

1. Click Eagle Server, Physical tab: the power switch on the picture of the server is off. Click it on. Why: a powered-off device does nothing, and "Power" is a checked item.
2. Config tab (or Desktop, IP Configuration): IP 192.168.254.254, mask 255.255.255.0, gateway 192.168.254.253. Why: the server needs its own address and a gateway (R1-ISP) to answer PCs in the other network. Unlocks three items.
3. Services: HTTP On. DNS On, add the A record eagle-server.example.com to 192.168.254.254. Unlocks three items.
4. Connect the server to R1-ISP **Fa0/0** with a **crossover** cable. Unlocks two items.
5. Click PC 1A: IP 172.16.1.1, mask 255.255.0.0, gateway 172.16.255.254, DNS 192.168.254.254. Connect it to S1-Central **Fa0/1** with a straight-through cable. Why: 1A must be in the LAN, know its router, and know where DNS is. Unlocks six items.
6. Check Results: 100 %. Screenshot.
7. Realtime test ping 1A to Eagle Server (fails once because of ARP, Fire again). Then Delete the test packet.
8. Simulation mode. Press Edit Filters (or Show All/None) and make sure DNS, UDP, HTTP, TCP and ICMP are ticked. Why: the Event List otherwise fills with ARP and other noise.
9. On PC 1A: Desktop, Web Browser, `eagle-server.example.com`, Go. Capture / Forward through the whole exchange. Open the envelopes at 1A and at the server and look at the layers: DNS sits on UDP, HTTP sits on TCP. Count the packets: the DNS part is two packets, the HTTP part is many (handshake, request, data, acknowledgements, close).

Questions hidden in the activity: the three reflection questions are the report questions below. One more that the text implies in Task 2: "why must the Event Filter include UDP and TCP?" Because DNS and HTTP are the applications, but what you see on the wire are UDP datagrams and TCP segments carrying them; filtering only DNS and HTTP hides the handshake and the acknowledgements.

**Report question 1: a diagram of the sequence of protocol events for a web page.**

*In brief:* DNS query and reply over UDP come first. Then TCP SYN, SYN-ACK and ACK open the connection. HTTP GET goes out and HTTP 200 OK with the page comes back, acknowledged by TCP. Finally FIN and ACK close the connection. The filtered Event List in Simulation mode shows exactly this order.

Same ladder as in PTSkills 3, now with the transport layer written on each arrow:

1. DNS query, UDP, port 53 (1A to server)
2. DNS reply, UDP (server to 1A)
3. TCP SYN, port 80 (1A to server)
4. TCP SYN-ACK (server to 1A)
5. TCP ACK (1A to server)
6. HTTP GET, inside TCP (1A to server)
7. HTTP 200 OK with the page, inside TCP, possibly several segments (server to 1A)
8. TCP ACKs for the data (1A to server)
9. TCP FIN and ACK in both directions

A screenshot of the filtered Event List shows this order and can be used as the diagram.

**Report question 2: where might things go wrong? Does a packet get stuck at a router or disappear?**

*In brief:* A wrong DNS setting stops everything before any web traffic. A wrong gateway or mask keeps the packet inside the LAN. A router with a port down, or without a matching route, throws the packet away at once; it is not held or queued. A real router also sends back an ICMP destination unreachable; Packet Tracer shows the packet vanishing at the router and the sender times out. A powered-off or service-less server receives the packets but never answers.

- Wrong or missing DNS server on the PC: the name is never resolved; no HTTP is sent at all; the browser shows "name cannot be resolved".
- Wrong gateway or mask on the PC: the packet is sent to the wrong neighbour or never leaves the LAN; nobody answers; the ping times out.
- Router port turned off or without an address (the PTSkills 5 situation): the frame reaches the router and is dropped there. In Simulation mode the envelope gets a red cross at R2-Central.
- Router without a route to the destination network: the router **discards** the packet. It does not keep it or wait; a packet with no matching route is thrown away at once. A real router also sends an ICMP "destination unreachable" message back; Packet Tracer shows the packet disappearing at the router and the sender reports a timeout.
- Server powered off or services off: packets arrive but nothing answers; the client waits and gives up.
- Wrong cable type between server and router: the link light stays red and nothing passes at all.

**Report question 3: compare DNS with HTTP, and UDP with TCP.**

*In brief:* DNS turns a name into an address with one short question and answer over UDP port 53. HTTP fetches the page itself over TCP port 80, with methods and status codes and large answers. UDP sends single datagrams with no handshake, no acknowledgements and no retransmission, so it is fast but unreliable. TCP opens a connection, numbers and acknowledges every byte, resends what is lost, and closes cleanly. That costs extra packets but guarantees the whole page arrives intact and in order.

DNS and HTTP are both application protocols where a client asks and a server answers. DNS turns a name into an address, one short question and one short answer, carried by UDP on port 53, and it must happen first. HTTP fetches the content itself, carried by TCP on port 80, with methods such as GET and status codes such as 200, and its answers can be large and split over many segments.

UDP and TCP are the two transport protocols underneath. UDP is connectionless: one datagram, no handshake, no acknowledgement, no retransmission; cheap and fast, which suits a tiny DNS exchange. TCP is connection-oriented: a handshake before any data, sequence numbers and acknowledgements so lost segments are resent and order is kept, flow and congestion control, and an orderly close. It costs extra packets (you can count them in the Event List) but guarantees that the whole page arrives complete and in order.

---

## PTSkills 5: Routing IP Packets

**What you achieve:** you fix a router. R2-Central's LAN port is switched off and has no address, and the router has no route to the outside. Four checked items: the port's status, its IP, its mask, and the default route.

Steps, in order:

1. Realtime: ping from PC 1A to 192.168.254.254 (Add Simple PDU, or Desktop, Command Prompt, `ping 192.168.254.254`). It fails. Hover over R2-Central: port Fa0/0 is down and has no address. Why: this is the fault you are going to repair; seeing it first makes the fix meaningful.
2. Click R2-Central, Config tab, INTERFACE, FastEthernet0/0: IP 172.16.255.254, mask 255.255.0.0, Port Status: On. Close the window. Why: the LAN's gateway must have an address in the LAN and be switched on, otherwise the PCs have no door to the outside. Unlocks three items (Port Status, IP Address, Subnet Mask).
3. Hover over R2-Central again: Fa0/0 is up. Ping Eagle Server again: it **still fails**. The activity asks "what are some possible reasons why?" See the hidden questions below.
4. Click the Inspect tool (magnifying glass on the right toolbar), click R2-Central, choose Routing Table. You see two "C" lines (connected networks: 172.16.0.0/16 and 10.10.10.4/30) and nothing for 192.168.254.0/24. Why: this is the proof that the router does not know where the server network is.
5. Click R2-Central, Config tab, ROUTING, Static: Network 0.0.0.0, Mask 0.0.0.0, Next Hop 10.10.10.6, press Add. Why: 0.0.0.0/0 matches every destination, so "anything I do not know, hand to R1-ISP at 10.10.10.6". Unlocks the last item.
6. Config tab, GLOBAL, Settings, press Save (this is "copy running-config startup-config"). Why: router settings live in memory; without Save a power cycle (or Reset Activity) forgets them.
7. Inspect the routing table again: a new "S*" line, 0.0.0.0/0 via 10.10.10.6.
8. Check Results: 100 %. Screenshot.
9. Realtime: ping 1A to Eagle Server. Fails once (ARP), Fire again, Successful.
10. Simulation mode: use the same PDU and Capture / Forward it from 1A to the server and back. Open the envelope at each hop and compare the inbound and outbound frame: same source and destination IP all the way, different MAC addresses after every router, TTL one lower after every router.

Questions hidden in the activity and short answers:

- Task 1: "Try reaching Eagle Server. The request still fails. What are some possible reasons why?" The port is now up, so the frame reaches R2-Central, but the router has no route to 192.168.254.0/24 and throws the packet away. Other possible reasons in general: the serial link to R1-ISP down, R1-ISP missing its route back to 172.16.0.0/16 (it has one: `ip route 172.16.0.0 255.255.0.0 10.10.10.5`), the server off, or ARP not yet done.
- Task 2: "You will see the router's directly connected networks, but there is no way to reach the Eagle Server network." What does "directly connected" mean? Networks the router has a port in. It learns those by itself; every other network must be taught, by a static route like here or by a routing protocol (RIP and OSPF in later labs).
- Task 3: "This route is configured so that wherever packets from the 172.16.0.0/16 LAN are destined, they will go to the R1-ISP router." Why is a default route enough here? Because R2-Central has only one way out. A default route is the usual choice for a stub network with a single exit.
- Task 3: "Save ... in case the router is power cycled." What happens without Save? The running configuration is lost at the next reboot and the port and route are gone again.
- Reflection, "where might things go wrong?" A missing or wrong route (packet dropped at the router), a wrong next hop (packet sent to a router that drops it), a port down (frame dropped), a wrong mask on a route (matches the wrong destinations), or no route back on the other router (the request arrives, the reply cannot return).

**Report question 1: what data can an IP packet contain, and how do you see it in the tool?**

*In brief:* An IP packet is a header plus a payload. The header carries version, lengths, identification and fragment fields, TTL, the protocol number of the payload, a checksum, and the source and destination IP addresses. The payload is the transport unit: ICMP for a ping, UDP for DNS, TCP for HTTP. In Simulation mode, click the envelope or the Info square in the Event List; the PDU Information window's Inbound and Outbound PDU Details tabs list every header field. Taken at R2-Central it shows the IP addresses unchanged while the MAC addresses and TTL differ.

An IP packet is a header followed by a payload. The header holds: version (4), header length, type of service, total length, identification, flags and fragment offset (for splitting big packets), time to live (TTL, lowered by one at every router, the packet is dropped at zero), the protocol number of what is inside (1 for ICMP, 6 for TCP, 17 for UDP), a header checksum, and the source and destination IP addresses. The payload is whatever the transport layer hands down: an ICMP echo request for a ping, a UDP datagram with a DNS message, or a TCP segment with part of an HTTP page.

To see it in Packet Tracer: Simulation mode, send the test ping from 1A to Eagle Server, press Capture / Forward once or twice, then click the envelope on the workspace or the coloured square in the Info column of the Event List. The PDU Information window opens. The OSI Model tab shows the packet layer by layer. The Inbound PDU Details and Outbound PDU Details tabs show the actual fields: the Ethernet frame on top, then the IP header with every field named (VER, IHL, TL, ID, FLAGS, TTL, PRO, CHKSUM, SRC IP, DST IP) and then the ICMP message. Take this screenshot while the packet is at R2-Central: source 172.16.1.1 and destination 192.168.254.254 are the same on both tabs, the MAC addresses and the TTL are not.

**Report question 2: what is a route, and what does "a packet is routed" mean?**

*In brief:* A route is one line in a router's table: to reach network X with mask Y, send to next hop Z. The default route 0.0.0.0/0 means "everything else goes to Z", here R1-ISP at 10.10.10.6. A packet is routed when each router matches its destination address against the table, picks the most specific line, lowers the TTL, and re-wraps the packet in a new frame for the next hop. This repeats until a router has the destination network directly connected and delivers it. Without a matching line the packet is dropped, which is why the ping failed before the fix.

A route is one line in a router's routing table: "to reach destination network X with mask Y, send to next hop Z (or out of port W)". R2-Central's table has its two directly connected networks and, after this activity, the default route 0.0.0.0/0 with next hop 10.10.10.6, meaning "anything I have no better line for goes to R1-ISP".

"The packet is routed" means that at every router the destination address is compared with the table, the most specific matching line is chosen, the TTL is lowered by one, and the packet is wrapped in a new frame addressed to that next hop. This repeats hop by hop until a router has the destination network directly connected and delivers the packet there. Before the fix the packet was dropped at R2-Central because no line matched; after the default route exists it goes to R1-ISP, which has 192.168.254.0/24 connected and delivers it to Eagle Server. The reply comes back the same way because R1-ISP already has a route to 172.16.0.0/16.

---

## Screenshots to collect for the report

- Check Results with the Assessment Items tab, one per activity (five).
- PTSkills 2: the Event List of the first ping with ARP lines above the ICMP line.
- PTSkills 4: the filtered Event List showing the DNS, TCP and HTTP order.
- PTSkills 5: the PDU Information window (Inbound or Outbound PDU Details) with the IP header fields, taken at R2-Central; and the routing table before and after the default route.

# Z0025E Computer Networks, Lab 2 report: PTSkills 1 to 5

Group: (names)
Date: 2 October 2026
Packet Tracer version used: (8.0.0 / 8.2.2 / 9.0.1)

This report follows the "Lab Report" section of the Canvas assignment 9.5 Lab 2: one screenshot of Check Results with the Assessment Items tab per activity, and the answers to the questions of each activity.

## PTSkills 1: Introduction to Packet Tracer

**Completion**

[Screenshot: Check Results, Assessment Items tab, PTSkills 1, 2 of 2 items, 100 %]

**Question: Explain the difference between a router and a switch**

A switch connects devices inside one network. It forwards frames by MAC address, using a table it builds by watching which address appears on which port. All its ports are in the same network; in the lab, S1-Central's ports are all in VLAN 1 (172.16.0.0/16), and the switch only has an IP address so it can be managed (172.16.254.1). A switch passes frames on unchanged and sends broadcasts out of every port.

A router connects different networks. Every port of a router is in a different network, and the router forwards packets by IP address using its routing table. R2-Central joins the LAN 172.16.0.0/16 (port Fa0/0, 172.16.255.254) to the serial link 10.10.10.4/30 (port S0/0/0, 10.10.10.5); R1-ISP joins that link to the server network 192.168.254.0/24. When a router forwards a packet it discards the old frame, lowers the TTL by one and builds a new frame for the next hop, so the MAC addresses change at every router while the IP addresses stay the same. A router does not forward broadcasts. In Packet Tracer the difference shows on mouse-over: a router lists an IP address per port, a switch lists VLAN membership per port and no port addresses.

## PTSkills 2: Examining Packets

**Completion**

[Screenshot: Check Results, Assessment Items tab, PTSkills 2, 6 of 6 items, 100 %]

**Question: In Task 2, it says "The first time you issue this one-shot ping message, it will show as Failed--this is because of the ARP process". Find out why is this so by doing your own (re)search.**

A ping is an ICMP echo request. It travels inside an IP packet, and the IP packet travels inside an Ethernet frame. To build the frame, PC 1B needs the MAC address of the next device on the path. Eagle Server is in another network, so the frame must go to the default gateway 172.16.255.254, and the PC does not yet know that router's MAC address. It therefore first sends an ARP request as a broadcast ("who has 172.16.255.254?"), and R2-Central answers with its MAC address. While the PC waits for that answer, the ping that caused the lookup is discarded, which is what many real operating systems also do. That is why the first attempt shows Failed. The same lookup happens again at R1-ISP, which must ask for Eagle Server's MAC address before it can deliver the packet. The second ping succeeds because every ARP table along the path is now filled. In Simulation mode this is visible: the first run shows ARP frames (destination FFFF.FFFF.FFFF) before any ICMP, the second run shows only ICMP. ARP entries expire after a few minutes, so a later ping can fail again for the same reason.

[Optional screenshot: Event List of the first ping with the ARP lines above the ICMP line]

## PTSkills 3: Configuring Hosts and Services

**Completion**

[Screenshot: Check Results, Assessment Items tab, PTSkills 3, 11 of 11 items, 100 %]

**Question: Can you now explain the process that occurs when you type a URL into a browser and a web page returns? What types of client-server interactions are involved?**

Typing eagle-server.example.com into the browser on PC 1B starts two separate conversations, both started by the PC.

1. Name lookup (DNS). The browser asks the PC's DNS client for the address behind the name. The PC sends a DNS query in a UDP datagram to port 53 of its configured DNS server, 192.168.254.254, which is Eagle Server. The server looks up its record ("eagle-server.example.com, A, 192.168.254.254") and answers with the IP address.
2. Page transfer (HTTP). The browser opens a TCP connection to that address on port 80: a three-way handshake (SYN from the PC, SYN-ACK from the server, ACK from the PC). Over that connection the browser sends an HTTP GET request for the page; the server's HTTP service answers with HTTP 200 OK and the HTML of the page, which the browser renders. Finally the connection is closed with FIN and ACK segments.

The client-server interactions are therefore a DNS client talking to a DNS server over UDP, and an HTTP client talking to an HTTP server over TCP. Both are request and reply, and the client always asks first. Underneath, every packet travels PC 1B, S1-Central, R2-Central, R1-ISP, Eagle Server and back, with ARP supplying MAC addresses where needed.

[Diagram: two vertical lines, PC 1B and Eagle Server, with arrows top to bottom: DNS query, DNS reply, SYN, SYN-ACK, ACK, HTTP GET, HTTP 200 OK, FIN/ACK]

## PTSkills 4: Analyzing the Application and Transport Layers

**Completion**

[Screenshot: Check Results, Assessment Items tab, PTSkills 4, 15 of 15 items, 100 %]

**Question 1: Can you make a diagram of the sequence of protocol events involved in requesting a web page using a URL?**

[Diagram or screenshot of the filtered Event List]

The sequence, with the transport protocol on each step:

1. DNS query, UDP port 53, PC 1A to Eagle Server
2. DNS reply, UDP, Eagle Server to PC 1A
3. TCP SYN, port 80, PC 1A to Eagle Server
4. TCP SYN-ACK, Eagle Server to PC 1A
5. TCP ACK, PC 1A to Eagle Server
6. HTTP GET inside TCP, PC 1A to Eagle Server
7. HTTP 200 OK with the page inside TCP, possibly several segments, Eagle Server to PC 1A
8. TCP ACKs for the data, PC 1A to Eagle Server
9. TCP FIN and ACK in both directions

**Question 2: Where might things go wrong? (Think about, what happens if router configuration is wrong? Does the package get stuck at the router, does it disappear?)**

- Wrong or missing DNS server on the PC: the name is never resolved, no HTTP traffic is sent at all, and the browser reports that the name cannot be resolved.
- Wrong default gateway or subnet mask on the PC: the packet is sent to the wrong neighbour or never leaves the LAN; nobody answers and the request times out.
- Router port turned off or without an address: the frame reaches the router and is dropped there. In Simulation mode the envelope gets a red cross at R2-Central.
- Router without a route to the destination network: the router discards the packet immediately. It does not hold or queue it. A real router also sends an ICMP "destination unreachable" message back to the sender; in Packet Tracer the packet simply disappears at the router and the sender sees a timeout.
- Server powered off, or DNS or HTTP service off: the packets arrive but nothing answers; the client waits and gives up.
- Wrong cable type between server and router: the link never comes up and nothing passes at all.

**Question 3: Compare and contrast DNS and HTTP, and UDP and TCP.**

DNS and HTTP are both application-layer protocols in which a client asks and a server answers. DNS translates a name into an address with one short query and one short reply, uses UDP port 53, and must complete before HTTP can start. HTTP fetches the content itself, uses TCP port 80, has methods such as GET and status codes such as 200, and its answers can be large and split over many segments.

UDP and TCP are the two transport protocols beneath them. UDP is connectionless: one datagram, no handshake, no acknowledgement, no retransmission; it is fast and light, which suits a tiny DNS exchange. TCP is connection-oriented: a handshake before any data, sequence numbers and acknowledgements so lost segments are resent and order is kept, flow and congestion control, and an orderly close. This costs extra packets, as can be counted in the Event List, but guarantees that the whole page arrives complete and in order.

## PTSkills 5: Routing IP Packets

**Completion**

[Screenshot: Check Results, Assessment Items tab, PTSkills 5, 4 of 4 items, 100 %]

**Question 1: What data can an IP Packet contain? See if you can find out how to view this information from within the tool when you send a test packet.**

An IP packet consists of a header and a payload. The header holds the version (4), the header length, the type of service, the total length, an identification number with flags and a fragment offset (used when a packet has to be split), the time to live (TTL, lowered by one at every router and dropped at zero), the protocol number of the payload (1 for ICMP, 6 for TCP, 17 for UDP), a header checksum, and the source and destination IP addresses. The payload is whatever the transport layer hands down: an ICMP echo request for a ping, a UDP datagram carrying a DNS message, or a TCP segment carrying part of an HTTP page.

In Packet Tracer this can be viewed in Simulation mode: send the test ping from PC 1A to Eagle Server, press Capture / Forward, then click the envelope on the workspace or the coloured square in the Info column of the Event List. The PDU Information window opens. Its OSI Model tab shows the packet layer by layer, and the Inbound PDU Details and Outbound PDU Details tabs show the actual fields: the Ethernet frame, then the IP header with every field named (VER, IHL, TL, ID, FLAGS, TTL, PRO, CHKSUM, SRC IP, DST IP), then the ICMP message.

[Screenshot: PDU Information window, Outbound PDU Details, taken while the packet is at R2-Central. Source 172.16.1.1 and destination 192.168.254.254 are the same on the inbound and outbound side; the MAC addresses and the TTL differ.]

**Question 2: What is a route? What does it mean a packet is routed?**

A route is one line in a router's routing table: "to reach destination network X with mask Y, send to next hop Z (or out of port W)". R2-Central's table contains its two directly connected networks and, after this activity, the default route 0.0.0.0/0 with next hop 10.10.10.6, which means "anything I have no better entry for goes to R1-ISP".

"The packet is routed" means that at every router the destination address is compared with the routing table, the most specific matching line is chosen, the TTL is lowered by one, and the packet is placed into a new frame addressed to that next hop. This repeats hop by hop until a router has the destination network directly connected and delivers the packet there. Before the fix the packet was dropped at R2-Central because no line matched; after the default route exists it is forwarded to R1-ISP, which has 192.168.254.0/24 connected and delivers it to Eagle Server. The reply returns the same way because R1-ISP already has a route to 172.16.0.0/16.

[Optional screenshots: the routing table of R2-Central before and after the default route]

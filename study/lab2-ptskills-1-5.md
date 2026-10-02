# Lab 2: PTSkills 1 to 5, draft answers

Source: Canvas assignment "9.5 Lab 2 (Submit your report)" (course 614, assignment 3042) and the instructions inside the five activity files. Report due 2 October 2026 (PDF, one submission per group, 5 points, one per activity). Written 2 October 2026 from the standard lab topology: R1-ISP, R2-Central, S1-Central, PC 1A, PC 1B, Eagle Server.

Required in the report, per activity: a screenshot of Check Results with the Assessment Items tab, and the answers below. Use the converted `_v8` files from `converted/` when working in Packet Tracer 8.2.x or 9.x; the Canvas originals cannot reach 100 % there.

## PTSkills 1: explain the difference between a router and a switch

A switch works at layer 2. It forwards Ethernet frames inside one local network by looking at the destination MAC address and its MAC address table, which it fills by watching the source addresses of frames that arrive on each port. All its ports belong to the same network; in the lab, S1-Central's ports are all in VLAN 1, 172.16.0.0/16, and the switch itself only has an IP address for management (172.16.254.1). A switch does not change the frame it forwards.

A router works at layer 3. Each of its interfaces belongs to a different network, and it forwards IP packets between those networks by looking at the destination IP address and its routing table. R2-Central connects 172.16.0.0/16 (Fa0/0, 172.16.255.254) to the serial link 10.10.10.4/30 (S0/0/0, 10.10.10.5); R1-ISP connects that link to the server network 192.168.254.0/24. When a router forwards a packet it strips the old frame, decrements the TTL and builds a new frame for the next hop, so MAC addresses change at every router while IP addresses stay the same. A router also stops broadcasts; a switch floods them. In Packet Tracer the difference is visible on mouse-over: a router shows an IP address per port, a switch shows VLAN membership per port and no IP addresses.

## PTSkills 2: why the first one-shot ping fails (ARP)

A ping from PC 1B to Eagle Server is an ICMP echo request inside an IP packet, and IP packets travel inside Ethernet frames. To build the frame, 1B needs a destination MAC address. Eagle Server is on another network, so the frame must go to the default gateway, 172.16.255.254, and 1B does not yet know the gateway's MAC address. It first sends an ARP request ("who has 172.16.255.254?") as a broadcast; R2-Central answers with its MAC. Packet Tracer models what many operating systems do while waiting: the echo request that triggered the lookup is discarded, so the test shows Failed. The same lookup happens again at R1-ISP, which must ARP for Eagle Server's MAC on 192.168.254.0/24 before it can deliver. The second ping succeeds because every ARP table along the path is now filled.

In Simulation mode this is visible: the first run shows ARP frames (broadcast, destination FFFF.FFFF.FFFF) before any ICMP, the second run shows only ICMP. ARP entries age out after a while, which is why a ping can fail again later.

Screenshot: the Event List of the first ping showing ARP before ICMP.

## PTSkills 3: from URL to web page, and the client-server interactions

Typing eagle-server.example.com into the browser on PC 1B starts two separate client-server exchanges.

1. Name resolution. The browser asks the PC's DNS client to turn the name into an address. The PC sends a DNS query in a UDP datagram to port 53 of its configured DNS server, 192.168.254.254 (Eagle Server). The server looks up its record ("eagle-server.example.com, A, 192.168.254.254") and answers with the IP address.
2. Web transfer. The browser opens a TCP connection to that address on port 80: a three-way handshake (SYN, SYN-ACK, ACK). Over that connection it sends an HTTP GET request for the page; the server's HTTP service answers with an HTTP 200 OK response that carries the HTML, and the browser renders it. Finally the connection is closed with FIN and ACK segments.

Both are client-server interactions started by the client: DNS client to DNS server over UDP, HTTP client to HTTP server over TCP. Underneath, every packet is routed PC 1B to S1-Central to R2-Central to R1-ISP to Eagle Server and back, with ARP filling in MAC addresses as in PTSkills 2.

Diagram: two vertical lines (PC 1B, Eagle Server) with arrows in this order: DNS query, DNS reply, SYN, SYN-ACK, ACK, HTTP GET, HTTP 200 OK, FIN/ACK.

## PTSkills 4: sequence diagram, failure points, DNS vs HTTP, UDP vs TCP

Diagram: the same ladder as above with the transport protocol written on each arrow: DNS query and reply on UDP 53, then the TCP handshake, HTTP GET and HTTP response on TCP 80, then the TCP close. The Event List in Simulation mode, with the filter set to DNS, UDP, HTTP, TCP and ICMP, gives this order directly; a screenshot of that list works as the diagram.

Where things go wrong, and what happens to the packet:

- Wrong or missing DNS server on the PC: the name is never resolved, no HTTP traffic is sent at all, the browser shows a name error.
- Wrong default gateway or subnet mask on the PC: the packet is sent to the wrong next hop or never leaves the LAN; the switch forwards it, nobody answers.
- Router interface down or without an address (the PTSkills 5 situation): the frame reaches the router and is dropped there; in Simulation mode the envelope gets a red cross at R2-Central.
- Router without a route to the destination network: the router discards the packet. It does not queue it or hold it; a packet with no matching route is dropped, and a real router sends back an ICMP "destination unreachable". In Packet Tracer the packet simply disappears at that router and the sender sees a timeout.
- Server services off (DNS or HTTP disabled on Eagle Server): the packets arrive but nobody answers, so the client waits and gives up.

DNS versus HTTP: both are application-layer, client-server, request-response protocols. DNS translates names to addresses in one short query and one short reply, uses UDP port 53, and is needed before HTTP can start. HTTP transfers the content itself, uses TCP port 80, has methods (GET) and status codes (200), and can carry large responses over many segments.

UDP versus TCP: UDP is connectionless; it sends one datagram with no handshake, no acknowledgement and no retransmission, so it is fast and light, which suits a tiny DNS exchange. TCP is connection-oriented: a handshake before data, sequence numbers and acknowledgements so lost segments are resent and order is kept, flow and congestion control, and an orderly close. That costs extra packets (count them in the Event List) but guarantees that the whole web page arrives intact.

## PTSkills 5: what an IP packet contains, what a route is

What an IP packet contains: a header and a payload. The header holds the version (4), header length, type of service, total length, identification, flags and fragment offset, time to live, the protocol number of what is inside (1 for ICMP, 6 for TCP, 17 for UDP), a header checksum, and the source and destination IP addresses. The payload is the transport-layer unit: here an ICMP echo request, in the earlier activities a UDP datagram with a DNS message or a TCP segment with HTTP.

How to see it in the tool: in Simulation mode, send the test PDU from 1A to Eagle Server, then click the envelope on the workspace or the coloured square in the Info column of the Event List. The PDU Information window opens; the "Inbound PDU Details" and "Outbound PDU Details" tabs show the frame, the IP header with every field named and filled, and the ICMP message below it; the "OSI Model" tab shows the same packet layer by layer. Screenshot that window at R2-Central: it shows the source 172.16.1.1 and destination 192.168.254.254 unchanged while the MAC addresses differ on the inbound and outbound sides.

What a route is: one line in a router's routing table that says "for destination network X with mask Y, send to next hop Z (or out interface W)". R2-Central's table has its two directly connected networks and, after Task 3, the default route 0.0.0.0/0 with next hop 10.10.10.6, which means "anything I have no better entry for goes to R1-ISP".

"The packet is routed" means that at each router the destination address is compared with the table, the most specific matching route is chosen, the TTL is decreased by one, and the packet is put into a new frame addressed to the next hop; this repeats hop by hop until a router has the destination network directly connected and delivers the packet. Before Task 3 the packet was dropped at R2-Central because no entry matched; after the default route exists it is forwarded to R1-ISP, which has 192.168.254.0/24 connected and delivers it to Eagle Server.

## Screenshots to collect

- Check Results with the Assessment Items tab, one per activity (five in total).
- PTSkills 2: Event List of the first ping showing ARP before ICMP.
- PTSkills 4: the filtered Event List with the DNS, TCP and HTTP order.
- PTSkills 5: the PDU Information window with the IP header fields, taken at R2-Central.

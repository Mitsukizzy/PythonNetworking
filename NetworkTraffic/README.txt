USC ID: 8436341111
Name: Isabella "Izzy" Benavente
Python Version: 2.7.12
Additional Library: pypcap


Ping Tool Usage:
	CASE 1 - $ sudo python ping.py -d 206.190.36.45 -c 4 -p "hello"
	CASE 2 - $ sudo python ping.py -d 1.2.3.4 -c 5 -p "Hello"
	CASE 3 - (Disconnect host from internet and run CASE 1)

Traffic Sniffer Usage
	INT  - $ python trafficviewer.py -i en0 -c 6
	READ - $ python trafficviewer.py -r icmp.pcap -c 5
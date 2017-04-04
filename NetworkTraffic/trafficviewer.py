""" Assignment 2 - CSCI 353 Spring 2017
	Isabella Benavente
	Using Python 2.7.12 
	Traffic Viewer Module 
	USAGE: $ python trafficviewer.py -i en0 -c 6
"""
#!/usr/bin/python2 

import socket
import sys, time
import struct
import pcap
import getopt
import logging
import select
import random

ECHO_CODE = 8

class Ping():
	
	read = ''
	count = ''
	interface = ''

	sent = 0
	rcvd = 0
	lost = 0

	TTL = 64

	pmin = TTL
	pmax = 0
	psum = 0

	def __init__(self):        
		# Init socket, parameters are to specify internet, raw socket, and int type
		# Need to run as root for ICMP (use sudo)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
			#self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		except socket.error, message:
			print 'Socket creation failed. Error: ' + str(message[0]) + ' Message ' + message[1]
			sys.exit()

	def getChecksum(self, source_string):
		# Checksum function source: https://gist.github.com/pklaus/856268
		sum = 0
		count_to = (len(source_string) / 2) * 2
		count = 0
		while count < count_to:
			this_val = ord(source_string[count + 1])*256+ord(source_string[count])
			sum = sum + this_val
			sum = sum & 0xffffffff # Necessary?
			count = count + 2
		if count_to < len(source_string):
			sum = sum + ord(source_string[len(source_string) - 1])
			sum = sum & 0xffffffff # Necessary?
		sum = (sum >> 16) + (sum & 0xffff)
		sum = sum + (sum >> 16)
		answer = ~sum
		answer = answer & 0xffff
		# Swap bytes. Bugger me if I know why.
		answer = answer >> 8 | (answer << 8 & 0xff00)
		return answer

	def makePacket(self, idnum):
		checksum = self.getChecksum(self.payload)
		header = struct.pack("BBHHH", ECHO_CODE, 0, 0, idnum, self.sent)
		checksum = self.getChecksum(header + self.payload)
		header = struct.pack("BBHHH", ECHO_CODE, 0, socket.htons(checksum), idnum, self.sent)
		packet = header + self.payload
		return packet

	def receive(self, id, timeSent):
		timeLeft = timeSent
		RTT = 0
		while timeLeft > 0:
			status = select.select([self.sock], [], [], timeLeft)
			RTT = time.time() - timeSent
			RTT = int(round(RTT * 1000))
			if RTT > self.TTL:
				self.lost += 1
				return
			data, rcvAddr = self.sock.recvfrom(2048) # buffer size in bytes
			header = data[20:28]
			type, code, checksum, pid, seq = struct.unpack("BBHHH", header)

			if id == pid:				
				reply = data[28:]
				print "  Reply from " + rcvAddr[0] + ": bytes=" + str(len(reply)) + " time="  + str(RTT) + "ms TTL=" + str(self.TTL)

				self.pmin = min(self.pmin, RTT)
				self.pmax = max(self.pmax, RTT)
				self.psum += RTT

				self.rcvd += 1
				return

	def showSummary(self):
		pavg = (self.psum / self.sent)
		ppct = (self.lost / self.sent) * 100
		if self.rcvd == 0:
			self.pmin = 0

		print "Ping statistics for " + self.dst
		print "  Packets: Sent = " + str(self.sent) + ", Received = " + str(self.rcvd) + ", Lost = " + str(self.lost) + " (" +  str(ppct) + "% loss)"

		if self.rcvd > 0:
			print "  Approximate round trip times in milli-seconds:"
			print "  Minimum = " +  str(self.pmin) + "ms, Maximum = " + str(self.pmax) + "ms, Average = " + str(pavg) + "ms"

	
	def main(self, argv):
		"""Main function in PING"""

		argv = sys.argv[1:]
		logfile = ''

		try:
			opts, args = getopt.getopt(argv, "hl:i:c:r:", ["logfile=", "int=", "count=", "read="])
		except getopt.GetoptError:
			print('test.py -l <logfile> -i <int> -c <count> -r <read>')
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print('test.py -l <logfile> -i <int> -c <count> -r <read>')
				sys.exit()
			elif opt in ("-l", "--logfile"):
				logfile = arg
			elif opt in ("-i", "--int"):
				self.interface = arg
			elif opt in ("-c", "--count"):
				self.count = int(arg)              
			elif opt in ("-r", "--read"):
				self.read = arg

		# Verify command line args
		if self.interface == '' and self.read == '':
			# Interface and read are mutually exclusive, should not both be specified
			print "USAGE: sudo test.py -i <interface> -c <count> -r <read> (OPTIONAL: -l <logfile>)"
			sys.exit(0)

		if (self.interface != '' and self.count == '') or (self.count != '' and self.interface ==''):
			# Interface and count both need to be set together in order to work
			print "USAGE: sudo test.py -i <interface> -c <count> -r <read> (OPTIONAL: -l <logfile>)"
			sys.exit(0)

		# Configure log file path, format, and clear file each time using write mode
		if logfile != '':
			logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(message)s', filemode ='w')
			logging.info("Payload: " + self.payload + ", Count: " + str(self.count) + ", Destination: " + self.dst)

		print "Viewer: listening on " + self.interface

		sniffer = pcap.pcap(name=self.interface)
		addr = lambda pkt, offset: '.'.join(str(ord(pkt[i])) for i in xrange(offset, offset + 4)).ljust(16)
		for ts, pkt in sniffer:
			print ts, '\t', addr(pkt, sniffer.dloff + 12), '\t>\tDST', addr(pkt, sniffer.dloff + 16)

		logging.info("Exiting network traffic viewer...")

ping = Ping()
ping.main(sys.argv[1:])

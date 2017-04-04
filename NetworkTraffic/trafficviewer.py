""" Assignment 2 - CSCI 353 Spring 2017
	Isabella Benavente
	Using Python 2.7.12 and pypcap
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
import decimal

ECHO_CODE = 8

class Viewer():
	
	read = ''
	count = ''
	interface = ''

	def __init__(self):        
		# Init socket, parameters are to specify internet, raw socket, and int type
		# Need to run as root for ICMP (use sudo)
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
			#self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		except socket.error, message:
			print 'Socket creation failed. Error: ' + str(message[0]) + ' Message ' + message[1]
			sys.exit()

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
		if (self.interface == '' and self.read == '') or (self.interface != '' and self.read != ''):
			# Interface and read are mutually exclusive, should not both be specified or both empty
			print "USAGE: sudo test.py -i <interface> -c <count> -r <read> (OPTIONAL: -l <logfile>)"
			sys.exit(0)
		elif self.count == '':
			# Count must always be specified
			print "USAGE: sudo test.py -i <interface> -c <count> -r <read> (OPTIONAL: -l <logfile>)"
			sys.exit(0)

		# Configure log file path, format, and clear file each time using write mode
		if logfile != '':
			logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(message)s', filemode ='w')
			logging.info("Payload: " + self.payload + ", Count: " + str(self.count) + ", Destination: " + self.dst)

		if self.interface != '':
			# Traffic Viewing mode
			print "Viewer: listening on " + self.interface

			sniffer = pcap.pcap(name=self.interface, immediate=True)
			addr = lambda packet, offset: '.'.join(str(ord(packet[i])) for i in xrange(offset, offset + 4)).ljust(16)
			data = lambda packet, offset: "".join(str(ord(packet[i])) for i in xrange(offset, offset + 2)).ljust(8)
			tcp = lambda packet, offset: "".join(str(ord(packet[i])) for i in xrange(offset, offset + 4)).ljust(16)
			for timestamp, packet in sniffer:
				print "{0:.6f}".format(timestamp) + '  ' + addr(packet, sniffer.dloff + 12) + ">  " + addr(packet, sniffer.dloff + 16) + "| " + data(packet, sniffer.dloff + 8) + "id: " + data(packet, sniffer.dloff + 4) + "seq: " + tcp(packet, sniffer.dloff + 28) + "length: " + data(packet, sniffer.dloff + 2)
		elif self.read != '':
			# File Reading mode
			p = pcap.open(file(self.read))
			for i in p:
				print "Packet " + i + " " + p.version + " " + p.length + " " + p.linktype

		logging.info("Exiting network traffic viewer...")

viewer = Viewer()
viewer.main(sys.argv[1:])

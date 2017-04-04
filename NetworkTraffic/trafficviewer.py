""" Assignment 2 - CSCI 353 Spring 2017
	Isabella Benavente
	Using Python 2.7.12 and pypcap
	Traffic Viewer Module 
	USAGE: 
		INT  - $ python trafficviewer.py -i en0 -c 6
		READ - $ python trafficviewer.py -r icmp.pcap -c 5
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

	def printPcap(self, source):
		i = 0
		source.setfilter('icmp') # We only care about ICMP

		addr = lambda packet, offset: '.'.join(str(ord(packet[i])) for i in xrange(offset, offset + 4)).ljust(16)
		oneByte = lambda packet, offset: ''.join(str(ord(packet[i])) for i in xrange(offset, offset + 1)).ljust(4)
		twoByte = lambda packet, offset: ''.join(str(ord(packet[i])) for i in xrange(offset, offset + 2)).ljust(8)
		fourByte = lambda packet, offset: ''.join(str(ord(packet[i])) for i in xrange(offset, offset + 16)).ljust(16)

		for t, p in source:
			if i >= self.count:
				break

			icmpCode = self.translateICMPCode(oneByte(p, source.dloff + 20))

			print "{0:.6f}".format(t),	# print timestamp with 6 decimals
			print addr(p, source.dloff + 12) + ">  " + addr(p, source.dloff + 16),
			print "| ICMP " + icmpCode.ljust(16),
			print "id: " + twoByte(p, source.dloff + 24) + "   seq: " + twoByte(p, source.dloff + 26),
			print "length: " + twoByte(p, source.dloff + 2)
			i += 1
	
	def translateICMPCode(self, code):
		# Reference to ICMP Type Numbers: https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml
		# Only going to translate codes up to 0-12 so this doesn't get unruly and long 
		code = int(code)

		if code == 0:
			return "echo reply"
		elif code == 3:
			return "destination unreachable"
		elif code == 4:
			return "source quench"			
		elif code == 5:
			return "redirect"
		elif code == 6:
			return "alternate host address"
		elif code == 8:
			return "echo request"
		elif code == 9:
			return "router advertisment"
		elif code == 10:
			return "router soliciation"
		elif code == 11:
			return "time exceeded"
		elif code == 12:
			return "parameter problem"
		elif code == 1 or code == 2 or code == 7:
			return "unassigned"

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
			logging.info("Count: " + str(self.count))

		if self.interface != '':
			# Traffic Viewing mode
			print "Viewer: listening on " + self.interface
			sniffer = pcap.pcap(name=self.interface, immediate=True)
			self.printPcap(sniffer)			
		elif self.read != '':
			# File Reading mode
			print "Reader: viewing from " + self.read
			pfile = pcap.pcap(self.read)
			self.printPcap(pfile)

		logging.info("Exiting network traffic viewer...")

viewer = Viewer()
viewer.main(sys.argv[1:])

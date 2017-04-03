""" Assignment 2 - CSCI 353 Spring 2017
	Isabella Benavente
	Using Python 2.7.12 
	Ping Tool Module 
	USAGE: $ python ping.py -d 206.190.36.45 -c 4 -p "hello"
"""
#!/usr/bin/python2 

import socket
import sys, time
import struct
import pcap
import getopt
import logging
import random

ECHO_CODE = 8

class Ping():
	
	payload = ''
	count = ''
	dst = ''

	sent = 0
	rcvd = 0
	lost = 0
	TTL = 64

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

	def makePacket(self, idnum, payload):
		checksum = self.getChecksum(payload)
		header = struct.pack("BBHHH", ECHO_CODE, 0, 0, idnum, self.sent)
		payload =  payload
		checksum = self.getChecksum(header + payload)
		header = struct.pack("BBHHH", ECHO_CODE, 0, socket.htons(checksum), idnum, self.sent)
		packet = header + payload
		return packet

	def receive(self):
		print "Waiting for reply"
		while True:
			data, rcvAddr = self.sock.recvfrom(2048) # buffer size in bytes
			header = data[20:28]
			reply = data[28:]
			type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", header)
			print "Reply from " + rcvAddr[0] + ": bytes=" + str(len(reply)) + " time=" + "ms TTL=" + str(self.TTL)
			self.rcvd += 1
			print reply

			if self.rcvd == self.count:
				self.showSummary(rcvAddr[0])
				break

	def showSummary(self, dst):
		print "Ping statistics for " + dst
		print "  Packets: Sent = " + str(self.sent) + ", Received =" + str(self.rcvd) + ", Lost = " + str(self.lost) + "(% loss)"
		print "  Approximate round trip times in milli-seconds:"
		print "  Minimum = " + "ms, Maximum =" + "ms, Average =" + "ms"

	
	def main(self, argv):
		"""Main function in PING"""

		argv = sys.argv[1:]
		logfile = ''

		try:
			opts, args = getopt.getopt(argv, "hl:p:c:d:", ["logfile=", "payload=", "count=", "dst="])
		except getopt.GetoptError:
			print('test.py -l <logfile> -p <payload> -c <count> -d <dst>')
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print('test.py -l <logfile> -p <payload> -c <count> -d <dst>')
				sys.exit()
			elif opt in ("-l", "--logfile"):
				logfile = arg
			elif opt in ("-p", "--payload"):
				payload = arg
			elif opt in ("-c", "--count"):
				self.count = int(arg)              
			elif opt in ("-d", "--dst"):
				dst = arg

		# Configure log file path, format, and clear file each time using write mode
		if logfile != '':
			logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(message)s', filemode ='w')
			logging.info("Payload: " + payload + ", Count: " + str(self.count) + ", Destination: " + dst)

		self.src = socket.gethostbyname(socket.gethostname())
		print "Payload: " + payload + ", Count: " + str(self.count) + ", Destination: " + dst

		idnum = int((id(self.TTL) * random.random()) % 65535)
		packet = self.makePacket(idnum, payload)   
		print "packet: " + packet

		# Send out packets
		for x in range(0, self.count):            
			print "Pinging " + dst + " with " + str(len(payload)) + " bytes of data \"" + payload + "\""
			self.sock.sendto(packet, (dst, 0))
			self.sent += 1

		# Get ready to receive replies
		self.receive() 
		self.sock.close()

		logging.info("terminating client..")

ping = Ping()
ping.main(sys.argv[1:])

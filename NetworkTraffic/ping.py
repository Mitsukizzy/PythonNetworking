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

ECHO_REQUEST = 8

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
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        except socket.error, message:
            print 'Socket creation failed. Error: ' + str(message[0]) + ' Message ' + message[1]
            sys.exit()
            
        self.shouldExit = False

    def getChecksum(self, payload):
        # Got this checksum function from an article on BinaryTides
        checksum = 0
        
        for i in range(0, len(payload)-1, 2):
            w = ord(payload[i]) + (ord(payload[i+1]) << 8 )
            checksum = checksum + w
        
        checksum = (checksum>>16) + (checksum & 0xffff)
        checksum = checksum + (checksum >> 16)
        checksum = ~checksum & 0xffff
        
        return int(checksum)

    def makePacket(self, idnum, payload):
        checksum = self.getChecksum(payload)
        header = struct.pack("bbHHh", 8, 0, 0, idnum, 1)
    	packet = 192 * 'F' + payload
        checksum = self.getChecksum(header + packet)
        header = struct.pack("bbHHh", 8, 0, checksum, idnum, 1)
        packet = header + packet
        return packet

    def receive(self):
        while self.shouldExit == False:
            print "Waiting for reply"
            reply, rcvAddr = self.sock.recvfrom(2048) # buffer size in bytes
            print "Got reply"
            header = reply[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack("BBHHH", header)
            print "Reply from " + ": bytes=" + " time=" + "ms TTL=" + self.TTL
            self.rcvd += 1
            logging.info(data[0])
            print data[0]

            if self.rcvd == self.count:
                self.showSummary(self)

    def showSummary(self):
        print "Ping statistics for " + dst
        print "  Packets: Sent = " + sent + ", Received =" + rcvd + ", Lost = " + lost + "(% loss)"
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
        #print "Source IP: " + self.src
        #packet = IP(src=src, dst=dst)/ICMP()
        # srloop(packet, count=3)

        # For ease of use in instance function
        port = int(80)        
        self.port = port

        # data = self.sock.recvfrom(1024) # buffer size in bytes
        # welcomedata = data[0].split(' ')
        # if welcomedata[0] == 'welcome':
        #     client1 = welcomedata[1]

        print "Payload: " + payload + ", Count: " + str(self.count) + ", Destination: " + dst

        idnum = int((id(self.TTL) * random.random()) % 65535)
        packet = self.makePacket(idnum, payload)   
        print "packet: " + packet
        
        while packet:   
            print "Pinging " + dst + " with " + str(len(payload)) + " bytes of data \"" + payload + "\""
            sent = self.sock.sendto(packet, (dst, 1))
            packet = packet[sent:]

        # Sent out packets
        # for x in range(0, self.count):            
        #     print "Pinging " + dst + " with " + str(len(payload)) + " bytes of data \"" + payload + "\""
        #     self.sock.sendto(packet, (dst, self.port))
        #     self.sent += 1

        # Get ready to receive replies
        self.receive() 
        self.sock.close()

        logging.info("terminating client..")

ping = Ping()
ping.main(sys.argv[1:])

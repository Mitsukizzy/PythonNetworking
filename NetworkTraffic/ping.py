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
import getopt
import logging
import threading

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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.shouldExit = False

    def send(self, dst, payload):    
        idnum = self.sent
        packet = struct.pack("bbHHh", ECHO_REQUEST, 0, idnum, idnum, 1)
        packet += payload
        print "Pinging " + dst + " with " + str(len(payload)) + " bytes of data \"" + payload + "\""

        self.sock.sendto(packet, (self.src, self.port))
        self.sent += 1

    def receive(self):
        while self.shouldExit == False:
            data = self.sock.recvfrom(1024) # buffer size in bytes
            reply = struct.unpack(data[0])
            print "Reply from " + ": bytes=" + " time=" + "ms TTL=" + self.TTL
            self.rcvd += 1
            logging.info(data[0])
            print data[0]

            if self.rcvd == self.count:
                Client.showSummary(self)

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
                self.count = arg                
            elif opt in ("-d", "--dst"):
                dst = arg

        # Configure log file path, format, and clear file each time using write mode
        if logfile != '':
            logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(message)s', filemode ='w')
            logging.info("Payload: " + payload + ", Count: " + self.count + ", Destination: " + dst)

        self.src = socket.gethostbyname(socket.gethostname())
        print "Source IP: " + self.src
        # packet = IP(src=src, dst=dst)/ICMP()
        # srloop(packet, count=3)

        # For ease of use in instance function
        port = int(80)        
        self.port = port

        # data = self.sock.recvfrom(1024) # buffer size in bytes
        # welcomedata = data[0].split(' ')
        # if welcomedata[0] == 'welcome':
        #     client1 = welcomedata[1]

        print "Payload: " + payload + ", Count: " + self.count + ", Destination: " + dst
        logging.info("received welcome")
            
        # Thread setup
        self.threadRecv = threading.Thread(target=Ping.receive, args=(self,))
        self.threadSend = threading.Thread(target=Ping.send, args=(self,dst,payload))
        self.threadRecv.setDaemon(True)
        self.threadSend.setDaemon(True)
        self.threadRecv.start()
        self.threadSend.start()       

        # Keep main thread alive
        try:
            while self.shouldExit == False:
                time.sleep(.1)
        except KeyboardInterrupt:
            self.shouldExit = True
            print "exit"
        
        logging.info("terminating client..")

ping = Ping()
ping.main(sys.argv[1:])

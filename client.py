""" Assignment 1 - CSCI 353 Spring 2017
    Isabella Benavente
    Using Python 2.7.12 
    CLIENT Module 
    USAGE: $ python client.py -s 127.0.0.1 -p 7022 -l client1log.txt -n Alice
    USAGE: $ python client.py -s 127.0.0.1 -p 7021 -l client2log.txt -n Bob
"""
#!/usr/bin/python2 
# Clients communicate using UDP

import socket
import sys, time
import getopt
import logging
import threading

class Client():
    
    serverip = ''
    port = ''
    logfile = ''
    clientname = ''
    
    def __init__(self):        
        # Init socket, parameters are to specify internet and UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.shouldExit = False

    def send(self):    
        message = ''
        while self.shouldExit == False:
            message = raw_input("")

            if message == "exit":
                self.shouldExit = True
                break

            msgparts = message.split(' ')
            # Expected message input is "sendto <client> <message>"
            if msgparts[0] != 'sendto' or len(msgparts) <= 2:
                print "Message format incorrect, part0 is " + msgparts[0] + " and len is " + str( len(msgparts) )
                continue
            
            # Construct message in the format "sendto <client> message <message>"
            index = message.find(msgparts[2])
            message = message[:index] + 'message ' + message[index:]
            self.sock.sendto(message, (self.serverip, self.port))

    def receive(self):
        print "waiting for messages.."
        while self.shouldExit == False:
            data = self.sock.recvfrom(1024) # buffer size in bytes
            print data[0]
    
    def main(self, argv):
        """Main function in CLIENT"""

        argv = sys.argv[1:]

        try:
            opts, args = getopt.getopt(argv, "hs:p:l:n:", ["serverIP=", "portno=", "logfile=", "myname="])
        except getopt.GetoptError:
            print('test.py -n <serverIP> -p <portno> -l <logfile> -n <myname>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('test.py -n <serverIP> -p <portno> -l <logfile> -n <myname>')
                sys.exit()
            elif opt in ("-s", "--serverIP"):
                serverip = arg
            elif opt in ("-p", "--portno"):
                port = arg
            elif opt in ("-l", "--logfile"):
                logfile = arg
            elif opt in ("-n", "--myname"):
                clientname = arg

        logging.basicConfig(filename=logfile, level=logging.DEBUG)
        logging.info("connecting to the server " + serverip + " at port " + port)
        
        # For ease of use in instance function
        port = int(port)        
        self.serverip = serverip
        self.port = port

        self.sock.sendto(("register " + clientname).encode(), (serverip, port))
        logging.info("sending register message " + clientname)

        data = self.sock.recvfrom(1024) # buffer size in bytes
        welcomedata = data[0].split(' ')
        if welcomedata[0] == 'welcome':
            client1 = welcomedata[1]

        print "connected to server and registered"
        logging.info("received welcome")
            
        # Thread setup
        self.threadRecv = threading.Thread(target=Client.receive, args=(self,))
        self.threadSend = threading.Thread(target=Client.send, args=(self,))
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
        
        logging.info("terminating client")

client = Client()
client.main(sys.argv[1:])

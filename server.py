""" Assignment 1 - CSCI 353 Spring 2017
    Isabella Benavente
    Using Python 2.7.12 
    SERVER Module 
    USAGE: $ python server.py -p 7021 -l serverlog.txt
"""
#!/usr/bin/python2 

import socket
import sys, time
import getopt
import logging
import threading

IP = "127.0.0.1"

class Server():   

    port = ''
    logfile = ''
    client = ''

    def __init__(self):        
        # Init socket, parameters are to specify internet and UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.shouldExit = False
        self.serverip = ''
        self.serverport = ''
        self.overlayport = ''
        self.lookupDict = {}

    # Function declarations
    def lookupSender(self, clientip, clientport):
        for clientname, clientdata in self.lookupDict.items():
            if clientdata[0] == clientip and clientdata[1] == clientport:
                return clientname
        return "unknown"

    def lookupRecipient(self, clientname):
        if self.lookupDict.has_key(clientname):
            return self.lookupDict[clientname]          
        return "unknown", "unknown"

    def listen(self):
        while self.shouldExit == False:
            self.connection, self.conn_addr =  self.overlaysock.accept()

    def accept(self):        
        while self.shouldExit == False:
            data = self.connection.recv(1024)
            print "Data received: " + data


    def handleClientMessages(self):
        # Constantly wait to receive messages
        while self.shouldExit == False:
            data, addr = self.sock.recvfrom(1024) # buffer size in bytes

            # Received register, send welcome
            dataparts = data.split(' ')
            if dataparts[0] == 'register':
                client = str(dataparts[1])
                print client + " registered from host " + addr[0] + " port " + str(addr[1])
                logging.info("received register " + client + " from host " + addr[0] + " port " + str(addr[1]))
                logging.info("client connection from host " + addr[0] + " port " + str(addr[1]))
                self.sock.sendto("welcome " + client, (addr[0], addr[1]))            
                self.lookupDict[client] = (addr[0], addr[1])
            # Received message, send to intended client
            else:
                recipient = dataparts[1]
                recvIP, recvPort = self.lookupRecipient(recipient)
                sender = self.lookupSender(addr[0], addr[1])
                message = data[data.find(dataparts[3]):]
                logging.info("sendto " + recipient + " from " + sender + " " + message) 
                #print "Message received: ", data
                #print recipient + " " + recvIP + " " + str(recvPort) + " " + sender
                
                if recvIP != "unknown" and recvPort != "unknown": 
                    logging.info(recipient + " registered with server")
                    logging.info("recvfrom " + sender + " to " + recipient + " " + message)
                    message = "recvfrom " + sender + " " + message
                    self.sock.sendto(message, (recvIP, recvPort))
                else:                
                    logging.info(recipient + " not registered with server") 

    def main(self, argv):
        """Main function in SERVER"""

        argv = sys.argv[1:]

        # Handle command line arguments
        try:
            opts, args = getopt.getopt(argv, "hs:t:o:p:l:", ["serverip=", "serverport=", "overlayport=", "portno=", "logfile="])
        except getopt.GetoptError:
            print('test.py -i <portno> -o <logfile>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print('test.py -i <portno> -o <logfile>')
                sys.exit()
            elif opt in ("-s", "--serverip"):
                self.serverip = arg
            elif opt in ("-t", "--serverport"):
                self.serverport = arg
            elif opt in ("-o", "--overlayport"):
                self.overlayport = arg
            elif opt in ("-p", "--portno"):
                port = arg
            elif opt in ("-l", "--logfile"):
                logfile = arg
        
        logging.basicConfig(filename=logfile, level=logging.DEBUG)
        logging.info("server started on " + IP + " at port " + port)

        # Parameters are to specify internet and UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, int(port)))

        if self.serverip != '' and self.serverport != '':
            # TCP Socket for Server-Server connections
            self.servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servsock.connect((self.serverip, int(self.serverport)))
        elif self.overlayport != '':
            self.overlaysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.overlaysock.bind((IP, int(self.overlayport)))
            self.threadListen = threading.Thread(target=Server.listen, args=(self,))
            self.threadListen.setDaemon(True)
            self.threadListen.start()  

        # Thread setup
        self.threadRecv = threading.Thread(target=Server.handleClientMessages, args=(self,))
        self.threadRecv.setDaemon(True)
        self.threadRecv.start()     

        # Keep main thread alive
        try:
            while self.shouldExit == False:
                time.sleep(.1)
        except KeyboardInterrupt:
            self.shouldExit = True
            print "exit"         

        logging.info("terminating server...")

server = Server()
server.main(sys.argv[1:])

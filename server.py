""" Assignment 1 - CSCI 353 Spring 2017
    Isabella Benavente
    Using Python 2.7.12 
    SERVER Module 
    USAGE: $ python server.py -p 7021 -l serverlog.txt
"""
#!/usr/bin/python2 

import socket
import sys
import getopt
import logging
import threading

IP = "127.0.0.1"

def main(argv):
    """Main function in SERVER"""

    port = ''
    logfile = ''
    client = ''
    lookupDict = {}

    def lookupSender(clientip, clientport):
        for clientname, clientdata in lookupDict.items():
            if clientdata[0] == clientip and clientdata[1] == clientport:
                return clientname
        return "unknown"

    def lookupRecipient(clientname):
        if lookupDict.has_key(clientname):
            return lookupDict[clientname]   
        
        logging.info(clientname + " not registered with server") 
        return "unknown", "unknown"

    try:
        opts, args = getopt.getopt(argv, "hp:l:", ["portno=", "logfile="])
    except getopt.GetoptError:
        print('test.py -i <portno> -o <logfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <portno> -o <logfile>')
            sys.exit()
        elif opt in ("-p", "--portno"):
            port = arg
        elif opt in ("-l", "--logfile"):
            logfile = arg

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logging.info("server started on " + IP + " at port " + port)
    logging.info("client connection from host " + IP + " port " + port)
    logging.info("received register " + " from host " + " port")

    # Parameters are to specify internet and UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, int(port)))

    # Constantly wait to receive messages
    while True:
        data, addr = sock.recvfrom(1024) # buffer size in bytes

        # Received register, send welcome
        dataparts = data.split(' ')
        if dataparts[0] == 'register':
            client = str(dataparts[1])
            print client + " registered from host " + addr[0] + " port " + str(addr[1])
            sock.sendto("welcome " + client, (addr[0], addr[1]))            
            lookupDict[client] = (addr[0], addr[1])
        # Received message, send to intended client
        else:
            recipient = dataparts[1]
            recvIP, recvPort = lookupRecipient(recipient)
            sender = lookupSender(addr[0], addr[1])
            message = data[data.find("message"):]
            print "Message received: ", data

            print recipient + " " + recvIP + " " + str(recvPort) + " " + sender
            if recvIP != "unknown" and recvPort != "unknown":            
                logging.info("recvfrom " + sender + " to " + recipient + " " + message)
                logging.info("sendto " + recipient + " from " + sender + " " + message)
                sock.sendto(data, (recvIP, recvPort))

    logging.info("terminating server")

main(sys.argv[1:]) # argument gets everything after script name

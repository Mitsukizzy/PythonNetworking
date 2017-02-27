""" Assignment 1 - CSCI 353 Spring 2017
    Isabella Benavente
    Using Python 2.7.12 
    CLIENT Module 
"""
# Clients communicate using UDP

import socket
import sys
import getopt
import logging

def main(argv):
    """Main function in CLIENT"""

    serverip = ''
    port = ''
    logfile = ''
    clientname = ''
    message = ''

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

    # Parameters are to specify internet and UDP
    port = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(("register " + clientname).encode(), (serverip, port))
    logging.info("sending register message " + clientname)

    data = sock.recvfrom(1024) # buffer size in bytes
    welcomedata = data[0].split(' ')
    if welcomedata[0] == 'welcome':
        client1 = welcomedata[1]
        print "client1 is ", client1

    print "connected to server and registered"
    logging.info("received welcome")

    print "waiting for messages.."

    while True:
        message = raw_input("Enter message: ")

        if message == "exit":
            print "exit"
            logging.info("terminating client")
            sys.exit()

        message = "sendto " + message
        sock.sendto(message, (serverip, port))

main(sys.argv[1:]) # argument gets everything after script name

""" Assignment 1 - CSCI 353 Spring 2017
    Isabella Benavente
    Using Python 2.7.12 
    SERVER Module 
    USAGE: $ python server.py -p 7021 -l serverlog.txt
"""

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
    client1 = ''
    
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
        registerdata = data.split(' ')
        if registerdata[0] == 'register':
            client1 = registerdata[1]
            print "DEBUG NEW CLIENT - addr0: ", addr[0], "addr1: ", addr[1]
            sock.sendto("welcome " + client1, (addr[0], addr[1]))
        else:
            print "Message received: ", data
            print "From addr: ", addr


    logging.info("terminating server")

main(sys.argv[1:]) # argument gets everything after script name

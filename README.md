# ChatSystem
A chat system that supports multiple clients and servers. 
Built using Python 2.7.12


Example Server usage using 2 servers and 3 clients:
SERVER 1
$ python server.py -o 7030 -p 7021 -l server1log.txt

SERVER 2
$ python server.py -s 127.0.0.1 -t 7030 -p 7022 -l server2log.txt

CLIENT 1 (connects to SERVER 1)
$ python client.py -s 127.0.0.1 -p 7021 -l client1log.txt -n Alice

CLIENT 2 (connects to SERVER 1)
$ python client.py -s 127.0.0.1 -p 7021 -l client2log.txt -n Bob

CLIENT 3 (connects to SERVER 2)
$ python client.py -s 127.0.0.1 -p 7022 -l client3log.txt -n Carl
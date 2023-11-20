#!/usr/bin/env python3

from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()
from os.path import exists

import grpc

import csci4220_hw3_pb2
import csci4220_hw3_pb2_grpc

def run():
    if len(sys.argv) != 3:
        print("Error, correct usage is {} [control port] [base station file]".format(sys.argv[0]))
        sys.exit(-1)
        
    # Read base station file
    station_file = open(sys.argv[2], "r")
    if(station_file == FileNotFoundError)
        print("Error, base station file " + sys.argv[2] + " does not exist\n")
        sys.exit(-1)
        
    station_file.close()

    if not exists:
        print("Error, provided base station file " + sys.argv[2] + " does not exist\n")
        sys.exit(-1)

    local_id = int(sys.argv[1])
    my_port = str(int(sys.argv[2])) # add_insecure_port() will want a string
    k = int(sys.argv[3])
    my_hostname = socket.gethostname() # Gets my host name
    my_address = socket.gethostbyname(my_hostname) # Gets my IP address from my hostname

    #''' Use the following code to convert a hostname to an IP and start a channel
	#Note that every stub needs a channel attached to it
	#When you are done with a channel you should call .close() on the channel.
	#Submitty may kill your program if you have too many file descriptors open
	#at the same time. '''
	
	#remote_addr = socket.gethostbyname(remote_addr_string)
	#remote_port = int(remote_port_string)
	#channel = grpc.insecure_channel(remote_addr + ':' + str(remote_port))

if __name__ == '__main__':
	run()
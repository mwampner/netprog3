#!/usr/bin/env python3

from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()
from os.path import exists
import select

import grpc

# import csci4220_hw3_pb2
# import csci4220_hw3_pb2_grpc

def run():
    if len(sys.argv) != 3:
        print("Error, correct usage is {} [control port] [base station file]".format(sys.argv[0]))
        sys.exit(-1)
        
    # Read base station file
    station_file = open(sys.argv[2], "r")
    if station_file == FileNotFoundError:
        print("Error, base station file " + sys.argv[2] + " does not exist\n")
        sys.exit(-1)

    # read in base file information
    # key : BaseID
    # val : [0] - XPOS
    #       [1] - YPOS
    #       [2] - NUMLINKS
    #       [3:] - List of Links
    base = {}
    for line in station_file:
        # print(line)
        count = 0
        for i in line.split(' '):
            if count == 0:
                base[i] = []
                key = i
            else:
                base[key].append(i.strip())
            count += 1
    # print(base)
    station_file.close()

    if not exists:
        print("Error, provided base station file " + sys.argv[2] + " does not exist\n")
        sys.exit(-1)

    local_id = int(sys.argv[1])
    my_port = str(int(sys.argv[1])) # add_insecure_port() will want a string
    k = int(sys.argv[1])
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

    # create socket
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind(('localhost', local_id)) # bind socket to port
    control_socket.listen(5) # listen for clients

    # listen
    print("listnening for connections")
    inputs = [sys.stdin, control_socket]

    while True:
        readable, _, _ = select.select(inputs, [], [])
        for sock in readable:
            if sock == control_socket:
                # Accept incoming connections
                client_socket, client_address = control_socket.accept()
                print("Connected to:", client_address)

                # Test connection
                message = ('Connected - walshm7\n')
                client_socket.send(message.encode())

                # Close the client socket
                client_socket.close()
            elif sock == sys.stdin:
                # Read from standard input
                try:
                    command = input().strip()  # Read from stdin

                    # commands
                    if command == "QUIT":
                        print("Server shutting down...")
                        # Clean up and terminate
                        control_socket.close()
                        sys.exit(0)
                    elif command.startswith("WHERE"): # confused on where this comes from
                        # Handle WHERE command
                        # Extract NodeID and process accordingly
                        pass  # Implement handling WHERE command
                    elif command.startswith("UPDATEPOSITION"): # confused on where this comes from
                        # Handle UPDATEPOSITION command
                        # Extract necessary information and respond
                        pass  # Implement handling UPDATEPOSITION command
                    else:
                        print("Invalid command. Please enter a valid command.")
                except KeyboardInterrupt:
                    print("\nServer interrupted by user. Shutting down...")
                    control_socket.close()
                    sys.exit(0)
                except Exception as e:
                    print("Error:", e)



if __name__ == '__main__':
	run()
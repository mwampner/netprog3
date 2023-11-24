#!/usr/bin/env python3

from concurrent import futures
import sys  # For sys.argv, sys.exit()
import socket  # for gethostbyname()
from os.path import exists
import select
import math

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


    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind(('localhost', local_id)) # bind socket to port
    control_socket.listen(5) # listen for clients

    # listen
    print("listnening for connections")
    inputs = [sys.stdin, control_socket]

    while True:
        readable, _, _ = select.select(inputs, [], [])
        for sock in readable:
            
            # if sock == control_socket:
            #     # Accept incoming connections
            #     client_socket, client_address = control_socket.accept()
            #     print("Connected to:", client_address)
            #
            #     # Test connection
            #     message = ('Connected - walshm7\n')
            #     client_socket.send(message.encode())
            #
            #     # Close the client socket
            #     # client_socket.close()
            if sock == sys.stdin:
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
                        try:
                            parts = command.split()
                            node_id = parts[1]
                            if node_id in base:
                                x_pos = base[node_id][0]
                                y_pos = base[node_id][1]

                                there_message = f"THERE {node_id} {x_pos} {y_pos}\n"

                                client_socket.send(there_message.encode())
                                print(there_message)
                            else:
                                print("Node ID not found.")
                        except Exception as e:
                            print("Error handling WHERE command:", e)
                    elif command.startswith("UPDATEPOSITION"): # confused on where this comes from
                        try:
                            parts = command.split()
                            sensor_id = parts[1]
                            x_pos = parts[2]
                            y_pos = parts[3]

                            reachable_list = []
                            for node_id, pos_info in base.items():
                                reachable_list.append(f"{node_id} {pos_info[0]} {pos_info[1]}")

                            # Construct REACHABLE message
                            num_reachable = len(reachable_list)
                            reachable_message = f"REACHABLE {num_reachable} {' '.join(reachable_list)}\n"

                            print(reachable_message)
                            client_socket.send(reachable_message.encode())

                        except Exception as e:
                            print("Error handling UPDATEPOSITION command:", e)
                    else:
                        print("Invalid command. Please enter a valid command.")
                except KeyboardInterrupt:
                    print("\nServer interrupted by user. Shutting down...")
                    control_socket.close()
                    sys.exit(0)
                except Exception as e:
                    print("Error:", e)
            elif sock == control_socket: # check for new connection
                client_socket, client_address = control_socket.accept()
                inputs.append(client_socket)
                print("Connected to:", client_address)
                command = client_socket.recv(1024).decode()
                try:
                    parts = command.split()
                    sensor_id = parts[1]
                    sns_range = int(parts[2])
                    x_pos = int(parts[3])
                    y_pos = int(parts[4])
                    base[sensor_id] = [x_pos, y_pos]
                    reachable_list = []
                    
                    for node_id, pos_info in base.items():
                        if(math.dist([x_pos, y_pos], [int(pos_info[0]), int(pos_info[1])]) <= sns_range):
                            reachable_list.append(node_id)
                    print("TEST")
                    base[sensor_id].append(len(reachable_list))
                    for n in reachable_list:
                        base[sensor_id].append(n)
                    # Construct REACHABLE message
                    num_reachable = len(reachable_list)
                    reachable_message = f"REACHABLE {num_reachable} {' '.join(reachable_list)}\n"

                    print(reachable_message)
                    client_socket.send(reachable_message.encode())

                except Exception as e:
                    print("Error handling UPDATEPOSITION command:", e)
            else: # receive from existing client
                client_socket = sock
                command = client_socket.recv(1024).decode()
                if command.startswith("WHERE"): # confused on where this comes from
                    try:
                        parts = command.split()
                        node_id = parts[1]
                        if node_id in base:
                            x_pos = base[node_id][0]
                            y_pos = base[node_id][1]

                            there_message = f"THERE {node_id} {x_pos} {y_pos}\n"

                            client_socket.send(there_message.encode())
                            print(there_message)
                        else:
                            print("Node ID not found.")
                    except Exception as e:
                        print("Error handling WHERE command:", e)




if __name__ == '__main__':
	run()
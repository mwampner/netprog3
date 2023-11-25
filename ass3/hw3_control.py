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


def lists_reachable(x, y, range, dic, id):

    try:
        reachable = []
        for b, val in dic.items():
            dist = math.dist([int(x), int(y)], [int(val[0]), int(val[1])])
            if dist <= int(range) and b != id:
                reachable.append(b)
            # print(reachable,b, id)

        return reachable
    except Exception as e:
        print("Error in lists_reachable:", e)


def closest(base, curr, dest, hops, base_stations):
    # print("in closest")
    reachable = [0,float('inf')]
    x = base[dest][0]
    y = base[dest][1]
    # print(x,y)
    cansee = base[curr][3]
    # print(cansee)
    # print(hops)
    # print(base.keys())
    for b, val in base.items():
        if b in cansee or (curr in base_stations and b not in base_stations):
            # print(int(val[0]), int(val[1]))
            dist = 0
            try:
                dist = math.dist([int(x), int(y)], [int(val[0]), int(val[1])])
            except Exception as e:
                print("Error in dist:", e)
            if b not in hops and b in base_stations: # base_station
                if dist < reachable[1]:
                    #print(curr + " ---> " + b + " (" + str(dist) + ")")
                    reachable[0] = b
                    reachable[1] = dist
            else: # clients
                #print(curr + " ---> " + b + " (" + str(dist) + ")")
                #print(hops)
                #print(base[b][3])
                if b not in hops and curr in base[b][3]:
                    if dist < reachable[1]:
                        reachable[0] = b
                        reachable[1] = dist

    # reachable = sorted(reachable.items(), key=lambda x: x[1])
    #     # reachable = dict(reachable)
    return reachable[0]

def check_lists(l1, l2):
    for i in l1:
        if i not in l2:
            # print(i)
            return False
    return True


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
    base_stations = []
    for line in station_file:
        # print(line)
        count = 0
        lt = []
        key = ''
        for i in line.split(' '):
            if count == 0:
                base[i] = []
                key = i
            elif count > 3:
                lt.append(i.strip())
            else:
                base[key].append(i.strip())
            count += 1
        base[key].append(lt)
        base_stations.append(key)

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
    # print("listnening for connections")
    inputs = [sys.stdin, control_socket]
    clients = {}

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
                    clients[sensor_id] = client_socket
                    
                    for node_id, pos_info in base.items():
                        if(math.dist([x_pos, y_pos], [int(pos_info[0]), int(pos_info[1])]) <= sns_range and node_id != sensor_id):
                            reachable_list.append(node_id)
                    # print("TEST")
                    base[sensor_id].append(len(reachable_list))
                    base[sensor_id].append(reachable_list)
                    # Construct REACHABLE message
                    num_reachable = len(reachable_list)
                    reachable_message = f"REACHABLE {num_reachable} {' '.join(reachable_list)}\n"

                    # print(reachable_message)
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
                            # print(there_message)
                        else:
                            print("Node ID not found.")
                    except Exception as e:
                        print("Error handling WHERE command:", e)
                elif command.startswith("UPDATEPOSITION"):
                    try:
                        parts = command.split()
                        range = parts[2]
                        sensor_id = parts[1]
                        x_pos = parts[3]
                        y_pos = parts[4]

                        reachable = lists_reachable(x_pos,y_pos, range, base, sensor_id)
                        # for node_id, pos_info in base.items():
                        #     reachable_list.append(f"{node_id} {pos_info[0]} {pos_info[1]}")

                        # Construct REACHABLE message
                        num_reachable = len(reachable)
                        base[sensor_id] = [x_pos, y_pos, num_reachable, reachable]

                        reachable_message = f"REACHABLE {num_reachable} {' '.join(reachable)}\n"

                        # print(reachable_message)
                        client_socket.send(reachable_message.encode())
                    except Exception as e:
                        print("Error handling UPDATEPOSITION command:", e)
                elif command.startswith("DATAMESSAGE"):
                    try:
                        # print(command)
                        hop = command[command.find('[') + 1: command.find(']')].split()
                        parts = command.split()
                        #  "DATAMESSAGE " + sensor_id + " " + next_sns + " " + msg[1] + " 1 ['" + sensor_id + "']"
                        sensor_id = parts[1]
                        next_sns = parts[2]
                        dest = parts[3]


                        # hop = parts[5][2:-2].split()  # parse away the brackets
                        # print(hop, "hop")

                        # send to sensor

                        while 1:
                            if next_sns not in base_stations:
                                # print("here")
                                next_sock = clients[next_sns]
                                hop_str = ""
                                for i in hop:
                                    hop_str = hop_str + ' ' + i
                                data_msg = "DATAMESSAGE " + sensor_id + " " + next_sns + " " + dest + " [ " + hop_str + "]"
                                next_sock.send(data_msg.encode())

                                break
                            else:  # send to base_station
                                # print(base[next_sns][3])
                                # print(hop)
                                if next_sns == dest:
                                    print(next_sns+": Message from "+sensor_id+" to "+dest+" successfully received")
                                    break
                                elif dest in base[next_sns][3]: # base stations can reach each other
                                    hop.append(next_sns)
                                    print(next_sns+": Message from "+ sensor_id+" to "+dest+" being forwarded through "+next_sns)
                                    next_sns = dest
                                elif check_lists(base[next_sns][3], hop):
                                    # print("no")
                                    print(next_sns+": Message from "+sensor_id+" to "+dest+" could not be delivered")
                                    break
                                else:
                                    nxt = closest(base,next_sns, dest, hop, base_stations)
                                    # print(nxt, "nxt")
                                    if nxt in base_stations:
                                        print(next_sns+": Message from "+ sensor_id+" to "+dest+" being forwarded through "+next_sns)
                                        hop.append(next_sns)
                                        next_sns = nxt


                                    else:
                                        print(next_sns + ": Message from " + sensor_id + " to " + dest + " being forwarded through " + next_sns)
                                        next_sock = clients[nxt]
                                        hop_str = ""
                                        space = "', '"
                                        hop_str = space.join(hop)
                                        #for i in hop:
                                        #    hop_str = hop_str + ' ' + i
                                        data_msg = "DATAMESSAGE " + sensor_id + " " + nxt + " " + dest+ " ['" + hop_str + "']"
                                        next_sock.send(data_msg.encode())
                                        break
                        client_socket.send("message sent".encode())


                    except Exception as e:
                        print("Error handling DATAMESSAGE command:", e)
                elif command == "": # Client disconnect
                    for c in clients:
                        if clients[c] == client_socket:
                            print("DISCONNECT " + c)
                            base.pop(c)
                            inputs.remove(client_socket)








if __name__ == '__main__':
	run()
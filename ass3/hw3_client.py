import socket
import sys
import math

def send_message_to_control(message):
    control_address = (sys.argv[1], int(sys.argv[2]))  # Control server address and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as control_socket:
        control_socket.connect(control_address)
        control_socket.sendall(message.encode())
        response = control_socket.recv(1024)  # buffer size?
        return response.decode()


def send_where_message(sensor_id):
    # Format the WHERE message for the control server
    message = f"WHERE {sensor_id}\n"
    response = send_message_to_control(message)

    # print THERE message
    print(response.decode())

    return response


def send_update_position_message(sensor_id, x_position, y_position):
    # Format the UPDATEPOSITION message for the control server
    message = f"UPDATEPOSITION {sensor_id} {x_position} {y_position}\n"
    response = send_message_to_control(message)
    
    # print REACHABLE message
    res_str = sensor_id + ": After reading REACHABLE message, I can see: "
    response = response.split()
    reachable = []
    for sns in response:
        if sns != "REACHABLE" and not sns.isnumeric():
            # add to reachable list
            reachable.append(sns)
    # print string
    res_str = res_str + reachable
    print(res_str + "\n")
    return reachable


def send_data_message(msg):
    # Format the DATA message for the control server
    response = send_message_to_control(msg)
    return response

def find_next_loc(dest, reachable, hop_list):
    # get position of destination
    dest_pos = send_where_message(dest).split()
    # dictionary to find distances and sort
    next_ops = {}
    for s in reachable:
        # get dest for reachables
        loc = send_where_message(s)
        # get distance from dest
        dist = math.dist([loc[1], loc[2]], [dest_pos[1], dest_pos[2]])
        next_ops[s] = dist
    # sort dict
    next_ops = sorted(next_ops.items(), key=lambda x:x[1])
    next_ops = dict(next_ops)
    
    # check hop_list
    for s in next_ops:
        found = False
        for h in hop_list:
            if s == h:
                found = True
        if not found:
            return s
    # impossible to send
    return -1

def data_message_handling(res, x, y):
    org_sns = res[1]
    dest = res[3]
    sns = res[2]
    # iterate hop data
    hop_num = res[4] + 1
    hop_list = res[5]
    hop_list.append(sns)
    # get reachable list for sensor
    reachable = send_update_position_message(sensor_id, x, y)
    next_sns = ""
    # search for dest
    for s in reachable:
        if s == dest:
            next = dest
    if next == dest:
        # build data message
        data_msg = "DATAMESSAGE " + org_sns + " " + next_sns + " " + dest + " " + hop_num + " " + hop_list
        send_data_message(data_msg)
    else:
        next_sns = find_next_loc(dest, reachable, hop_list)
        if next_sns == -1:
            print(sns + ": Message from " + org_sns + " to " + dest + " could not be delivered")
            return -1
        else: # possible to send message
            data_msg = "DATAMESSAGE " + org_sns + " " + next_sns + " " + dest + " " + hop_num + " " + hop_list
            send_data_message(data_msg)
        
if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(
            "Usage: python3 -u hw3_client.py [control address] [control port] [SensorID] [SensorRange] [InitialXPosition] [InitialYPosition]")
        sys.exit(-1)

    control_address = sys.argv[1]
    control_port = int(sys.argv[2])
    sensor_id = sys.argv[3]
    sensor_range = int(sys.argv[4])
    x_position = int(sys.argv[5])
    y_position = int(sys.argv[6])
    reachable_list = []

    # find hostname ip
    if not control_address[0].isnumeric():
        control_address = socket.gethostbyname(control_address)

    # connect client to control
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((control_address, control_port))                # This server to a port

    # test
    #response = send_where_message(sensor_id)
    #print("Response from control server:", response)
    # initial connection message
    response = send_update_position_message(sensor_id, x_position, y_position)
    print("Response from control server:", response)

    # Additional sensor logic...()

    # Set up select
    msg_sources = [s, sys.stdin]

    while 1:
        # start select
        input_detect = [msg_sources, [], []]

        for source in input_detect:
            # Check for message input
            if source == sys.stdin:
            # Check for control message
                msg = sys.stdin.readline()
                msg = msg.split()
            
            # Handle messages
            # QUIT
                if(msg[0] == "QUIT"):
                    s.close()
                    exit()
            # MOVE
                elif(msg[1] == "MOVE"):
                    # check for valid inputs
                    if len(msg) != 3:
                        print("Invalid MOVE command\n")
                    else: # valid command
                        # change position
                        x_position = msg[1]
                        y_position = msg[2]
                        # notify control
                        reachable_list = send_update_position_message(sensor_id, x_position, y_position)
            # SENDDATA
                elif(msg[0] == "SENDDATA"):
                    if len(msg) != 2:
                        print("Invalid SENDDATA command arguments\n")
                    else: # valid command
                        # update position message
                        response = send_update_position_message(sensor_id, x_position, y_position)
                        next_sns = ""
                        # check for directy
                        for s in response:
                            if s == msg[1]:
                                next_sns = s
                        if next_sns == s:
                            print(sensor_id + ": Sent a new message bound for " + msg[1])
                            # build data message
                            data_msg = "DATAMESSAGE " + sensor_id + " " + next_sns + " " + msg[1] 
                            send_data_message(data_msg)
                        else:
                            # find where to send msg
                            next_sns = find_next_loc(msg[1], response, [])
                            # send data message to control
                            data_msg = "DATAMESSAGE " + sensor_id + " " + next_sns + " " + msg[1] + " 1 ['" + sensor_id + "']"
                            send_data_message(data_msg)
            # WHERE
                elif(msg[0] == "WHERE"):
                    # invalid command structure
                    if len(msg) != 2:
                        print("Invalid WHERE commad arguments\n")
                    else: # valid command
                        res = send_where_message(msg[1])
            # INVALID COMMAND
                else:
                    print("Invalid Client command input\n")
            else: # accept control message
                response = s.recv(1024).decode()
                response = response.split()
                # received data message
                if response[0] == "DATAMESSAGE":
                    if(len(response) != 6):
                        print("Invalid DATAMESSAGE received exiting...")
                        s.close()
                        exit(-1)
                    else: 
                        # received message destination
                        if response[3] == sensor_id:
                            print(sensor_id + ": Message from " + response[1] + " to " + sensor_id + " successfully received\n")
                        else: # pass on message to next id
                            data_message_handling(response, x_position, y_position, response[5])
                else: # received invalid message
                    print("Invalid message received from control: exiting...\n")
                    s.close()
                    exit(-1)
                    
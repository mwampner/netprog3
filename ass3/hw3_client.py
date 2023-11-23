import socket
import sys


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
    print(response)

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


def send_data_message(destination_id, next_id, message):
    # Format the DATA message for the control server
    data_message = f"DATAMESSAGE {destination_id} {next_id} {message}\n"
    response = send_message_to_control(data_message)
    return response

def send_initial_data_message(destination_id, message):
    # Format the DATA message for the control server
    data_message = f"DATAMESSAGE {destination_id} {next_id} {message}\n"
    response = send_message_to_control(data_message)
    return response


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
    s.bind((control_address, control_port))                # This server to a port

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
                        # print client message
                        print(sensor_id + ": Sent a new message bound for " + msg[1])
                        # update position message
                        response = send_update_position_message(sensor_id, x_position, y_position)
                        # send data message to control
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
                else: # received invalid message
                    print("Invalid message received from control: exiting...\n")
                    s.close()
                    exit(-1)
                    
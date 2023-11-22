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
    return response


def send_update_position_message(sensor_id, x_position, y_position):
    # Format the UPDATEPOSITION message for the control server
    message = f"UPDATEPOSITION {sensor_id} {x_position} {y_position}\n"
    response = send_message_to_control(message)
    return response


def send_data_message(destination_id, next_id, message):
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
    initial_x_position = int(sys.argv[5])
    initial_y_position = int(sys.argv[6])

    # test
    response = send_where_message(sensor_id)
    print("Response from control server:", response)

    response = send_update_position_message(sensor_id, initial_x_position, initial_y_position)
    print("Response from control server:", response)

    # Additional sensor logic...()
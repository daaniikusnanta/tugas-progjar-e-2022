import socket
import logging
import json
import ssl
from time import sleep

alldata = dict()

f = open("../player_data.txt", "r")
for line in f :
    data = line.split(",")
    player_data = {
        "nomor": int(data[0]),
        "nama": data[1].strip(),
        "posisi": data[2].strip()
    }
    alldata[data[0]] = player_data

logging.basicConfig(level=logging.INFO)

def version():
    return "version 0.0.1"

def process_request(request_string):
    cstring = request_string.split(" ")
    request_result = None

    try:
        command = cstring[0].strip()
        if (command == 'getplayerdata'):
            player_number = cstring[1].strip()

            try:
                request_result = alldata[player_number]
            except:
                request_result = None

        elif (command == 'version'):
            request_result = version()

    except:
        request_result = None

    sleep(0.1)
    return request_result

def serialize(a):
    serialized =  json.dumps(a)
    logging.info("Serialized data: " + serialized)
    return serialized

def run_server(server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.info(f"Starting up on {server_address}")
    sock.bind(server_address)
    sock.listen(1000)

    while True:
        logging.info("Waiting for a connection...")
        connection, client_address = sock.accept()

        is_request_done=False
        data_received=""

        while True:
            data = connection.recv(32)
            logging.info(f"Received {data}")
            
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    is_request_done=True

                if (is_request_done==True):
                    result = process_request(data_received)
                    logging.info(f"Result: {result}")

                    result = serialize(result)
                    result += "\r\n\r\n"
                    connection.sendall(result.encode())
                    is_request_done = False
                    data_received = ""
                    break

            else:
                logging.warning(f"No more data from {client_address}")
                break

if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 13000))

    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt (Control-C): Program stopped")
        exit(0)

    finally:
        logging.warning("Finished")

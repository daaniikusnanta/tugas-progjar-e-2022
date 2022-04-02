import socket
import logging
import json
from time import sleep
import threading
import ssl
import os

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

def serialize(data):
    serialized =  json.dumps(data)
    return serialized

def process_request(request_string):
    cstring = request_string.split(" ")
    request_result = None

    try:
        command = cstring[0].strip()
        if (command == 'getplayerdata'):
            logging.info("getdata")
            nomorpemain = cstring[1].strip()

            try:
                logging.info(f"data {nomorpemain} ketemu")
                request_result = alldata[nomorpemain]

            except:
                request_result = None
        
        elif (command == 'version'):
            request_result = version()

    except:
        request_result = None

    sleep(0.1)
    return request_result

def handler(connection, client_address, socket_context):
    is_request_done=False
    data_received=""

    try:
        connection = socket_context.wrap_socket(connection, server_side=True)
        while True:
            data = connection.recv(32)
            logging.warning(f"Received {data}.")

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
    
    except ssl.SSLError as error_ssl:
        logging.warning(f"SSL error: {str(error_ssl)}")

def run_server(server_address):
    cert_location = os.getcwd() + '/certs/'
    socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    socket_context.load_cert_chain(
        certfile = cert_location + 'domain.crt',
        keyfile = cert_location + 'domain.key'
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.info(f"Starting up on {server_address}")

    sock.bind(server_address)
    sock.listen(1000)

    clients = []
    
    while True:
        logging.info("Waiting for a connection...")
        connection, client_address = sock.accept()

        client = threading.Thread(target=handler, args=(connection, client_address, socket_context))
        client.start()
        clients.append(client)

if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 14000))

    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt (Control-C): Program stopped.")
        exit(0)

    finally:
        logging.warning("Finished")

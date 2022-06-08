import random
from tabulate import tabulate
import socket
import json
import logging
import time
import threading
import ssl
import os

server_connection = ('172.16.16.101', 14000)

logging.basicConfig(level=logging.INFO)

def make_secure_socket(destination_address='localhost', port=12000):
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode=ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/certs/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.info(f"Connecting to {server_address}...")

        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock,server_hostname=destination_address)
        logging.info(secure_socket.getpeercert())

        return secure_socket

    except Exception as ee:
        logging.warning(f"Error {str(ee)}")

def deserialize(data):
    deserialized = json.loads(data)
    return deserialized

def send_command(command_str):
    server_address = server_connection[0]
    server_port = server_connection[1]
    sock = make_secure_socket(server_address, server_port)

    try:
        logging.info(f"Sending message...")
        sock.sendall(command_str.encode())

        data_received=""

        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        result = deserialize(data_received)
        return result

    except Exception as ee:
        logging.warning(f"Error during data receiving {str(ee)}")
        return False

def get_player_data(nomor=0):
    cmd = f"getplayerdata {nomor}\r\n\r\n"
    result = send_command(cmd)
    return result

def get_version():
    cmd = f"version \r\n\r\n"
    result = send_command(cmd)
    return result

def request_player_data(idx, results):

    starting_request_time = time.perf_counter()

    result = get_player_data(random.randint(1,25))

    if (result):
        latency = time.perf_counter() - starting_request_time
        print(result['nama'], result['nomor'], result['posisi'])
        results[idx] = latency

    else:
        logging.warning("Failed to get player data")
        results[idx] = -1

if __name__=='__main__':
    h = get_version()
    if (h):
        print(h)

    request_count = 100
    thread_count = [1, 5, 10, 20]

    comparation_data = []

    for threads in thread_count:
        response_count = 0
        latency_total = 0
        tasks = {}
        task_results = {}

        starting_execution_time = time.perf_counter()

        loops = request_count
        while loops > 0:
            thread_loops = threads if loops >= threads else loops

            for i in range(thread_loops):
                tasks[loops - i] = threading.Thread(target=request_player_data, args=(loops - i, task_results))
                tasks[loops - i].start()

            for i in range(thread_loops):
                tasks[loops - i].join()
                result = task_results[loops - i]
                if (result != -1):
                    response_count += 1
                    latency_total += result

            loops -= thread_loops

        execution_time = time.perf_counter() - starting_execution_time
        average_latency = latency_total / response_count

        comparation_data.append([threads, request_count, response_count, f"{execution_time * 1000:.3f} ms", f"{average_latency * 1000:.3f} ms"])

    comparation_header = ["Thread Count", "Request Count", "Response Count", "Execution Time", "Average Latency"]
    print(tabulate(comparation_data, headers=comparation_header, tablefmt="fancy_grid"))
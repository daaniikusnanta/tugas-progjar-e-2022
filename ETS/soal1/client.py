import random
from tabulate import tabulate
import socket
import json
import logging
import time
import concurrent.futures

server_address = ('localhost', 13000)

def make_socket(destination_address='localhost',port=13000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"Connecting to {server_address}...")
        sock.connect(server_address)
        return sock

    except Exception as ee:
        logging.warning(f"Error {str(ee)}")

def deserialize(s):
    logging.warning(f"Deserialize {s.strip()}")
    return json.loads(s)

def send_command(command_str):
    alamat_server = server_address[0]
    port_server = server_address[1]
    sock = make_socket(alamat_server,port_server)

    try:
        logging.warning(f"Sending message...")
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

        hasil = deserialize(data_received)
        logging.warning("Data received from server:")
        return hasil

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

def request_player_data():

    starting_request_time = time.perf_counter()

    result = get_player_data(random.randint(1,25))

    if (result):
        latency = time.perf_counter() - starting_request_time
        print(result['nama'], result['nomor'], result['posisi'])
        print(f"Latency: {latency * 1000:.2f} ms")
        return latency
    else:
        print("Failed to get player data")
        return -1

if __name__=='__main__':
    h = get_version()
    if (h):
        print(h)

    request_count = 1000
    worker_count = [1, 5, 10, 20]

    comparation_data = []

    for worker in worker_count:
        response_count = 0
        latency_total = 0
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=worker)
        tasks = {}

        starting_execution_time = time.perf_counter()
        for i in range(request_count):
            tasks[i] = executor.submit(request_player_data)

        for i in range(request_count):
            result = tasks[i].result()
            if (result != -1):
                response_count += 1
                latency_total += result

        execution_time = time.perf_counter() - starting_execution_time
        average_latency = latency_total / response_count

        comparation_data.append([worker, request_count, response_count, f"{execution_time * 1000:.3f} ms", f"{average_latency * 1000:.3f} ms"])

    comparation_header = ["Thread Count", "Request Count", "Response Count", "Execution Time", "Average Latency"]
    print(tabulate(comparation_data, headers=comparation_header, tablefmt="fancy_grid"))
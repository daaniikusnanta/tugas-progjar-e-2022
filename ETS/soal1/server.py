import sys
import socket
import logging
import json
import os
import ssl

alldata = dict()

alldata['1']=dict(nomor=1, nama="Lionel Messi", posisi="RW")
alldata['2']=dict(nomor=2, nama="Cristiano Ronaldo", posisi="ST")
alldata['3']=dict(nomor=3, nama="Robert Lewandowski", posisi="ST")
alldata['4']=dict(nomor=4, nama="Kevin de Bruyne", posisi="CAM")
alldata['5']=dict(nomor=5, nama="Casemiro", posisi="CDM")
alldata['6']=dict(nomor=6, nama="Jan Oblak", posisi="GK")
alldata['7']=dict(nomor=7, nama="Mohamed Salah", posisi="RW")
alldata['8']=dict(nomor=8, nama="Sadio Mane", posisi="ST")
alldata['9']=dict(nomor=9, nama="Virgil van Dijk", posisi="CB")
alldata['10']=dict(nomor=10, nama="Kylian Mbappe", posisi="ST")
alldata['11']=dict(nomor=11, nama="Sadio Mane", posisi="LW")
alldata['12']=dict(nomor=12, nama="Neymar Jr", posisi="LW")
alldata['13']=dict(nomor=13, nama="Harry Kane", posisi="ST")
alldata['14']=dict(nomor=14, nama="N'golo Kante", posisi="CDM")
alldata['15']=dict(nomor=15, nama="Gareth Bale", posisi="RW")
alldata['16']=dict(nomor=16, nama="Manuel Neuer", posisi="GK")
alldata['17']=dict(nomor=17, nama="Sergio Ramos", posisi="CB")
alldata['18']=dict(nomor=18, nama="Gianluigi Donnaruma", posisi="GK")
alldata['19']=dict(nomor=19, nama="Karim Benzema", posisi="ST")
alldata['20']=dict(nomor=20, nama="Joshua Kimmich", posisi="CDM")
alldata['21']=dict(nomor=21, nama="Heung Min-Son", posisi="LM")
alldata['22']=dict(nomor=22, nama="Alisson Becker", posisi="GK")
alldata['23']=dict(nomor=23, nama="Thibaut Courtouis", posisi="GK")
alldata['24']=dict(nomor=24, nama="Ederson", posisi="GK")
alldata['25']=dict(nomor=25, nama="Sadio Mane", posisi="LW")

def version():
    return "version 0.0.1"

def process_request(request_string):
    cstring = request_string.split(" ")
    request_result = None

    try:
        command = cstring[0].strip()
        if (command == 'getplayerdata'):
            logging.warning("getdata")
            nomorpemain = cstring[1].strip()

            try:
                logging.warning(f"data {nomorpemain} ketemu")
                request_result = alldata[nomorpemain]
            except:
                request_result = None

        elif (command == 'version'):
            request_result = version()

    except:
        request_result = None

    return request_result


def serialize(a):
    serialized =  json.dumps(a)
    logging.warning("Serialized data: " + serialized)
    return serialized

def run_server(server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.warning(f"Starting up on {server_address}.")
    sock.bind(server_address)
    sock.listen(1000)

    while True:
        logging.warning("Waiting for a connection...")
        connection, client_address = sock.accept()
        logging.warning(f"Incoming connection from {client_address}.")

        try:
            selesai=False
            data_received=""
            while True:
                data = connection.recv(32)
                logging.warning(f"Received {data}.")
                
                if data:
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        selesai=True

                    if (selesai==True):
                        hasil = process_request(data_received)
                        logging.warning(f"Result: {hasil}")

                        hasil = serialize(hasil)
                        hasil += "\r\n\r\n"
                        connection.sendall(hasil.encode())
                        selesai = False
                        data_received = ""
                        break

                else:
                    logging.warning(f"No more data from {client_address}.")
                    break

        except ssl.SSLError as error_ssl:
            logging.warning(f"SSL error: {str(error_ssl)}.")

if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 12000))
    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt (Control-C): Program stopped.")
        exit(0)
    finally:
        logging.warning("selesai")

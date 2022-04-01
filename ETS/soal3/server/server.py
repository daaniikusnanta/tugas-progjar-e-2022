import sys
import socket
import logging
import json
import os
import ssl
import threading

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

class ClientHandler(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        cert_location = os.getcwd() + '/certs/'
        socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        socket_context.load_cert_chain(
            certfile=cert_location + 'domain.crt',
            keyfile=cert_location + 'domain.key'
        )

        try:
            
            self.connection = socket_context.wrap_socket(self.connection, server_side=True)

            selesai=False
            data_received=""

            while True:
                data = self.connection.recv(32)
                logging.warning(f"Received {data}.")

                if data:
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        selesai=True
                    if (selesai==True):
                        hasil = self.process_request(data_received)
                        logging.warning(f"Result: {hasil}")
                        hasil = self.serialize(hasil)
                        hasil += "\r\n\r\n"
                        self.connection.sendall(hasil.encode())
                        selesai = False
                        data_received = ""
                        break

                else:
                    logging.warning(f"No more data from {self.client_address}.")
                    break

        except ssl.SSLError as error_ssl:
            logging.warning(f"SSL error: {str(error_ssl)}.")

        finally:
            self.client_socket.close()
    
    def serialize(self, data):
        serialized =  json.dumps(data)
        logging.warning("Serialized data: " + serialized)
        return serialized

    def process_request(self, request_string):
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
                request_result = self.version()

        except:
            request_result = None

        return request_result

    def version():
        return "version 0.0.1"

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        server_address = ('0.0.0.0', 14000)
        logging.warning(f"Starting up on {server_address}.")
        self.socket.bind(server_address)
        self.socket.listen(1000)
        
        while True:
            self.connection, self.client_address = self.socket.accept()
            logging.warning(f"Incoming connection from {self.client_address}.")
            
            client = ClientHandler(self.connection, self.client_address)
            client.start()
            self.clients.append(client)

if __name__=='__main__':
    try:
        server = Server()
        server.start()

    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt (Control-C): Program stopped.")
        exit(0)
    finally:
        logging.warning("selesai")

import socket
import json
import shlex
import base64
import logging

server_address=('172.16.16.101',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False
    
def remote_post(filename="",filedata=""):
    if (filedata == ""):
        try:
            logging.warning("reading file")
            with open(filename,'rb') as fp:
                filedata = base64.b64encode(fp.read()).decode('utf-8')
        except Exception as e:
            print(f"Error message: {e}")
            return False

    if " " in filename:
        filename = f'"{filename}"'

    command_str=f"POST {filename} {filedata}"
    hasil = send_command(command_str)
    return check_error(hasil, "File berhasil diupload.")

def check_error(hasil, success_message="Berhasil."):
    if (hasil['status']=='OK'):
        print(success_message)
        return False

    if (hasil['data']):
        print(f"Error message: {hasil['data']}")
    
    print("Gagal.")    
    return True

def handle_command(command):
    cmd, *params = shlex.split(command)
    cmd = cmd.lower()
    
    try:
        if cmd == "list":
            remote_list()
    
        elif cmd == "get":
            remote_get(params[0])
    
        elif cmd == "post":
            remote_post(params[0], params[1] if len(params) > 1 else "")
    
        elif cmd == "help":
            print_command_list()
            print("\n")
     
        else:
            print("Unknown command")
    
    except Exception as e:
         print(f"Error when handling command: {str(e)}") 

def print_command_list():
    print("Command list:")
    print(" list\t\t\t\t: get lists of files available on server")
    print(" get <filename>\t\t\t: download filename from server")
    print(" post <filename> [filedata]\t: upload filename to server. When filedata is not specified, filename will be uploaded")
    print(" help\t\t\t\t: show available commands")

if __name__=='__main__':
    server_address=('172.16.16.101',7777)
    
    print_command_list()
    try:
        while 1:
            print("\nEnter command (^C to exit):")
            handle_command(input())
    except KeyboardInterrupt:
        print("\nProgram exited.")

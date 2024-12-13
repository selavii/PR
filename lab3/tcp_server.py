import socket
import threading
import random
import time
import json
from threading import Lock, Condition

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5443

file_access_lock = Lock()
write_condition = Condition(file_access_lock)
active_readers = 0

data_file_path = 'shared_data.json'


def initialize_shared_file():
    with file_access_lock:
        try:
            with open(data_file_path, 'x') as file:
                json.dump({}, file)
        except FileExistsError:
            pass

initialize_shared_file()


def handle_client(client_socket, client_address):
    print(f"Connected by {client_address}")
    try:
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break

            command = request.strip().lower()

            if command == "exit":
                print(f"Client {client_address} requested to disconnect.")
                client_socket.sendall(b"Goodbye!")
                break

            elif command == "read":
                process_read_request(client_socket)

            elif command.startswith("write"):
                try:
                    message = command.split(" ", 1)[1]
                    process_write_request(client_socket, message)
                except IndexError:
                    client_socket.sendall(b"Invalid write command. Usage: write <message>\n")
            else:
                client_socket.sendall(b"Invalid command. Use 'read', 'write <message>', or 'exit'\n")
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection lost with {client_address}")
    finally:
        client_socket.close()
        print(f"Connection closed by {client_address}")

def process_read_request(client_socket):
    global active_readers

    with file_access_lock:
        while active_readers == -1:
            client_socket.sendall(b"Write operation in progress, please wait...\n")
            write_condition.wait()
        active_readers += 1

    time.sleep(random.randint(1, 7))

    with file_access_lock:
        with open(data_file_path, 'r') as file:
            file_data = json.load(file)
        client_socket.sendall(json.dumps(file_data).encode('utf-8') + b'\n')

    with file_access_lock:
        active_readers -= 1
        if active_readers == 0:
            write_condition.notify_all()


def process_write_request(client_socket, message):
    global active_readers

    with file_access_lock:
        while active_readers > 0:
            write_condition.wait()
        active_readers = -1

    time.sleep(random.randint(1, 7))

    with file_access_lock:
        with open(data_file_path, 'r+') as file:
            file_data = json.load(file)
            if 'messages' not in file_data:
                file_data['messages'] = []
            file_data['messages'].append(message)
            file.seek(0)
            json.dump(file_data, file)
            file.truncate()

    with file_access_lock:
        active_readers = 0
        write_condition.notify_all()

    client_socket.sendall(b"Write operation successful\n")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen()
        print(f"Server is running on {SERVER_HOST}:{SERVER_PORT}")
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

if __name__ == "__main__":
    start_server()

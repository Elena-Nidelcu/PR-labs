import socket
import threading
import time
import random

shared_file_path = 'shared_data.txt'
file_lock = threading.Lock()
TCP_HOST = '0.0.0.0'
TCP_PORT = 5001

def handle_client_connection(client_socket):
    with client_socket:
        command = client_socket.recv(1024).decode('utf-8').strip()
        delay = random.randint(1, 3)
        time.sleep(delay)  # Simulate network delay or processing time

        if command.startswith("write"):
            data = command.split(" ", 1)[1] if len(command.split()) > 1 else "default data"
            with file_lock:
                with open(shared_file_path, 'a') as file:
                    file.write(data + "\n")
            client_socket.sendall(b"Data written successfully.\n")

        elif command == "read":
            with file_lock:
                with open(shared_file_path, 'r') as file:
                    content = file.read()
            client_socket.sendall(content.encode('utf-8'))

        else:
            client_socket.sendall(b"Invalid command.\n")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_HOST, TCP_PORT))
    server_socket.listen(5)
    print(f"TCP server listening on {TCP_HOST}:{TCP_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    start_tcp_server()

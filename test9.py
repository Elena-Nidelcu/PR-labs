import socket
import threading
import time
import random

def test_tcp_client(command):
    host = '127.0.0.1'  # Server address
    port = 5001  # Use the same port as the TCP server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Sending command: {command}")
        s.sendall(command.encode())
        data = s.recv(1024)
        print(f"Received from server: {data.decode()}")
        time.sleep(random.randint(1, 3))  # Delay to simulate concurrent access

commands = ["write Au Revoir, Shoshanna!", "write Another brick", "read"]

threads = []
for cmd in commands:
    thread = threading.Thread(target=test_tcp_client, args=(cmd,))
    threads.append(thread)
    thread.start()
    time.sleep(0.5)

for thread in threads:
    thread.join()

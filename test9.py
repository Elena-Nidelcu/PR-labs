import socket
import threading
import random
import time


# Function for a client to send a command and print the server response
def test_tcp_client(command):
    host = '127.0.0.1'  # Server address
    port = 5001  # Must match the server port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Sending command: {command}")
        s.sendall(command.encode())
        data = s.recv(1024)
        print(f"Received from server: {data.decode()}")


# List of commands to be sent by "clients"
commands = [
    "write Yet another movie",
    "write Sometimes I feel like screaming",
    "read",
    "write Come together",
    "read"
]

# Create threads to simulate concurrent client requests
threads = []
for cmd in commands:
    # Create a new thread for each command
    thread = threading.Thread(target=test_tcp_client, args=(cmd,))
    threads.append(thread)
    thread.start()

    # Add a slight delay to stagger the requests and create randomness
    time.sleep(random.uniform(0.1, 0.5))

# Wait for all threads to complete
for thread in threads:
    thread.join()

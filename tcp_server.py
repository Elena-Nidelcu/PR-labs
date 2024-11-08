import socket
import threading

# Shared file path and synchronization tools
shared_file_path = 'shared_data.txt'
file_lock = threading.Lock()
write_lock = threading.Lock()
write_complete = threading.Condition(write_lock)
ongoing_writes = 0


# Function to handle individual client connections
def handle_client_connection(client_socket):
    global ongoing_writes
    with client_socket:
        # Receive the command from the client
        command = client_socket.recv(1024).decode('utf-8').strip()

        # Write command: Write data to the shared file
        if command.startswith("write"):
            data = command.split(" ", 1)[1] if len(command.split()) > 1 else "default data"
            # Indicate a write is happening
            with write_lock:
                ongoing_writes += 1

            # Write data to the file (critical section)
            with file_lock:
                with open(shared_file_path, 'a') as file:
                    file.write(data + "\n")

            # Decrement write counter and notify readers if no more writes are pending
            with write_lock:
                ongoing_writes -= 1
                if ongoing_writes == 0:
                    write_complete.notify_all()  # Signal readers if no more writes are happening

            # Send confirmation to the client
            client_socket.sendall(b"Data written successfully.\n")

        # Read command: Read data from the shared file
        elif command == "read":
            # Wait until all writes are complete
            with write_lock:
                while ongoing_writes > 0:
                    write_complete.wait()

            # Read data from the file (critical section)
            with file_lock:
                with open(shared_file_path, 'r') as file:
                    content = file.read()

            # Send the file content to the client
            client_socket.sendall(content.encode('utf-8'))

        # Invalid command handling
        else:
            client_socket.sendall(b"Invalid command.\n")


# Function to start the TCP server and accept connections
def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5001))
    server_socket.listen(5)
    print("TCP server listening on port 5001")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()


# Run the TCP server
if __name__ == '__main__':
    start_tcp_server()

import json
import socket
import pika
import threading
import time
import requests
from ftplib import FTP

# Configuration variables
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'products'
WEB_SERVER_URL_UPLOAD = 'http://localhost:5000/upload'
FTP_HOST = '127.0.0.1'
FTP_USER = 'testuser'
FTP_PASS = 'testpass'
FTP_FILE_NAME = 'processed_products.json'
FETCH_INTERVAL = 30  # Time interval in seconds to fetch files
LEADER_DISCOVERY_URL = 'http://localhost:5000/leader'  # Endpoint to discover the leader

# Function to upload a file to an FTP server
def upload_to_ftp(file_path):
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {file_path}', file)
        ftp.quit()
        print(f"Successfully uploaded {file_path} to FTP server.")
    except Exception as e:
        print(f"Error during FTP upload: {e}")

# Function to fetch a file from the FTP server
def fetch_file_from_ftp():
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        with open(FTP_FILE_NAME, 'wb') as file:
            ftp.retrbinary(f'RETR {FTP_FILE_NAME}', file.write)
        ftp.quit()
        print(f"Successfully fetched {FTP_FILE_NAME} from FTP server.")
        send_file_to_webserver(FTP_FILE_NAME)
    except Exception as e:
        print(f"Error fetching file from FTP: {e}")

# Function to send a file to a web server
def send_file_to_webserver(file_path):
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file)}
            response = requests.post(WEB_SERVER_URL_UPLOAD, files=files)
        if response.status_code == 200:
            print(f"Successfully sent file to webserver: {file_path}")
        else:
            print(f"Failed to send file to webserver: {response.status_code}")
    except Exception as e:
        print(f"Error sending file to webserver: {e}")

# Function to fetch the current leader from the RAFT manager
def get_leader():
    try:
        response = requests.get(LEADER_DISCOVERY_URL)
        if response.status_code == 200:
            leader_info = response.json()
            print(f"Current leader is Node {leader_info['leader_id']}.")
            return leader_info['leader_id']
        else:
            print("Failed to fetch leader info.")
    except Exception as e:
        print(f"Error fetching leader: {e}")
    return None

# Function to send data to the leader via UDP
def send_to_leader(request_data):
    leader_id = get_leader()
    if leader_id is None:
        print("No leader available. Cannot process request.")
        return

    leader_port = 10000 + leader_id
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        message = {'type': 'DatabaseRequest', 'request_data': request_data}
        try:
            sock.sendto(json.dumps(message).encode(), ('localhost', leader_port))
            data, _ = sock.recvfrom(1024)  # Await response from leader
            response = json.loads(data.decode())
            print(f"Response from leader: {response}")
        except Exception as e:
            print(f"Error communicating with leader: {e}")

# Function to process RabbitMQ messages and send them to the leader
def process_rabbitmq_message(product_data):
    print(f"Processing message: {product_data}")
    send_to_leader(product_data)

# Function to consume RabbitMQ messages
def consume_rabbitmq_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        product_data = json.loads(body)
        print(f"Received from RabbitMQ: {product_data}")

        # Process data and send it to the leader
        process_rabbitmq_message(product_data)

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Message acknowledged for {product_data}")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
    print("Waiting for RabbitMQ messages...")
    channel.start_consuming()

# Thread to periodically fetch files from FTP
def fetch_file_periodically():
    while True:
        fetch_file_from_ftp()
        time.sleep(FETCH_INTERVAL)

# Start the FTP fetch thread
fetch_thread = threading.Thread(target=fetch_file_periodically)
fetch_thread.daemon = True
fetch_thread.start()

# Start consuming RabbitMQ messages
consume_rabbitmq_messages()

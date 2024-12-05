import json
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


# FTP Upload Function
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


# Function to fetch file from FTP server
def fetch_file_from_ftp():
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)

        # Assuming the file to fetch is 'processed_products.json'
        with open(FTP_FILE_NAME, 'wb') as file:
            ftp.retrbinary(f'RETR {FTP_FILE_NAME}', file.write)
        ftp.quit()
        print(f"Successfully fetched {FTP_FILE_NAME} from FTP server.")

        # Now send the file as multipart to the webserver
        send_file_to_webserver(FTP_FILE_NAME)

    except Exception as e:
        print(f"Error fetching file from FTP: {e}")


# Function to send file to the webserver as multipart request
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


# Function to process data from RabbitMQ and upload to FTP server
def process_and_upload_to_ftp(product_data):
    # Example of map/filter/reduce logic (to be customized as per your task)
    processed_data = [product_data]  # Replace with your actual data processing logic

    # Save processed data to a file
    with open(FTP_FILE_NAME, 'w') as file:
        json.dump(processed_data, file)

    # Upload the file back to the FTP server
    upload_to_ftp(FTP_FILE_NAME)


# Function to consume RabbitMQ messages and process them
def consume_rabbitmq_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        product_data = json.loads(body)
        print(f"Received from RabbitMQ: {product_data}")

        # Process data and upload it to FTP server
        process_and_upload_to_ftp(product_data)

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Message acknowledged for {product_data}")

    # Set auto_ack to False to manually acknowledge the messages
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
    print("Waiting for RabbitMQ messages...")
    channel.start_consuming()


# Thread to fetch file from FTP server every 30 seconds
def fetch_file_periodically():
    while True:
        fetch_file_from_ftp()
        time.sleep(FETCH_INTERVAL)


# Start the thread to fetch files from FTP server periodically
fetch_thread = threading.Thread(target=fetch_file_periodically)
fetch_thread.daemon = True  # Set the thread as daemon so it exits with the main program
fetch_thread.start()

# Start consuming RabbitMQ messages
consume_rabbitmq_messages()

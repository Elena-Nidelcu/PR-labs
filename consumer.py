import json
import threading
import time
import pika
import requests
from ftplib import FTP

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'product_queue'

# FTP Configuration
FTP_HOST = '127.0.0.1'
FTP_USER = 'testuser'
FTP_PASS = 'testpass'
FTP_FILE_NAME = 'processed_products.json'

# Web server URL
WEB_SERVER_URL_UPLOAD = 'http://localhost:5000/upload'
WEB_SERVER_URL_CREATE = 'http://localhost:5000/create'

# Function to fetch a file from the FTP server and send it to the webserver
def fetch_from_ftp_and_upload():
    while True:
        try:
            # Connect to FTP server and fetch file
            ftp = FTP(FTP_HOST)
            ftp.login(user=FTP_USER, passwd=FTP_PASS)
            with open(FTP_FILE_NAME, 'wb') as file:
                ftp.retrbinary(f'RETR {FTP_FILE_NAME}', file.write)
            ftp.quit()
            print(f"Fetched {FTP_FILE_NAME} from FTP server.")

            # Upload the file to the webserver
            with open(FTP_FILE_NAME, 'rb') as file:
                response = requests.post(WEB_SERVER_URL_UPLOAD, files={'file': file})
                if response.status_code == 200:
                    print(f"Successfully uploaded {FTP_FILE_NAME} to webserver.")
                else:
                    print(f"Failed to upload file. Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during FTP fetch/upload: {e}")

        # Wait 30 seconds before fetching the file again
        time.sleep(30)

# Function to consume RabbitMQ messages and forward them to the webserver
def consume_rabbitmq_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        product_data = json.loads(body)
        print(f"Received from RabbitMQ: {product_data}")

        # Send data to the webserver's /create endpoint
        response = requests.post(WEB_SERVER_URL_CREATE, json=product_data)
        if response.status_code == 201:
            print(f"Successfully sent to webserver: {product_data}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
        else:
            print(f"Failed to send to webserver: {response.text}")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
    print("Waiting for RabbitMQ messages...")
    channel.start_consuming()

# Start FTP fetching/uploading in a separate thread
ftp_thread = threading.Thread(target=fetch_from_ftp_and_upload, daemon=True)
ftp_thread.start()

# Start RabbitMQ message consumption in the main thread
consume_rabbitmq_messages()

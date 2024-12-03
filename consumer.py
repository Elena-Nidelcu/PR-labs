import pika
import requests
import json

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'product_queue'

# Web server URL
WEB_SERVER_URL = 'http://localhost:5000/create'

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

def callback(ch, method, properties, body):
    product_data = json.loads(body)
    print(f"Received: {product_data}")

    # Send data to the webserver
    response = requests.post(WEB_SERVER_URL, json=product_data)
    if response.status_code == 201:
        print(f"Successfully sent to webserver: {product_data}")
    else:
        print(f"Failed to send to webserver: {response.text}")

# Consume messages
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("Waiting for messages...")
channel.start_consuming()

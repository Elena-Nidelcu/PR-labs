import requests
from bs4 import BeautifulSoup
import pika
import json

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'product_queue'

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

# Scraper logic
url = 'https://sportlandia.md/femei/incaltaminte-pentru-femei/ghete-femei'
response = requests.get(url)

if response.status_code == 200:
    print("Request successful!")
    html_content = response.text
else:
    print(f"Failed to retrieve content. Status code: {response.status_code}")

soup = BeautifulSoup(html_content, 'html.parser')
products = soup.find_all('div', class_='item')

for product in products:
    title_div = product.find('div', class_='title')
    name = title_div.find('a').text.strip() if title_div else "Name not found"
    price_div = product.find('div', class_='price')
    price_elements = price_div.find_all('div') if price_div else []
    price = price_elements[-1].text.strip() if price_elements else "Price not available"
    size_div = product.find('div', class_='sizes')
    size = size_div.find('span').text.strip() if size_div and size_div.find('span') else "Size not available"
    color_div = product.find('div', class_='colors')
    color = color_div.find('span')['data-product-id'] if color_div and color_div.find('span') else "Color not available"
    link = title_div.find('a')['href'] if title_div else "Link not found"

    # Remove ' LEI' and convert to a float
    try:
        price = float(price.replace(' LEI', '').replace(',', '.').strip())
    except ValueError:
        continue  # Handle invalid price

    # Publish to RabbitMQ
    product_data = {
        "name": name,
        "price": price,
        "size": size,
        "color": color,
        "link": link
    }
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(product_data))
    print(f"Published: {product_data}")

# Close RabbitMQ connection
connection.close()

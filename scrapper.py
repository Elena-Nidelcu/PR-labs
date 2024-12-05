import json

import requests
from bs4 import BeautifulSoup
from functools import reduce
import pika
from ftplib import FTP

# Conversion rate from LEI to EUR
LEI_TO_EUR_RATE = 0.05

# Define the desired price range (in EUR)
MIN_PRICE = 110.0
MAX_PRICE = 120.0

# RabbitMQ Connection Details
RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'products'


# Function to filter products based on price range
def is_in_price_range(product):
    return MIN_PRICE <= product['price'] <= MAX_PRICE


# Function to convert LEI price to EUR
def convert_to_eur(product):
    product['price'] = round(product['price'] * LEI_TO_EUR_RATE, 2)
    return product


# Function to save filtered products to a file
def save_to_file(products, filename='processed_products.json'):
    with open(filename, 'w') as file:
        json.dump(products, file, indent=4)  # Save the products as a formatted JSON file
    print(f"Filtered products saved to {filename}")


# Function to send messages to RabbitMQ
def send_to_rabbitmq(products):
    """
    Sends a list of product dictionaries to RabbitMQ in JSON format.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    for product in products:
        # Serialize the product dictionary to a JSON string
        product_json = json.dumps(product)
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=product_json)
        print(f"Sent to RabbitMQ: {product_json}")

    connection.close()

def upload_to_ftp(file_path, ftp_host='127.0.0.1', ftp_user='testuser', ftp_password='testpass'):
    """
    Uploads a file to the specified FTP server.
    """
    try:
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {file_path.split("/")[-1]}', file)
        ftp.quit()
        print(f"Uploaded {file_path} to FTP server.")
    except Exception as e:
        print(f"Error uploading file to FTP: {e}")


# Scraping logic
url = 'https://sportlandia.md/femei/incaltaminte-pentru-femei/ghete-femei'
response = requests.get(url)

if response.status_code == 200:
    print("Request successful!")
    html_content = response.text
else:
    print(f"Failed to retrieve content. Status code: {response.status_code}")

soup = BeautifulSoup(html_content, 'html.parser')
products = soup.find_all('div', class_='item')

items = []

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

    try:
        price = float(price.replace(' LEI', '').replace(',', '.').strip())  # Ensure price is a float
    except ValueError:
        continue  # Skip this product if the price is invalid

    items.append({
        "name": name,
        "price": price,  # Keep price in LEI for now
        "size": size,
        "color": color,
        "link": link
    })

# Process the items: convert prices to EUR
items_in_eur = list(map(convert_to_eur, items))

# Filter products within the price range
filtered_items = list(filter(is_in_price_range, items_in_eur))

# Save the filtered items to a file
save_to_file(filtered_items)

upload_to_ftp('processed_products.json')

# Send the filtered items to RabbitMQ
send_to_rabbitmq(filtered_items)

# Use reduce to calculate the total price of the filtered products
total_price = reduce(lambda acc, product: acc + product['price'], filtered_items, 0)
print(f"Total price of filtered products: {total_price:.2f} EUR")

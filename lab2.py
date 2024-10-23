import requests
from bs4 import BeautifulSoup
import mysql.connector

# Connect to MySQL server (without specifying the database initially)
cnx = mysql.connector.connect(
    user='root',
    password='Root123+',
    host='localhost'
)
cursor = cnx.cursor()

# Create the database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS sportlandia")
cursor.execute("USE sportlandia")

# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(10, 2),
    size INT,
    color VARCHAR(255),
    link VARCHAR(255)
);
"""
cursor.execute(create_table_query)

# URL of the website
url = 'https://sportlandia.md/femei/incaltaminte-pentru-femei/ghete-femei'

# Send GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    html_content = response.text
else:
    print(f"Failed to retrieve content. Status code: {response.status_code}")
    exit()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all product containers
products = soup.find_all('div', class_='item')

# Extract information
for product in products:
    # Get name
    title_div = product.find('div', class_='title')
    name = title_div.find('a').text.strip() if title_div else "Name not found"

    # Get price
    price_div = product.find('div', class_='price')
    price_elements = price_div.find_all('div') if price_div else []
    price = price_elements[-1].text.strip() if price_elements else "Price not available"

    # Validate and convert price into float
    try:
        price = float(price.replace(' LEI', '').replace(',', '.').strip())  # Ensure price is a float
    except ValueError:
        continue  # Skip this product if the price is invalid

    # Get size
    size_div = product.find('div', class_='sizes')
    size = size_div.find('span').text.strip() if size_div and size_div.find('span') else "Size not available"

    # Get color
    color_div = product.find('div', class_='colors')
    color = color_div.find('span')['data-product-id'] if color_div and color_div.find('span') else "Color not available"

    # Get link
    link = title_div.find('a')['href'] if title_div else "Link not found"

    # if name != "Name not found" and price != "Price not found" and price != "Price not available" and link != "Link not found":
    #     print(f"Name: {name:<52}, Price: {price:<6}, Size: {size:<4}, Color: {color:<5}, Link: {link}")

    # Insert data into the database if both name and price are available
    if name != "Name not found" and price != "Price not found" and price != "Price not available" and link != "Link not found" and color != "Color not available":
        # print(f"Inserting into database: Name: {name}, Price: {price}")
        insert_query = "INSERT INTO products (name, price, size, color, link) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (name, price, size, color, link))
        cnx.commit()

# Query to select all data from the products table
select_query = "SELECT * FROM products"
cursor.execute(select_query)

# Fetch all rows from the query result
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(f"{row[0]:<3} | {row[1]:<60} | {row[2]:<7} | {row[3]:<2} | {row[4]:<6} | {row[5]}")

# Close the database connection
cursor.close()
cnx.close()

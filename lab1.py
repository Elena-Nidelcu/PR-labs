import socket
import ssl
from bs4 import BeautifulSoup
from datetime import datetime
from functools import reduce

# Define the HTTPS URL and host details
host = 'sportlandia.md'
path = '/femei/incaltaminte-pentru-femei/ghete-femei'
port = 443  # Standard port for HTTPS

# Conversion rate from LEI to EUR
LEI_TO_EUR_RATE = 0.05  # Adjust this rate according to current exchange rates
MIN_PRICE = 30.00  # Minimum price in EUR for filtering
MAX_PRICE = 80.00  # Maximum price in EUR for filtering

# Function to check if product price is in the specified range
def is_in_price_range(product):
    return MIN_PRICE <= product['price'] <= MAX_PRICE

# Create a TCP socket and wrap it in an SSL context for HTTPS
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.create_default_context()  # Using SSLContext
wrapped_socket = context.wrap_socket(sock, server_hostname=host)
wrapped_socket.connect((host, port))

# Create the HTTP GET request in the correct format
http_request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

# Send the HTTP request over the TCP connection
wrapped_socket.sendall(http_request.encode())

# Receive the response in chunks and combine them
response = b""
while True:
    chunk = wrapped_socket.recv(4096)
    if not chunk:
        break
    response += chunk

# Close the socket connection
wrapped_socket.close()

# Decode the response and split the headers from the body
response_text = response.decode('utf-8', errors='ignore')
header, html_body = response_text.split("\r\n\r\n", 1)  # Split headers and body

# Print response headers (optional, for debugging)
print(header)

# Pass the HTML body to BeautifulSoup for parsing
soup = BeautifulSoup(html_body, 'html.parser')

# Check if the page is loaded and contains the expected data
if not soup.find('div', class_='item'):
    print("No products found. The page structure may have changed or the request may have failed.")
else:
    print("Products found, proceeding with extraction.")

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

    # Attempt to extract color information safely
    if color_div and color_div.find('span'):
        color_span = color_div.find('span')
        color = color_span['data-product-id'] if 'data-product-id' in color_span.attrs else "Color attribute not available"
    else:
        color = "Color not available"

    link = title_div.find('a')['href'] if title_div else "Link not found"

    try:
        price = float(price.replace(' LEI', '').replace(',', '.').strip())  # Ensure price is a float
    except ValueError:
        continue  # Skip this product if the price is invalid

    # Now scrape the individual product page to get the origin country
    product_url = link
    try:
        # Create a new socket connection for the individual product page
        product_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        product_wrapped_socket = context.wrap_socket(product_sock, server_hostname=host)
        product_wrapped_socket.connect((host, port))

        # Create the HTTP GET request for the product page
        product_http_request = f"GET {product_url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        product_wrapped_socket.sendall(product_http_request.encode())

        # Receive the product response in chunks
        product_response = b""
        while True:
            chunk = product_wrapped_socket.recv(4096)
            if not chunk:
                break
            product_response += chunk

        # Close the product socket connection
        product_wrapped_socket.close()

        # Decode the product response and split the headers from the body
        product_response_text = product_response.decode('utf-8', errors='ignore')
        product_header, product_html_body = product_response_text.split("\r\n\r\n", 1)

        # Pass the product HTML body to BeautifulSoup for parsing
        product_soup = BeautifulSoup(product_html_body, 'html.parser')

        # Look for the 'Tara de origine' row in the table
        origin_country = "Country not available"
        table_rows = product_soup.find_all('tr', class_='param')
        for row in table_rows:
            name_td = row.find('td', class_='name')
            value_td = row.find('td', class_='value')
            if name_td and value_td and 'Tara de origine' in name_td.text:
                origin_country = value_td.text.strip()
                break

        items.append({
            "name": name,
            "price": price,  # Keep price in LEI for now
            "size": size,
            "color": color,
            "link": link,
            "origin_country": origin_country
        })
    except Exception as e:
        print(f"Error fetching product details for {link}: {e}")

# Function to convert LEI price to EUR
def convert_to_eur(product):
    product['price'] = round(product['price'] * LEI_TO_EUR_RATE, 2)  # Convert LEI to EUR and round to 2 decimal places
    return product

# Use map to apply the conversion to all products
items_in_eur = list(map(convert_to_eur, items))

# Print the products with price in EUR
for item in items_in_eur:
    print(f"Name: {item['name']:<52}, Price (EUR): {item['price']:<6}, Size: {item['size']:<4}, Color: {item['color']:<5}, Origin Country: {item['origin_country']:<15}, Link: {item['link']}")

# Use filter to get the products within the price range
filtered_items = list(filter(is_in_price_range, items_in_eur))

# Print the filtered products
print(f"Products within price range {MIN_PRICE} EUR to {MAX_PRICE} EUR:")
for item in filtered_items:
    print(f"Name: {item['name']:<52}, Price (EUR): {item['price']:<6}")

# Use reduce to sum up the prices of the filtered products
total_price = reduce(lambda acc, product: acc + product['price'], filtered_items, 0)
total_price = round(total_price, 2)

# Print the total price of the filtered products
print(f"Total price of filtered products: {total_price:.2f} EUR")

# Get the current UTC timestamp
utc_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# Create a new data structure that holds the filtered products, total price, and UTC timestamp
product_summary = {
    "filtered_products": filtered_items,
    "total_price": total_price,
    "timestamp_utc": utc_timestamp
}

# Serialization to JSON
def serialize_to_json(summary):
    json_str = "{"
    json_str += f'"filtered_products": ['
    for index, product in enumerate(summary["filtered_products"]):
        json_str += "{"
        json_str += f'"name": "{product["name"]}", '
        json_str += f'"price": {product["price"]}, '
        json_str += f'"size": "{product["size"]}", '
        json_str += f'"color": "{product["color"]}", '
        json_str += f'"origin_country": "{product["origin_country"]}", '
        json_str += f'"link": "{product["link"]}"'
        json_str += "}"
        if index < len(summary["filtered_products"]) - 1:
            json_str += ", "
    json_str += "], "
    json_str += f'"total_price": {summary["total_price"]}, '
    json_str += f'"timestamp_utc": "{summary["timestamp_utc"]}"'
    json_str += "}"
    return json_str

# Serialization to XML
def serialize_to_xml(summary):
    xml_str = "<product_summary>\n"
    xml_str += "  <filtered_products>\n"
    for product in summary["filtered_products"]:
        xml_str += "    <product>\n"
        xml_str += f'      <name>{product["name"]}</name>\n'
        xml_str += f'      <price>{product["price"]}</price>\n'
        xml_str += f'      <size>{product["size"]}</size>\n'
        xml_str += f'      <color>{product["color"]}</color>\n'
        xml_str += f'      <origin_country>{product["origin_country"]}</origin_country>\n'
        xml_str += f'      <link>{product["link"]}</link>\n'
        xml_str += "    </product>\n"
    xml_str += "  </filtered_products>\n"
    xml_str += f'  <total_price>{summary["total_price"]}</total_price>\n'
    xml_str += f'  <timestamp_utc>{summary["timestamp_utc"]}</timestamp_utc>\n'
    xml_str += "</product_summary>"
    return xml_str

# Serialize the product summary
json_output = serialize_to_json(product_summary)
xml_output = serialize_to_xml(product_summary)

# Print serialized outputs
print("\nJSON Output:")
print(json_output)

print("\nXML Output:")
print(xml_output)

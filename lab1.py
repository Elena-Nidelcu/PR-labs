import requests
from bs4 import BeautifulSoup

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

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all product containers
products = soup.find_all('div', class_='item')

# Extract information
for product in products:
    # Get product name
    title_div = product.find('div', class_='title')
    if title_div:
        name = title_div.find('a').text.strip()
    else:
        name = "Name not found"

    # Get product price
    price_div = product.find('div', class_='price')
    if price_div:
        price_elements = price_div.find_all('div')
        if price_elements:
            price = price_elements[-1].text.strip()  # Getting the last price div
        else:
            price = "Price not available"
    else:
        price = "Price not found"

    # Get product size
    size_div = product.find('div', class_='sizes')
    if size_div and size_div.find('span'):
        size = size_div.find('span').text.strip()
    else:
        size = "Size not available"

    # Get product color (if available)
    color_div = product.find('div', class_='colors')
    if color_div:
        color = color_div.find('span')['data-product-id']  # Adjust based on actual attribute
    else:
        color = "Color not available"

    # # Get product brand (from a data attribute)
    # brand = product.get('data-brand', 'Brand not available')
    #
    # # Get product category
    # category = product.get('data-category-4', 'Category not available')

    # Get product link
    if title_div:
        link = title_div.find('a')['href']
    else:
        link = "Link not found"

    if name != "Name not found" and price != "Price not found" and price != "Price not available" and link != "Link not found":
        print(f"Name: {name:<52}, Price: {price:<11}, Size: {size:<4}, Color: {color:<5}, Link: {link}")

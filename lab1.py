import requests
from bs4 import BeautifulSoup

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

    if name != "Name not found" and price != "Price not found" and price != "Price not available" and link != "Link not found":
        print(f"Name: {name:<52}, Price: {price:<6}, Size: {size:<4}, Color: {color:<5}, Link: {link}")

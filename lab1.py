import requests
from bs4 import BeautifulSoup

# Conversion rate from LEI to EUR (example rate: 1 LEI = 0.05 EUR)
LEI_TO_EUR_RATE = 0.05

# Define the desired price range (in EUR)
MIN_PRICE = 30.0
MAX_PRICE = 100.0

# Function to filter products based on price range
def is_in_price_range(product):
    return MIN_PRICE <= product['price'] <= MAX_PRICE

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

    # Now scrape the individual product page to get the origin country
    product_url = link
    product_response = requests.get(product_url)
    if product_response.status_code == 200:
        product_soup = BeautifulSoup(product_response.text, 'html.parser')

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
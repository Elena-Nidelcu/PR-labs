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

    # Check for valid product fields
    if name != "Name not found" and price != "Price not found" and price != "Price not available" and link != "Link not found":
        print(f"Name: {name:<52}, Price: {price:<6}, Size: {size:<4}, Color: {color:<5}, Link: {link}")

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

            print(f"Origin Country: {origin_country}")

            items.append({
                "name": name,
                "price": price,
                "size": size,
                "color": color,
                "link": link,
                "origin_country": origin_country  # Include origin country in the scraped data
            })

# Optional: You can then save `items` to a file or continue processing it further

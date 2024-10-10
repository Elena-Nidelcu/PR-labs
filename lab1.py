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
import requests

# 1. Create a product
# Example product details for the Nike shoes
# product_data = {
#     "name": "Incaltaminte Sport Nike W AIR ZOOM ALPHAFLY NEXT 2",
#     "price": 5999.00,
#     "size": 37,
#     "color": "88291",
#     "link": "https://sportlandia.md/incaltaminte-sport-nike-w-air-zoom-alphafly-next-2-dn3559-600-88291"
# }
#
# # Sending the POST request to create a new product
# response = requests.post('http://127.0.0.1:5000/create', json=product_data)
# print(response.json())  # {'message': 'Product created'}
#
# # 2. Read a product
# response = requests.get('http://127.0.0.1:5000/read', params={'id': 2})
# print(response.json())  # Product data
#
# # 2-2. Read products without ID (test pagination)
# # Fetch the first 5 products (default pagination)
# response = requests.get('http://127.0.0.1:5000/read')
# for i in response.json():
#     print(i)
#
# # Fetch the next 5 products with offset = 5
# response = requests.get('http://127.0.0.1:5000/read', params={'offset': 5, 'limit': 5})
# for i in response.json():
#     print(i)
#
# # 3. Update a product
# # Example update request to update the product's name and price
# response = requests.put(
#     'http://127.0.0.1:5000/update',
#     params={'id': 29},
#     json={"name": "Updated Sneakers", "price": 5000.00, "size": 38, "color": "Red"}
# )
#
# # Print the response from the server
# print(response.json())  # Expected: {'message': 'Product updated'}
#
# # 4. Delete a product
# response = requests.delete('http://127.0.0.1:5000/delete', params={'id': 30})
# print(response.json())  # {'message': 'Product deleted'}

# The URL for the upload endpoint
url = 'http://127.0.0.1:5000/upload'

# Path to the file you want to upload
file_path = 'file.json'  # Make sure this file exists in the current directory

# Open the file in binary mode and send it as part of the POST request
with open(file_path, 'rb') as file:
    # 'file' here must match the parameter name in the Flask request.files['file']
    files = {'file': file}

    # Send the POST request
    response = requests.post(url, files=files)

# Print the server's response (should confirm file upload)
print(response.json())
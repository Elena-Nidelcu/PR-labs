from flask import Flask, request, jsonify
import mysql.connector
import requests
import json
import socket

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return 'Welcome to the Product Management API'

# Connect to MySQL
def get_db_connection():
    cnx = mysql.connector.connect(
        user='root',
        password='Root123+',
        host='localhost',
        database='sportlandia'
    )
    return cnx


# CREATE - POST /create
@app.route('/create', methods=['POST'])
def create_product():
    data = request.json
    name = data['name']
    price = data['price']
    size = data['size']
    color = data['color']
    link = data['link']

    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Insert the new product with the additional fields
    cursor.execute("""
        INSERT INTO products (name, price, size, color, link)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, price, size, color, link))
    cnx.commit()

    cursor.close()
    cnx.close()

    return jsonify({'message': 'Product created'}), 201


# READ - GET /read
@app.route('/read', methods=['GET'])
def read_product():
    product_id = request.args.get('id')  # Fetching the product ID from the request
    offset = request.args.get('offset', default=0, type=int)  # Default offset = 0
    limit = request.args.get('limit', default=5, type=int)    # Default limit = 5

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    # If product_id is provided, fetch that specific product
    if product_id:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        cursor.close()
        cnx.close()

        if product:
            return jsonify(product), 200
        else:
            return jsonify({'message': 'Product not found'}), 404

    # If product_id is not provided, fetch a paginated list of products
    cursor.execute("SELECT * FROM products LIMIT %s OFFSET %s", (limit, offset))
    products = cursor.fetchall()

    cursor.close()
    cnx.close()

    if products:
        return jsonify(products), 200
    else:
        return jsonify({'message': 'No products found'}), 404

@app.route('/update', methods=['PUT'])
def update_product():
    product_id = request.args.get('id')
    data = request.json

    # Check if the product ID is provided
    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400

    # Extract new data from the request JSON
    new_name = data.get('name')
    new_price = data.get('price')
    new_size = data.get('size')
    new_color = data.get('color')
    new_link = data.get('link')

    # Ensure at least one field is provided for updating
    if not any([new_name, new_price, new_size, new_color, new_link]):
        return jsonify({'message': 'No fields to update'}), 400

    # Connect to the database
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Build dynamic update query based on provided fields
    update_fields = []
    update_values = []

    if new_name:
        update_fields.append("name = %s")
        update_values.append(new_name)
    if new_price:
        update_fields.append("price = %s")
        update_values.append(new_price)
    if new_size:
        update_fields.append("size = %s")
        update_values.append(new_size)
    if new_color:
        update_fields.append("color = %s")
        update_values.append(new_color)
    if new_link:
        update_fields.append("link = %s")
        update_values.append(new_link)

    update_values.append(product_id)  # Add product_id to the list of values

    # Construct the query string
    update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"

    # Execute the update query
    cursor.execute(update_query, tuple(update_values))

    cnx.commit()
    cursor.close()
    cnx.close()

    return jsonify({'message': 'Product updated'}), 200


# DELETE - DELETE /delete
@app.route('/delete', methods=['DELETE'])
def delete_product():
    product_id = request.args.get('id')
    name = request.args.get('name')

    cnx = get_db_connection()
    cursor = cnx.cursor()

    if product_id:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    elif name:
        cursor.execute("DELETE FROM products WHERE name = %s", (name,))

    cnx.commit()
    cursor.close()
    cnx.close()

    return jsonify({'message': 'Product deleted'}), 200


LEADER_URL = "http://localhost:5000/leader"


# Function to fetch the current leader
def get_leader():
    try:
        response = requests.get(LEADER_URL)
        if response.status_code == 200:
            leader_info = response.json()
            print(f"Current leader is Node {leader_info['leader_id']}.")
            return leader_info['leader_id']
        else:
            print("Failed to fetch leader info.")
    except Exception as e:
        print(f"Error fetching leader: {e}")
    return None


# Function to send data to the leader
def send_to_leader(request_data):
    leader_id = get_leader()
    if leader_id is None:
        print("No leader available. Cannot process request.")
        return

    # Send request to the leader
    leader_port = 10000 + leader_id
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        message = {'type': 'DatabaseRequest', 'request_data': request_data}
        s.sendto(json.dumps(message).encode(), ('localhost', leader_port))

        # Await response from the leader
        data, _ = s.recvfrom(1024)
        response = json.loads(data.decode())
        print(f"Response from leader: {response}")


# Endpoint to upload a file and process it
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is included in the request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']

    # If no file is selected or file is empty
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Reading the content of the file (assuming it's a JSON file)
    file_content = file.read().decode('utf-8')  # Read the file and decode it (assuming text content)

    print(f"Received file content: {file_content}")  # Log the content of the file (for debugging)

    # Assuming the file content is a JSON object, process it
    try:
        file_data = json.loads(file_content)
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON file content'}), 400

    # Send the data to the leader for processing
    send_to_leader(file_data)

    return jsonify({'message': 'File received, processed, and sent to leader'}), 200


# Route to handle file uploads
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     # Check if a file is included in the request
#     if 'file' not in request.files:
#         return jsonify({'message': 'No file part in the request'}), 400
#
#     file = request.files['file']
#
#     # If no file is selected or file is empty
#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400
#
#     # Reading the content of the file (assuming it's a JSON file)
#     file_content = file.read().decode('utf-8')  # Read the file and decode it (assuming text content)
#
#     print(file_content)  # Log the content of the file (for debugging)
#
#     return jsonify({'message': 'File received and content printed', 'content': file_content}), 200

# @app.route('/update_leader', methods=['POST'])
# def update_leader():
#     data = request.get_json()
#     leader_id = data.get('leader_id')
#     if leader_id:
#         print(f"Manager received leader update: Node {leader_id} is now the leader.")
#         return jsonify({'message': 'Leader updated', 'leader_id': leader_id}), 200
#     return jsonify({'message': 'Invalid leader ID'}), 400


# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)

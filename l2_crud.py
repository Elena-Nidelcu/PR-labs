from flask import Flask, request, jsonify
import mysql.connector

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


# Route to handle file uploads
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

    print(file_content)  # Log the content of the file (for debugging)

    return jsonify({'message': 'File received and content printed'}), 200


# Run the server
if __name__ == '__main__':
    app.run(debug=True)

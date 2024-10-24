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
@app.route('/read', methods=['GET'])
def read_product():
    product_id = request.args.get('id')  # Fetching the product ID from the request

    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400  # Return error if no ID is provided

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    # Fetch product by ID only
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    cnx.close()

    if product:
        return jsonify(product), 200
    else:
        return jsonify({'message': 'Product not found'}), 404



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


# Run the server
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import mysql.connector
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

connected_users = []

# --- Database Connection ---
def get_db_connection():
    cnx = mysql.connector.connect(
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'Root123+'),
        host=os.getenv('MYSQL_HOST', 'db'),  # Docker service name for the database
        database=os.getenv('MYSQL_DB', 'sportlandia'),
        port=3306
    )
    return cnx

# --- Create Table if it Doesn't Exist ---
def create_products_table():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        price DECIMAL(10, 2),
        size INT,
        color VARCHAR(255),
        link VARCHAR(255)
    );
    """
    cursor.execute(create_table_query)
    cnx.commit()
    cursor.close()
    cnx.close()

# Call the function to create the table at the start of the application
create_products_table()

# --- Home Route ---
@app.route('/')
def home():
    return 'Welcome to the Product Management and Chat Application'

# --- CRUD Operations ---
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
    product_id = request.args.get('id')
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=5, type=int)

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    if product_id:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        cnx.close()
        if product:
            return jsonify(product), 200
        else:
            return jsonify({'message': 'Product not found'}), 404

    cursor.execute("SELECT * FROM products LIMIT %s OFFSET %s", (limit, offset))
    products = cursor.fetchall()
    cursor.close()
    cnx.close()

    if products:
        return jsonify(products), 200
    else:
        return jsonify({'message': 'No products found'}), 404

# UPDATE - PUT /update
@app.route('/update', methods=['PUT'])
def update_product():
    product_id = request.args.get('id')
    data = request.json

    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400

    new_name = data.get('name')
    new_price = data.get('price')
    new_size = data.get('size')
    new_color = data.get('color')
    new_link = data.get('link')

    if not any([new_name, new_price, new_size, new_color, new_link]):
        return jsonify({'message': 'No fields to update'}), 400

    cnx = get_db_connection()
    cursor = cnx.cursor()
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

    update_values.append(product_id)
    update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
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

# File Upload - POST /upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    file_content = file.read().decode('utf-8')
    print(file_content)

    return jsonify({'message': 'File received and content printed', 'content': file_content}), 200

# --- Chat Room ---
@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    if username not in connected_users:
        connected_users.append(username)
        emit('user_joined', {'username': username}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', {'username': data['username'], 'message': data['message']}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    emit('user_left', {'username': 'a user'}, broadcast=True)

# --- Run Application ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

connected_users = []

@app.route('/')
def chat():
    return render_template('chat.html')  # Serve the HTML file

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

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Хранение активных пользователей
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    nickname = request.form['nickname']
    if nickname:
        session['nickname'] = nickname
        users[nickname] = request.remote_addr
        return render_template('chat.html', nickname=nickname)
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    nickname = session.get('nickname')
    if nickname:
        emit('status', {'msg': f'{nickname} присоединился к чату!'}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    nickname = session.get('nickname')
    if nickname:
        emit('message', {'msg': f'{nickname}: {data["msg"]}'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    nickname = session.get('nickname')
    if nickname in users:
        del users[nickname]
        emit('status', {'msg': f'{nickname} покинул чат.'}, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', {'msg': f'{session["nickname"]} печатает...'}, broadcast=True)

socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

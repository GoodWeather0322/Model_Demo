from flask import Blueprint, render_template, request, jsonify
import string
import re
import codecs
import time
import os
from pathlib import Path
from flask_socketio import SocketIO, emit
from ..create_socket import socketio

newsgen = Blueprint('newsgen', __name__, template_folder='templates')

@newsgen.route('/', methods=['GET', 'POST'])
def index():
    return render_template('newsgen_index.html')

@newsgen.route('/test')
def test_page():
    return render_template('test.html') 

@newsgen.route('/submit', methods=['POST'])
def submit():

    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    source_text = request.form.get('submitsummary', 'not found s', type=str).strip()

    return jsonify(result=source_text+'123123', select='select', now_time='now_time')

@socketio.on('send_message')   
def message_recieved(data):   
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print(now_time)
    print('data', data)
    # emit('message', {'msg': data['text']})
    test()

@socketio.on('joined')   
def message_recieved(data):   
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print(now_time)
    print('data', data)

def test():
    for i in range(10):
        emit('message', {'msg': str(i)})
        print(str(i))
        time.sleep(0.5)
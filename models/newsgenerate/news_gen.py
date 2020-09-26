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

@socketio.on('session_connect', namespace='/newsgen')   
def message_recieved(data):   
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    #print('*******connect establish', now_time)
    emit('status', {'msg': 'connect establish: '+now_time})

@socketio.on('send_message', namespace='/newsgen')   
def message_recieved(data):   
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print(now_time)
    sent = data['text']
    emit('message', {'msg': sent})

print('='*30)
print('start load gpt2 model')
print('='*30)

# from transformers import BertTokenizerFast
# from transformers import GPT2Tokenizer, GPT2LMHeadModel

# bert_tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
# gpt_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')

# model = GPT2LMHeadModel.from_pretrained('gpt2-medium')
# model.resize_token_embeddings(bert_tokenizer.vocab_size)
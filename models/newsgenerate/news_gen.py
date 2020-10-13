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

stop_gen = False

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
    global stop_gen
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print(now_time)
    sent = data['text']
    print(sent)
    
    # emit('message', {'msg': sent})
    stop_gen = False
    generate_news(sent)

@socketio.on('stop_gen', namespace='/newsgen')   
def message_recieved(data):  
    global stop_gen
    print('stop gen click')
    stop_gen = True
    

print('='*30)
print('start load gpt2 model')

from transformers import BertTokenizer
from transformers import GPT2Config, GPT2LMHeadModel
import torch

bert_tokenizer = BertTokenizer.from_pretrained('models/newsgenerate/gpt2_model/config/bert_chinese_tokenizer')
gpt2_config = GPT2Config.from_json_file('models/newsgenerate/gpt2_model/config/gpt2/config.json')

gpt2_model = GPT2LMHeadModel(gpt2_config)
gpt2_model.resize_token_embeddings(bert_tokenizer.vocab_size)

from collections import OrderedDict
state_dict = torch.load('models/newsgenerate/gpt2_model/gpt2.mdl', map_location='cpu')
new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] # remove `module.`
    new_state_dict[name] = v

print(gpt2_model.load_state_dict(new_state_dict))

for parms in gpt2_model.parameters():
    parms.requires_grad=False
    
print('total parms : ', sum(p.numel() for p in gpt2_model.parameters()))
print('trainable parms : ', sum(p.numel() for p in gpt2_model.parameters() if p.requires_grad))

print('='*30)

max_length = 1000
max_history_length = 120
beam_size = 10
repetition_penalty = 3.0
temperature = 2.0
top_p = 0.7
no_repeat_ngram_size = 5
per_output_length = 10

def generate_news(sent):
    global stop_gen
    sents = re.split('。|，| ', sent)
    while '' in sents:
        sents.remove('')

    bert_sent = '[CLS]'
    for sent in sents:
        bert_sent += sent
        bert_sent += '[SEP]'

    bert_tokens = bert_tokenizer.tokenize(bert_sent)
    bert_idxs = bert_tokenizer.convert_tokens_to_ids(bert_tokens)
    bert_seqs = torch.LongTensor(bert_idxs).unsqueeze(0)

    # print(bert_seqs.shape)

    output = ''
    output_sent = bert_tokens

    for i in range(len(output_sent)):
        if output_sent[i] == '[CLS]':
            pass
        elif output_sent[i] == '[UNK]':
            pass
        elif output_sent[i] == '[SEP]':
            output += ' '
        else:
            output += output_sent[i]
    
    for i in range(max_length // per_output_length):
        if stop_gen == False:
            # print('stop_gen', stop_gen)
            if bert_seqs.size(1) > max_history_length:
                bert_seqs = bert_seqs[:, -max_history_length:]

            # print(bert_seqs.shape)
            bert_seqs = gpt2_model.generate(bert_seqs, 
                                            max_length=bert_seqs.size(1)+per_output_length, 
                                            top_k=beam_size, 
                                            top_p=top_p, 
                                            repetition_penalty=repetition_penalty,
                                            temperature=temperature,
                                            do_sample = False,
                                            num_return_sequences=1, 
                                            no_repeat_ngram_size=no_repeat_ngram_size,
                                            pad_token_id=bert_tokenizer.pad_token_id,
                                            bos_token_id=bert_tokenizer.cls_token_id,
            #                                       eos_token_id=bert_tokenizer.sep_token_id
                                            )

            output_seq = bert_tokenizer.convert_ids_to_tokens(bert_seqs[0])

            output_sent = output_seq[-per_output_length:]

            
            for i in range(len(output_sent)):
                if output_sent[i] == '[CLS]':
                    pass
                elif output_sent[i] == '[UNK]':
                    pass
                elif output_sent[i] == '[SEP]':
                    output += ' '
                else:
                    output += output_sent[i]
            # print(output)
            emit('message', {'msg': output})
        else:
            print('stop generate article')
            break
        
    print(output)
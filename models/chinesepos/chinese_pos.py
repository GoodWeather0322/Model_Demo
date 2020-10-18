from flask import Blueprint, render_template, request, jsonify
import string
import re
import codecs
import time
import os
from pathlib import Path
from flask_socketio import SocketIO, emit
from ..create_socket import socketio

pos = Blueprint('pos', __name__, template_folder='templates', static_folder='static')

@pos.route('/', methods=['GET', 'POST'])
def index():
    return render_template('chinesepos_index.html')

@pos.route('/test')
def test_page():
    return render_template('test.html') 

@pos.route('/submit', methods=['POST'])
def submit():

    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    source_text = request.form.get('submitsummary', 'not found s', type=str).strip()

    return jsonify(result=source_text+'123123', select='select', now_time='now_time')

@socketio.on('session_connect', namespace='/pos')   
def message_recieved(data):       
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    #print('*******connect establish', now_time)
    emit('status', {'msg': 'connect establish: '+now_time,})

@socketio.on('send_message', namespace='/pos')   
def message_recieved(data):   
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    print(now_time)
    sent = data['text']
    option = data['option']
    print(option, sent)
    
    # emit('message', {'msg': sent})
    do_pos(option, sent)
    

print('='*30)
print('start load Albert_CRF model')

from transformers import BertTokenizer, AlbertConfig
import torch
from .modeling import Albert_CRF

pos_tag_file = "models/chinesepos/albert_model/pos.tgt.dict"
tag2id = {}
tag2id['[CKIP]'] = 0
tag2id['[MONPA]'] = 1
count = 2
with open(pos_tag_file) as fp:
    for line in fp:
        line = line.strip().split()
        tag2id[line[0]] = count
        count += 1
id2tag = {v:k for k, v in tag2id.items()}

print(len(tag2id))


tokenizer = BertTokenizer.from_pretrained('models/chinesepos/albert_model/config/bert_chinese_tokenizer')
albert_config = AlbertConfig.from_json_file('models/chinesepos/albert_model/config/albert/config.json')

add_count = tokenizer.add_tokens(['[CKIP]', '[MONPA]'])
albert_crf = Albert_CRF(albert_config, id2tag, len(tokenizer))

from collections import OrderedDict
ckpt = torch.load('models/chinesepos/albert_model/albert_large.ckpt', map_location='cpu')
state_dict = ckpt['net']
new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] # remove `module.`
    new_state_dict[name] = v

print(albert_crf.load_state_dict(new_state_dict))

for parms in albert_crf.parameters():
    parms.requires_grad=False
    
print('total parms : ', sum(p.numel() for p in albert_crf.parameters()))
print('trainable parms : ', sum(p.numel() for p in albert_crf.parameters() if p.requires_grad))

print('='*30)


def do_pos(option, sent):
    if option == 'CKIP':
        sent = '[CKIP] ' + sent + ' [SEP]'
    elif option == 'MONPA':
        sent = '[MONPA] ' + sent + ' [SEP]'
    else:
        sent = '[MONPA] ' + sent + ' [SEP]'
    
    token = tokenizer.tokenize(sent)
    if len(token) > 256:
        token = token[:256]

    ids = tokenizer.convert_tokens_to_ids(token)
    input_seq = torch.LongTensor(ids)
    input_mask = torch.ones(input_seq.shape)

    best_tags_list = albert_crf(input_seq.unsqueeze(0), input_mask.unsqueeze(0))
    best_tags_list = best_tags_list[0]
    best_tags_list = [id2tag[tag_id] for tag_id in best_tags_list]

    if len(best_tags_list) != len(token):
        print('something error')
        emit('message', {'msg': [['something'], ['error']]})

    toks = []
    tags = []

    temp_tok = ''
    
    for tok, tag in zip(token[1:-1], best_tags_list[1:-1]):
        
        tag = tag.lower()
        tag = tag.split('-')
        
        if len(tag) == 2:
            bound, pos = tag
        elif len(tag) == 3:
            bound, _, pos = tag
            
        if bound == 's':
            toks.append(tok)
            tags.append(pos)
            
            continue
            
        temp_tok += tok+' '
        
        if bound == 'b':
            tags.append(pos)
            
        if bound == 'e':
            temp_tok = temp_tok.replace(' ##', '')
            if temp_tok.replace(' ', '').encode().isalpha() == False:
                temp_tok = temp_tok.replace(' ', '')
            toks.append(temp_tok)
            temp_tok = ''

            
    if len(temp_tok) > 0: # special case: no 'E-' in predicted_pos
        toks.append(temp_tok)
        temp_tok = ''
        
    if len(toks) != len(tags):
        emit('message', {'msg': [['something'], ['error']]})

    output = ''

    for tok, tag in zip(toks, tags):
        # print(tok, tag)
        output += tok + ' {' + tag.lower() + '}' + '   '
    
    # print(output)
    # output = [1, 2, 3, 4, 5]
    emit('message', {'msg': [toks, tags]})

        
    print(output)
from flask import Blueprint, render_template, request, jsonify
import string
import re
import codecs
import time
import os
from pathlib import Path

wordseg = Blueprint('wordseg', __name__, template_folder='templates')

@wordseg.route('/', methods=['GET', 'POST'])
def index():
    return render_template('wordseg_index.html')

@wordseg.route('/test')
def test_page():
    return render_template('test.html')

@wordseg.route('/result', methods=['POST'])
def submit():
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    text = request.form['submitsummary']
    select = request.form['options']

    punctuation = '[\\s+\\.\\!\\/_,$%^*(+"\']+|[+——！！，。？、~@#￥%……&*（）「」《》：；;]+'

    text = re.sub(punctuation, "", text)
    # print(text)
    result_fwd, not_match_fwd = cut_sentence_fwd(text, dict_list, max_len)
    result_bwd, not_match_bwd = cut_sentence_bwd(text, dict_list, max_len)

    # result_fwd.append(str(len(result_fwd)))
    # result_bwd.append(str(len(result_bwd)))

    if select == 'forward':
        result = result_fwd
    elif select == 'backward':
        result = result_bwd
    elif select == 'best':
        if len(result_fwd) < len(result_bwd):
            result = result_fwd
        elif len(result_bwd) < len(result_fwd):
            result = result_bwd
        else:
            fwd_count = {}
            bwd_count = {}
            for i in range(max_len, 0, -1):
                fwd_count[i] = 0
                bwd_count[i] = 0
            for i in range(len(result_fwd)):
                fwd_count[len(result_fwd[i])]+=1
                bwd_count[len(result_bwd[i])]+=1

            _fwd = 0
            _bwd = 0

            _found = False
            for i in range(max_len, 0, -1):
                _fwd += fwd_count[i]
                _bwd += bwd_count[i]
                if _fwd > _bwd:
                    result = result_fwd
                    _found = True
                    break
                elif _bwd > _fwd:
                    result = result_fwd
                    _found = True
                    break
                else:
                    pass
            
            if _found == False:
                result = result_fwd
    
    length = len(result)
    output = ' '.join(result)

    english_format = re.findall('[a-zA-Z\s]+\s+',output) 
    digit_format = re.findall('[\d\s]+\s+',output)

    for word in english_format:
        word = word.strip()
        new_word = ''.join(word.split())
        output = output.replace(word, new_word)

    for word in digit_format:
        word = word.strip()
        new_word = ''.join(word.split())
        output = output.replace(word, new_word)

    # print(output)
    return render_template('wordseg_result.html', option=select, length=length, output=output, now_time=now_time)

@wordseg.route('/merge', methods=['POST'])
def merge():
    merge_text = request.form.get('select', 'not found m', type=str).strip()
    source_text = request.form.get('submitsummary', 'not found s', type=str).strip()
    merge_result = ''.join(merge_text.split())
    result = source_text.replace(merge_text, merge_result)
    
    return jsonify(result=result, select=merge_result)

@wordseg.route('/split', methods=['POST'])
def split():
    split_text = request.form.get('select', 'not found m', type=str).strip()
    source_text = request.form.get('submitsummary', 'not found s', type=str).strip()
    split_result = ' '.join(''.join(split_text.split()))
    result = source_text.replace(split_text, split_result)
    
    return jsonify(result=result, select=split_result)




def load_dict(dict_dir):
    global max_len, list1, dict_list

    with open (dict_dir, encoding='utf-8-sig') as fp:
        for line in fp:
            list1.append(line.strip())

    # print(len(list1))
            
    for word in list1:
        if len(word) > max_len:
            max_len = len(word)
            
    for i in range(max_len):
        dict_list.append({})
        
    for word in list1:
        dict_list[len(word)-1][word] = 0

def cut_sentence_fwd(text, dict_list, max_len):
    result = []
    not_match = []
    text_len = len(text)
    no_word = ''
    n = 0
    while n < text_len:
        matched = 0
        for i in range(max_len, 0, -1):
            word = text[n:n+i]
            if word in dict_list[i-1]:
                matched = 1
                result.append(word)
                #dict_list[i-1][word]+=1
                n = n + i
                break
        if not matched:
            not_match.append(text[n])
            result.append(text[n])
            n = n + 1
    return result, not_match

def cut_sentence_bwd(text, dict_list, max_len):
    result = []
    not_match = []
    text_len = len(text)
    no_word = ''
    n = text_len
    while n > 0:
        matched = 0
        for i in range(max_len, 0, -1):
            word = text[n-i:n]
            if word in dict_list[i-1]:
                matched = 1
                result.append(word)
                #dict_list[i-1][word]+=1
                n = n - i
                break
        if not matched:
            not_match.append(text[n-1])
            result.append(text[n-1])
            n = n - 1
    result.reverse()
    return result, not_match

max_len = 0
list1 = []
dict_list = []

dict_dir = Path(os.path.abspath(__file__)).parent / "DICT.txt"
load_dict(dict_dir)
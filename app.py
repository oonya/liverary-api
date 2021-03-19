from flask import Flask, request, jsonify, json
import os
import json

from flask_cors import CORS, cross_origin

import MeCab

from models.models import Words
from models.database import db_session
import datetime


import google.auth.transport.requests
import google.oauth2.id_token


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['JSON_AS_ASCII'] = False


@app.route('/')
def deltee_config():
    return jsonify({"res" : "response"})


@app.route('/words')
def show_words():
    try:
        h = request.headers['Authorization']
    except Exception:
        return 'Unauthorized?', 401
        
    uuid = get_user_id(h)

    if uuid == None:
        return 'Unauthorized', 401

    with open('responses/words.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())
    
    words = db_session.query(Words).filter(Words.uuid==uuid).all()

    dic_ary = []
    for w in words:
        dic_ary.append({"text":w.vocabulary, "date":w.date})

    res["words"] = sorted(dic_ary, key=lambda x:x['date'])

    return jsonify(res)



@app.route('/word_num_list')
def get_word_num_list():
    try:
        h = request.headers['Authorization']
    except Exception:
        return 'Unauthorized?', 401

    uuid = get_user_id(h)
    
    if uuid == None:
        return 'Unauthorized', 401

    with open('responses/word_num_list.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())

    a = db_session.query(Words).filter(Words.uuid==uuid).all()
    for m in a:
        res["word_num_list"] = inc_res(res["word_num_list"], m)
        

    return jsonify(res)


def inc_res(dic_array, word):
    for d in dic_array:
        if d["month"] == word.date[:7]:
            d["sum"] += 1
            return dic_array
    
    dic_array.append({"month":word.date[:7], "sum":1})
    return dic_array


@app.route('/delete', methods=['POST'])
def delete_word():
    try:
        h = request.headers['Authorization']
    except Exception:
        return 'Unauthorized?', 401

    uuid = get_user_id(h)
    
    if uuid == None:
        return 'Unauthorized', 401

    f = request.get_data()
    form_data = json.loads(f.decode('utf-8'))
    word = form_data['word']

    a = db_session.query(Words).filter(Words.uuid==uuid, Words.vocabulary==word).first()
    if a == None:
        raise Exception

    db_session.delete(a)
    db_session.commit()

    return '', 204


@app.route('/get-morphological/<string:text>')
def morphological_analysis(text):
    res = ""
    m = MeCab.Tagger('')
    node = m.parseToNode(text)
    while node:
        # print(node.surface, node.feature.split(',')[0], '\n')
        print(node.surface, node.feature, '\n')

        res += node.surface + "  " + node.feature.split(',')[0] + "____"
        node = node.next

    return jsonify({"res":res})


@app.route('/save-vocabulary', methods=['POST'])
def save_vocabulary():
    try:
        h = request.headers['Authorization']
    except Exception:
        return 'Unauthorized?', 401

    uuid = get_user_id(h)
    
    if uuid == None:
        return 'Unauthorized', 401

    f = request.get_data()
    form_data = json.loads(f.decode('utf-8'))
    text = form_data['text']

    m = MeCab.Tagger('')
    node = m.parseToNode(text)

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    
    while node:
        part = node.feature.split(',')[0]
        if part != 'BOS/EOS' and part != '記号' and part != '助詞' and part != '助動詞' and part != '補助記号':
            word = kata_to_hira(node.feature.split(',')[6])

            if unique_vocabulary(uuid, word):
                w = Words(uuid=uuid, vocabulary=word, date=date)
                db_session.add(w)
                db_session.commit()

        node = node.next


    return 'succeed', 204


def unique_vocabulary(uuid, word):
    a = db_session.query(Words).filter(Words.uuid==uuid, Words.vocabulary==word).first()
    return a == None

def kata_to_hira(strj):
    return "".join([chr(ord(ch) - 96) if ("ァ" <= ch <= "ヴ") else ch for ch in strj])

@app.route('/debug/show-db')
def show_db():
    try:
        h = request.headers['Authorization']
    except Exception:
        return 'Unauthorized?', 401

    uuid = get_user_id(h)
    
    if uuid == None:
        return 'Unauthorized', 401

    res = {"res" : []}
    
    a = db_session.query(Words).filter(Words.uuid==uuid).all()
    for m in a:
        res["res"].append({"uuid":m.uuid, "voca":m.vocabulary, "date":m.date})
        print("uuid:{}\nvoca:{}\ndate:{}\n".format(m.uuid, m.vocabulary, m.date))
    
    return jsonify(res)


def get_user_id(header):
    HTTP_REQUEST = google.auth.transport.requests.Request()
    id_token = header.split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        return None
    
    return claims['user_id']


if __name__ == '__main__':
    app.run()
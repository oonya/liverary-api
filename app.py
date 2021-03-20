from flask import Flask, request, jsonify, json
import os
import json

from flask_cors import CORS, cross_origin

import MeCab

from models.models import Words
from models.database import db_session
from sqlalchemy import desc
import datetime


import google.auth.transport.requests
import google.oauth2.id_token

from errors import Expired
import pyrebase


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['JSON_AS_ASCII'] = False

# 今は俺のアカウントのになってるので、takummaのに差し替える
config = {
    "apiKey": os.getenv('apiKey'),
    "authDomain": os.getenv('authDomain'),
    "databaseURL": os.getenv('databaseURL'),
    "projectId": os.getenv('projectId'),
    "storageBucket": os.getenv('storageBucket'),
    "messagingSenderId": os.getenv('messagingSenderId'),
    "appId": os.getenv('appId'),
    "measurementId": os.getenv('measurementId')
}
firebase = pyrebase.initialize_app(config)


@app.route('/')
def deltee_config():
    return jsonify({"res" : "response"})


@app.route('/words')
def show_words():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401


    with open('responses/words.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())
    
    words = db_session.query(Words).filter(Words.uuid==uuid).all()

    dic_ary = []
    for w in words:
        dic_ary.append({"text":w.vocabulary, "date":w.date})

    res["words"] = sorted(dic_ary, key=lambda x:x['date'], reverse=True)

    return jsonify(res)



@app.route('/word_num_list')
def get_word_num_list():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401


    with open('responses/word_num_list.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())

    a = db_session.query(Words).filter(Words.uuid==uuid).all()

    dic_ary = []
    for m in a:
        dic_ary = inc_res(dic_ary, m)
    
    res['word_num_list'] = sorted(dic_ary, key=lambda x:x['month'])

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
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401


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
    f = request.get_data()
    form_data = json.loads(f.decode('utf-8'))
    text = form_data['text']
    device_id = form_data['deviceId']

    db = firebase.database()
    users = db.child("users").get()
    for user in users.each():
        if user.val()['deviceId'] == device_id:
            uuid = user.key()

    if uuid == None:
        return 'cannot find linked uuid', 401

    m = MeCab.Tagger('')
    node = m.parseToNode(text)

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    
    while node:
        part = node.feature.split(',')[0]
        if part != 'BOS/EOS' and part != '記号' and part != '助詞' and part != '助動詞' and part != '補助記号':
            word = kata_to_hira(node.feature.split(',')[6])

            a = db_session.query(Words).filter(Words.uuid==uuid, Words.vocabulary==word).first()
            if a:
                a.num += 1
                db_session.commit()
            else:
                w = Words(uuid=uuid, vocabulary=word, date=date, num=1)
                db_session.add(w)
                db_session.commit()

        node = node.next


    return 'succeed', 204

def kata_to_hira(strj):
    return "".join([chr(ord(ch) - 96) if ("ァ" <= ch <= "ヴ") else ch for ch in strj])


@app.route('/ranking')
def ranking():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401
    

    with open('responses/ranking.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())
    
    users = db_session.query(Words).filter(Words.uuid == uuid).order_by(desc(Words.num)).limit(3).all()
    for u in users:
        res["ranking"].append({"word":u.vocabulary, "num":u.num})
    
    return jsonify(res)


@app.route('/debug/show-db')
def show_db():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401


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
    
    now_unix_time = datetime.datetime.now().timestamp()
    if claims['exp'] < now_unix_time:
        print('Signature has expired')
        raise Expired()
    
    return claims['user_id']


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
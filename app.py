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

from api import Api

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
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.show_words(uuid)


@app.route('/word_num_list')
def get_word_num_list():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.word_num_list(uuid)


@app.route('/delete', methods=['POST'])
def delete_word():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.delete_word(uuid)


@app.route('/get-morphological/<string:text>')
def morphological_analysis(text):
    res = ""
    m = MeCab.Tagger('')
    node = m.parseToNode(text)
    while node:
        print(node.surface, node.feature, '\n')

        res += node.surface + "  " + node.feature.split(',')[0] + "____"
        node = node.next

    return jsonify({"res":res})


@app.route('/save-vocabulary', methods=['POST'])
def save_vocabulary():
    try:
        h = request.headers['Authorization']
        uuid = get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.save_vocabulary(uuid)


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
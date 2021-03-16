from flask import Flask, request, jsonify, json
import os
import json

from flask_cors import CORS, cross_origin

import MeCab

from models.models import Words
from models.database import db_session
import datetime


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['JSON_AS_ASCII'] = False


@app.route('/')
def deltee_config():
    return jsonify({"res" : "response"})


@app.route('/words')
def show_words():
    uuid = "uuid"
    with open('responses/words.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())

    return jsonify(res)



@app.route('/word_num_list')
def get_word_num_list():
    uuid = "uuid"
    with open('responses/word_num_list.json', mode='r', buffering=-1, encoding='utf-8') as f:
        res = json.loads(f.read())

    return jsonify(res)


@app.route('/delete', methods=['POST'])
def delete_word():
    f = request.get_data()
    form_data = json.loads(f.decode('utf-8'))
    word = form_data['word']
    uuid = "uuid"

    print(word, '\n', uuid, '\n\n')

    return '', 204


@app.route('/get-morphological/<string:text>')
def morphological_analysis(text):
    res = ""
    m = MeCab.Tagger('')
    node = m.parseToNode(text)
    while node:
        print(node.surface, node.feature.split(',')[0], '\n')
        res += node.surface + "  " + node.feature.split(',')[0] + "____"
        node = node.next

    return jsonify({"res":res})


@app.route('/save-vocabulary', methods=['POST'])
def save_vocabulary():
    f = request.get_data()
    form_data = json.loads(f.decode('utf-8'))
    text = form_data['text']
    uuid = "userIdentifer"

    m = MeCab.Tagger('')
    node = m.parseToNode(text)

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    
    while node:
        part = node.feature.split(',')[0]
        if part != 'BOS/EOS' and part != '記号' and part != '助詞' and part != '助動詞':
            word = node.feature.split(',')[6]

            if unique_vocabulary(uuid, word):
                w = Words(uuid=uuid, vocabulary=word, date=date)
                db_session.add(w)
                db_session.commit()

        node = node.next


    return 'succeed', 204


def unique_vocabulary(uuid, word):
    a = db_session.query(Words).filter(Words.uuid==uuid, Words.vocabulary==word).first()
    return a == None


@app.route('/debug/show-db')
def show_db():
    uuid = "userIdentifer"
    res = {"res" : []}
    
    a = db_session.query(Words).filter(Words.uuid==uuid).all()
    for m in a:
        res["res"].append({"uuid":m.uuid, "voca":m.vocabulary, "date":m.date})
        print("uuid:{}\nvoca:{}\ndate:{}\n".format(m.uuid, m.vocabulary, m.date))
    
    return jsonify(res)


if __name__ == '__main__':
    app.run()
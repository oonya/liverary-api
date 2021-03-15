from flask import Flask, request, jsonify, json
import os
import json

from flask_cors import CORS, cross_origin

import MeCab


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



if __name__ == '__main__':
    app.run()
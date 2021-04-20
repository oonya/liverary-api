from flask import Flask, request, jsonify, json
import json

from models.models import Words
from models.database import db_session
from sqlalchemy import desc
import datetime

import MeCab


class Api():
    def __init__(self):
        pass


    def show_words(uuid):
        with open('responses/words.json', mode='r', buffering=-1, encoding='utf-8') as f:
            res = json.loads(f.read())
        
        words = db_session.query(Words).filter(Words.uuid==uuid).all()

        dic_ary = []
        for w in words:
            dic_ary.append({"text":w.vocabulary, "date":w.date})

        res["words"] = sorted(dic_ary, key=lambda x:x['date'], reverse=True)

        return jsonify(res)
    

    def word_num_list(uuid):
        with open('responses/word_num_list.json', mode='r', buffering=-1, encoding='utf-8') as f:
            res = json.loads(f.read())

        a = db_session.query(Words).filter(Words.uuid==uuid).all()

        dic_ary = []
        for m in a:
            dic_ary = Api.inc_res(dic_ary, m)
        
        res['word_num_list'] = sorted(dic_ary, key=lambda x:x['month'])

        return jsonify(res)

    def inc_res(dic_array, word):
        for d in dic_array:
            if d["month"] == word.date[:7]:
                d["sum"] += 1
                return dic_array
        
        dic_array.append({"month":word.date[:7], "sum":1})
        return dic_array
    

    def delete_word(uuid):
        f = request.get_data()
        form_data = json.loads(f.decode('utf-8'))
        word = form_data['word']

        a = db_session.query(Words).filter(Words.uuid==uuid, Words.vocabulary==word).first()
        if a == None:
            raise Exception

        db_session.delete(a)
        db_session.commit()

        return '', 204
    
    def save_vocabulary(uuid):
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
                word = Api.kata_to_hira(node.feature.split(',')[6])

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
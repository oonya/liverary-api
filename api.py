from flask import Flask, request, jsonify, json
import json

from models.models import Words
from models.database import db_session
from sqlalchemy import desc
import datetime




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
    

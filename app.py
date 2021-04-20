from flask import Flask, request, jsonify, json

from flask_cors import CORS, cross_origin

from models.database import db_session
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
        uuid = Api.get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.show_words(uuid)


@app.route('/word_num_list')
def get_word_num_list():
    try:
        h = request.headers['Authorization']
        uuid = Api.get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.word_num_list(uuid)


@app.route('/delete', methods=['POST'])
def delete_word():
    try:
        h = request.headers['Authorization']
        uuid = Api.get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.delete_word(uuid)


@app.route('/save-vocabulary', methods=['POST'])
def save_vocabulary():
    try:
        h = request.headers['Authorization']
        uuid = Api.get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.save_vocabulary(uuid)


@app.route('/ranking')
def ranking():
    try:
        h = request.headers['Authorization']
        uuid = Api.get_user_id(h)
    except Expired:
        return 'Signature has expired', 401
    except Exception:
        return 'Unauthorized?', 401

    return Api.ranking(uuid)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
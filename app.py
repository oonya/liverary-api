from flask import Flask, request, jsonify, json
import os
import json

from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def deltee_config():
    return jsonify({"res" : "response"})




if __name__ == '__main__':
    app.run()
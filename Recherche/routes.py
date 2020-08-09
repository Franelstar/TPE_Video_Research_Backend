import string
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from flask_restful.utils.cors import crossdomain
import numpy as np
import cv2 as cv
import os
from werkzeug.utils import secure_filename
import random
import tensorflow as tf
import config


from .videoManager import *
from .model import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/foo": {"origins": config.URL}})

# app.config.from_object('config')

uploads_dir = '/var/www/API_TPE/Recherche/static/video'
models_dir = os.path.join(app.instance_path, 'models')
modelFilePath = os.path.join(models_dir, 'modelTPE2.h5')
model = tf.keras.models.load_model(modelFilePath)


@app.route('/')
def index():
    return "Hello wold !"


# route http posts to upload vidéo
@app.route('/api/upload', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def uploadVideo():
    if request.method == 'POST':
        video = request.files['file']
        extension = video.filename.split('.')
        sere = string.ascii_lowercase
        name_v = ''.join(random.choice(sere) for i in range(20))
        name = name_v + '.' + extension[len(extension) - 1]

        video.save(os.path.join(uploads_dir, secure_filename(name)))

        videoFileName = video.filename
        videoFilePath = os.path.join(uploads_dir, secure_filename(name))

        scene_list = get_scenes(videoFilePath)
        responder, data = save_video(title=videoFileName, file_name=videoFilePath, scene_list=scene_list, model=model,
                                     name_v=name_v)

        if not responder:
            os.remove(videoFilePath)

        # nparr = np.fromstring(r.data, np.uint8)
        # img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        # cv.imshow(img)

        response = jsonify(data)
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        # return request.json
        # print(r)

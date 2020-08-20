import string
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_restful.utils.cors import crossdomain
from werkzeug.utils import secure_filename
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input, decode_predictions

from .videoManager import *
from .sceneC import *
from .objetC import *
from .chercher import *
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/foo": {"origins": config.URL}})

# app.config.from_object('config')

models_dir = os.path.join(app.instance_path, 'models')
modelFilePath = os.path.join(models_dir, 'modelTPE2.h5')
model = tf.keras.models.load_model(modelFilePath)
model_inception_v3 = InceptionV3(include_top=True,
                                 weights='imagenet',
                                 input_tensor=None,
                                 input_shape=None,
                                 pooling=None,
                                 classes=1000)


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

        video.save(os.path.join(config.uploads_dir, secure_filename(name)))

        videoFileName = video.filename
        videoFilePath = os.path.join(config.uploads_dir, secure_filename(name))

        scene_list = get_scenes(videoFilePath)

        responder, data = save_video(title=videoFileName, file_name=videoFilePath, scene_list=scene_list, name_v=name_v,
                                     model=model, name=name)
        if responder:
            responder, data = save_objet(data=data, model=model_inception_v3,
                                         preprocess_input=preprocess_input, decode_predictions=decode_predictions)

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


# route http get pour recuperer les paramètres de recherche
@app.route('/api/home', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_Params():
    if request.method == 'GET':
        list_scenes = get_list_scene()
        list_objets = get_list_objets()
        response = jsonify({'scenes': list_scenes, 'objets': list_objets})
        return response


# route http get pour faire une recherche
@app.route('/api/search', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def get_search():
    if request.method == 'POST':
        image = request.files.get('file')
        scenes = request.values.get('scenes')
        objets = request.values.get('objets')
        print(image)
        if scenes:
            scenes = list(scenes.split('_'))
            if scenes[len(scenes)-1] == '':
                del(scenes[len(scenes)-1])
            print(scenes)

        if objets:
            objets = list(objets.split('_'))
            if objets[len(objets) - 1] == '':
                del (objets[len(objets) - 1])
            print(objets)

        if image:
            print('image existe')

        result = recherche(scenes=scenes, objets=objets)
        response = jsonify(result)
        return response

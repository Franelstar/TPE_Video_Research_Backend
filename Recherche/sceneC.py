import cv2 as cv
import random
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import config

from .model import *


def filtre(predictions_tempo):
    if len(predictions_tempo) == 1:
        return predictions_tempo[0]
    else:
        if predictions_tempo[0]['classe'] == predictions_tempo[1]['classe'] or predictions_tempo[0]['classe'] == \
                predictions_tempo[2]['classe']:
            return predictions_tempo[0]
        elif predictions_tempo[1]['classe'] == predictions_tempo[2]['classe']:
            return predictions_tempo[1]
        else:
            if predictions_tempo[0]['proba'] > predictions_tempo[1]['proba'] and predictions_tempo[0]['proba'] > \
                    predictions_tempo[2]['proba']:
                return predictions_tempo[0]
            elif predictions_tempo[1]['proba'] > predictions_tempo[2]['proba']:
                return predictions_tempo[1]
            else:
                return predictions_tempo[2]


def prediction(frame_choisi, cap, loaded_model, predictions_tempo, save=False, binaire=False):
    for j in range(len(frame_choisi)):
        cap.set(cv.CAP_PROP_POS_FRAMES, frame_choisi[j])
        res, frame = cap.read()
        if j == 0 and save:
            os.chdir(config.PATH_IMAGE_LONG)
            cv.imwrite(predictions_tempo[j]['image'], frame)
        frame = tf.image.resize(frame, [224, 224], method='nearest')
        X = image.img_to_array(frame)
        X = np.expand_dims(X, axis=0)
        images = np.vstack([X])
        images = images / 255
        if binaire:
            predictions_tempo[j]['classe'] = loaded_model.predict_classes(images)[0][0]
        else:
            predictions_tempo[j]['classe'] = loaded_model.predict_classes(images)[0]
        predictions_tempo[j]['proba'] = round(max(loaded_model.predict(images)[0]), 4)

    return filtre(predictions_tempo)


def save_video(title, file_name, scene_list, name_v, name, model0, model1_1, model1_2, model2_1, model2_2):
    cap = cv.VideoCapture(file_name)
    predictions = [{'classe': '', 'proba': 0.0, 'image': '', 'classe0': '', 'proba0': 0.0, 'classe1': '', 'proba1': 0.0}
                   for _ in range(len(scene_list))]
    for i, scene in enumerate(scene_list):
        debut = scene[0].get_frames()
        fin = scene[1].get_frames()
        if (fin - debut) > 4:
            frame_choisi = random.sample([i for i in range(debut, fin - 1)], 3)
        else:
            frame_choisi = [debut]

        # On crée limage
        name_image = name_v + str(i) + '.jpg'

        predictions_tempo = [{'classe': '', 'proba': 0, 'image': name_image} for i in range(len(frame_choisi))]

        # Classe 0
        result = prediction(frame_choisi, cap, model0, predictions_tempo, save=True, binaire=True)
        predictions[i]['classe0'] = result['classe']
        predictions[i]['proba0'] = result['proba']
        predictions[i]['image'] = result['image']

        # Classe 1
        if predictions[i]['proba0'] < 0.5:
            predictions[i]['classe0'] = 2  # Inconnu
            predictions[i]['classe'] = 19  # Inconnu
        else:
            if predictions[i]['classe0'] == 0:  # Extereur
                # Classe 1_1
                result = prediction(frame_choisi, cap, model1_1, predictions_tempo, binaire=False)
                predictions[i]['classe'] = result['classe']
                predictions[i]['proba'] = result['proba']
                if predictions[i]['proba'] < 0.5:
                    predictions[i]['classe'] = 19  # Inconnu
            else:  # Interier
                # Classe 1_2
                result = prediction(frame_choisi, cap, model1_2, predictions_tempo, binaire=True)
                predictions[i]['classe1'] = result['classe']
                predictions[i]['proba1'] = result['proba']
                if predictions[i]['classe1'] == 0:  # House
                    # Classe 2_1
                    result = prediction(frame_choisi, cap, model2_1, predictions_tempo, binaire=False)
                    predictions[i]['classe'] = result['classe'] + 7
                    predictions[i]['proba'] = result['proba']
                    if predictions[i]['proba'] < 0.5:
                        predictions[i]['classe'] = 19  # Inconnu
                else:  # No house
                    # Classe 2_2
                    result = prediction(frame_choisi, cap, model2_2, predictions_tempo, binaire=False)
                    predictions[i]['classe'] = result['classe'] + 13
                    predictions[i]['proba'] = result['proba']
                    if predictions[i]['proba'] < 0.5:
                        predictions[i]['classe'] = 19  # Inconnu

    return save_video_db(title, file_name, scene_list, predictions, name)


def get_list_scene():
    scenes = get_list_scene_db()
    result = {s[1]: s[0] for i, s in enumerate(scenes)}
    return result


def chercher_scene(scenes):
    scenes = get_scene(scenes)
    result = []
    path_image = config.URL + config.PATH_IMAGE_SHORT
    path_scene = config.URL + config.PATH_VIDEO_SCENE_SHORT
    path_video = config.URL + config.uploads_dir_SHORT
    for scene in scenes:
        one = {'id_scene': scene[0],
               'id_video': scene[1],
               'num_scene': scene[2],
               'duree_scene': scene[8],
               'type1': 'none',
               'type2': 'none',
               'proba_type1': scene[14],
               'proba_type2': scene[10],
               'image_url': path_image + scene[11],
               'scene_url': path_scene + scene[12],
               'video_url': path_video + scene[15].split('/')[-1],
               'nom_video': scene[16],
               'date_save': scene[17],
               'duree_video': scene[18].split('.')[0],
               'nom_type2': scene[19],
               'nom_type1': scene[20],
               'nbre_person': scene[21],
               'vue': False}
        result.append(one)

    return result


def prediction_image(frame, loaded_model, predictions_tempo, binaire=False):
    # frame = tf.image.resize(image, [224, 224], method='nearest')
    X = image.img_to_array(frame)
    X = np.expand_dims(X, axis=0)
    images = np.vstack([X])
    images = images / 255
    if binaire:
        predictions_tempo['classe'] = loaded_model.predict_classes(images)[0][0]
    else:
        predictions_tempo['classe'] = loaded_model.predict_classes(images)[0]
    predictions_tempo['proba'] = round(max(loaded_model.predict(images)[0]), 4)
    return predictions_tempo


def prediction_image_(image_path, model0, model1_1, model1_2, model2_1, model2_2):
    predictions = {'classe': '', 'proba': 0.0, 'image': '', 'classe0': '', 'proba0': 0.0, 'classe1': '', 'proba1': 0.0}
    predictions_tempo = {'classe': '', 'proba': 0, 'image': ''}
    frame = load_img(config.PATH_IMAGE_LONG + '/' + image_path, target_size=(224, 224))

    # Classe 0
    result = prediction_image(frame, model0, predictions_tempo, binaire=True)
    predictions['classe0'] = result['classe']
    predictions['proba0'] = result['proba']
    predictions['image'] = result['image']

    # Classe 1
    if predictions['proba0'] < 0.5:
        return []
    else:
        if predictions['classe0'] == 0:  # Extereur
            # Classe 1_1
            result = prediction_image(frame, model1_1, predictions_tempo, binaire=False)
            predictions['classe'] = result['classe']
            predictions['proba'] = result['proba']
            if predictions['proba'] < 0.5:
                return []
        else:  # Interier
            # Classe 1_2
            result = prediction_image(frame, model1_2, predictions_tempo, binaire=True)
            predictions['classe1'] = result['classe']
            predictions['proba1'] = result['proba']
            if predictions['classe1'] == 0:  # House
                # Classe 2_1
                result = prediction_image(frame, model2_1, predictions_tempo, binaire=False)
                predictions['classe'] = result['classe'] + 7
                predictions['proba'] = result['proba']
                if predictions['proba'] < 0.5:
                    return []
            else:  # No house
                # Classe 2_2
                result = prediction_image(frame, model2_2, predictions_tempo, binaire=False)
                predictions['classe'] = result['classe'] + 13
                predictions['proba'] = result['proba']
                if predictions['proba'] < 0.5:
                    return []

    return [str(predictions['classe'])]

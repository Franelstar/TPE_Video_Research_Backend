import cv2 as cv
import random
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import config

from .model import *


def prediction(frame_choisi, cap, loaded_model, predictions_tempo):
    for j in range(len(frame_choisi)):
        cap.set(cv.CAP_PROP_POS_FRAMES, frame_choisi[j])
        res, frame = cap.read()
        if j == 0:
            os.chdir(config.PATH_IMAGE_LONG)
            cv.imwrite(predictions_tempo[j]['image'], frame)
        frame = tf.image.resize(frame, [224, 224], method='nearest')
        X = image.img_to_array(frame)
        X = np.expand_dims(X, axis=0)
        images = np.vstack([X])
        images = images / 255
        predictions_tempo[j]['classe'] = loaded_model.predict_classes(images)[0]
        predictions_tempo[j]['proba'] = round(max(loaded_model.predict(images)[0]), 4)

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


def save_video(title, file_name, scene_list, model, name_v, name):
    cap = cv.VideoCapture(file_name)
    predictions = [{'classe': '', 'proba': 0, 'image': ''} for i in range(len(scene_list))]
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

        predictions[i] = prediction(frame_choisi, cap, model, predictions_tempo)

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
               'proba_type1': 'none',
               'proba_type2': scene[10],
               'image_url': path_image + scene[11],
               'scene_url': path_scene + scene[12],
               'video_url': path_video + scene[13].split('/')[-1],
               'nom_video': scene[14],
               'date_save': scene[15],
               'duree_video': scene[16].split('.')[0],
               'nom_type2': scene[17],
               'vue': False}
        result.append(one)

    return result

import psycopg2
import cv2 as cv
import random
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import datetime
import time
import os
import config

# pip install psycopg2-binary

con = psycopg2.connect(
    host=config.DB_HOST,
    database=config.DB_DATABASE,
    user=config.DB_USER,
    password=config.DB_PASSWORD, )

cur = con.cursor()


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
        predictions_tempo[j]['proba'] = max(loaded_model.predict(images)[0])

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


def save_video(title, file_name, scene_list, model, name_v):
    try:
        cur.execute('SELECT * FROM lieux_scene WHERE etat_lieux_scene = true')
        targets = cur.fetchall()
        path_image = config.URL+config.PATH_IMAGE_SHORT

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

        _, scene = enumerate(scene_list[len(scene_list) - 1])
        frame_number = scene[1].get_frames()
        time_str = scene[1].get_timecode()
        x = time.strptime(time_str.split('.')[0], '%H:%M:%S')
        seconde = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

        cur.execute(
            "SELECT * FROM video WHERE titre = '{}' and duree = '{}' and nbre_frame = '{}' and duree_str = '{}'".format(
                title, int(seconde), frame_number, time_str))
        rows = cur.fetchall()
        if not rows:
            query = "INSERT INTO "
            query += "video(titre, duree, nbre_frame, etat_video, video_file, duree_str) "
            query += "VALUES ('{}', '{}', '{}', '1', '{}', '{}')".format(
                title, int(seconde), frame_number, file_name, time_str)
            cur.execute(query)

            query = "SELECT * FROM video "
            query += "WHERE titre = '{}' and duree = '{}' and nbre_frame = '{}' ".format(title, int(seconde), frame_number)
            query += "and video_file = '{}' and duree_str = '{}'".format(file_name, time_str)
            cur.execute(query)

            rows = cur.fetchall()
            result_scenes = []
            if not rows:
                return False, [{'Erreur': 'Une erreur s\'est produite, veillez contacter l\'administrateur'}]
            else:
                id_video = rows[0][0]
                for i in range(len(predictions)):
                    debut, fin = enumerate(scene_list[i])
                    x_debut = time.strptime(debut[1].get_timecode().split('.')[0], '%H:%M:%S')
                    x_fin = time.strptime(fin[1].get_timecode().split('.')[0], '%H:%M:%S')
                    debut_time = datetime.timedelta(hours=x_debut.tm_hour, minutes=x_debut.tm_min,
                                                    seconds=x_debut.tm_sec).total_seconds()
                    fin_time = datetime.timedelta(hours=x_fin.tm_hour, minutes=x_fin.tm_min,
                                                   seconds=x_fin.tm_sec).total_seconds()

                    query = "INSERT INTO "
                    query += "scene(id_video, num_scene, frame_debut, frame_fin, nbre_frame, "
                    query += "start_time, end_time, duree, lieu_pos, proba, image) "
                    query += "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                        id_video, i + 1, int(debut[1].get_frames()), int(fin[1].get_frames()),
                                  int(fin[1].get_frames()) - int(debut[1].get_frames()), int(debut_time),
                        int(fin_time), int(fin_time) - int(debut_time), predictions[i]['classe'],
                        predictions[i]['proba'], predictions[i]['image'])

                    cur.execute(query)

                    template = {'num': str(i+1), 'image': path_image + predictions[i]['image'],
                                'nbre_frame': str(int(fin[1].get_frames()) - int(debut[1].get_frames())),
                                'duree': str(int(fin_time) - int(debut_time)),
                                'scene_lieu': str(targets[predictions[i]['classe']][1]),
                                'proba': str(predictions[i]['proba'])}

                    result_scenes.append(template)

            con.commit()
            result = [{'video': {'titre': title, 'duree': int(seconde), 'duree_str': time_str,
                                 'nbre_scene': len(predictions), 'nbre_frame': frame_number,
                                 'Success': 'Sauvegarde réussie'},
                       'scenes': [{i:   result_scenes[i]} for i in range(len(result_scenes))]}]
            return True, result
        else:
            return False, [{'Erreur': 'La vidéo que vous voulez enrégistrer existe déjà dans le système'}]

    except:
        con.rollback()

# cur.close()
# con.close()

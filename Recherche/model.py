import psycopg2
import datetime
import time
import config
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# pip install psycopg2-binary

con = psycopg2.connect(
    host=config.DB_HOST,
    database=config.DB_DATABASE,
    user=config.DB_USER,
    password=config.DB_PASSWORD)

cur = con.cursor()


def save_video_db(title, file_name, scene_list, predictions, name_v):
    try:
        cur.execute('SELECT * FROM lieux_scene WHERE etat_lieux_scene = true')
        targets = cur.fetchall()
        path_image = config.URL + config.PATH_IMAGE_SHORT

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
            query += "WHERE titre = '{}' and duree = '{}' and nbre_frame = '{}' ".format(title, int(seconde),
                                                                                         frame_number)
            query += "and video_file = '{}' and duree_str = '{}'".format(file_name, time_str)
            cur.execute(query)

            rows = cur.fetchall()
            result_scenes = []
            if not rows:
                return False, [{'Erreur': 'An error has occurred, please contact the administrator'}]
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

                    print('___________________________________________________________')
                    print(name_v)
                    ffmpeg_extract_subclip(file_name, int(debut_time), int(fin_time),
                                           targetname=config.PATH_VIDEO_SCENE + '/' + str(i) + name_v)

                    query = "INSERT INTO "
                    query += "scene(id_video, num_scene, frame_debut, frame_fin, nbre_frame, "
                    query += "start_time, end_time, duree, lieu_pos, proba, image, url) "
                    query += "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                        id_video, i + 1, int(debut[1].get_frames()), int(fin[1].get_frames()),
                                  int(fin[1].get_frames()) - int(debut[1].get_frames()), int(debut_time),
                        int(fin_time), int(fin_time) - int(debut_time), predictions[i]['classe'],
                        predictions[i]['proba'], predictions[i]['image'], str(i) + name_v)

                    cur.execute(query)

                    query = "SELECT id_scene FROM scene "
                    query += "WHERE id_video = '{}' and num_scene = '{}'".format(id_video, i + 1)
                    cur.execute(query)
                    id_scene = cur.fetchall()

                    template = {'num': str(i + 1), 'image': path_image + predictions[i]['image'],
                                'image_court': predictions[i]['image'],
                                'nbre_frame': str(int(fin[1].get_frames()) - int(debut[1].get_frames())),
                                'duree': str(int(fin_time) - int(debut_time)),
                                'scene_lieu': str(targets[predictions[i]['classe']][1]),
                                'proba': str(predictions[i]['proba']),
                                'id': '{}'.format(id_scene[0][0])}

                    result_scenes.append(template)

            con.commit()
            result = [{'video': {'titre': title, 'duree': int(seconde), 'duree_str': time_str,
                                 'nbre_scene': len(predictions), 'nbre_frame': frame_number,
                                 'Success': 'Saved successfully'},
                       'scenes': [{i: result_scenes[i]} for i in range(len(result_scenes))]}]
            return True, result
        else:
            return False, [{'Erreur': 'The video you want to record already exists in the system'}]

    except:
        con.rollback()


def save_objets_db(data):
    try:
        for i, scene in enumerate(data[0]['scenes']):
            id_scene = scene.get(i)['id']
            for j, obj in enumerate(scene.get(i)['liste_objets']):
                query = "INSERT INTO "
                query += "objets_scene(id_scene, id_objet, proba) "
                query += "VALUES ('{}', '{}', '{}')".format(id_scene, obj['id_objet'], float(obj['proba']))
                cur.execute(query)
                con.commit()
        return True
    except:
        con.rollback()


def get_list_scene_db():
    query = "SELECT l_s.nom, l_s.num_target FROM lieux_scene as l_s, scene as sc "
    query += "WHERE sc.lieu_pos = l_s.num_target GROUP BY l_s.id_lieux_scene"
    cur.execute(query)

    rows = cur.fetchall()
    return rows


def get_list_objets_db():
    query = "SELECT ob.name, ob.id FROM objets as ob, objets_scene as o_s "
    query += "WHERE o_s.id_objet = ob.id GROUP BY ob.id"
    cur.execute(query)

    rows = cur.fetchall()
    return rows


def get_scene(scenes):
    query = "SELECT sc.*, (SELECT vd.video_file FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.titre FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.save_date FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.duree_str FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT l_s.nom FROM lieux_scene as l_s WHERE sc.lieu_pos = l_s.num_target) "
    query += "FROM scene as sc "
    query += "WHERE "
    compteur = 0
    for scene in scenes:
        if compteur == 0:
            query += "sc.lieu_pos = '" + scene + "'"
        else:
            query += " OR sc.lieu_pos = '" + scene + "'"
        compteur += 1
    query += " GROUP BY sc.id_scene"
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def get_objets(objets):
    query = "SELECT sc.*, (SELECT vd.video_file FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.titre FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.save_date FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT vd.duree_str FROM video as vd WHERE sc.id_video = vd.id_video), "
    query += "(SELECT l_s.nom FROM lieux_scene as l_s WHERE sc.lieu_pos = l_s.num_target) "
    query += "FROM scene as sc, objets_scene as s_o "
    query += "WHERE sc.id_scene = s_o.id_scene AND ("
    compteur = 0
    for obj in objets:
        if compteur == 0:
            query += "s_o.id_objet = '" + obj + "'"
        else:
            query += " OR s_o.id_objet = '" + obj + "'"
        compteur += 1
    query += ") GROUP BY sc.id_scene"
    cur.execute(query)
    rows = cur.fetchall()

    query = "SELECT s_o.*, (SELECT ob.name FROM objets as ob WHERE s_o.id_objet = ob.id) "
    query += "FROM objets_scene as s_o "
    query += "WHERE "
    compteur = 0
    for obj in objets:
        if compteur == 0:
            query += "s_o.id_objet = '" + obj + "'"
        else:
            query += " OR s_o.id_objet = '" + obj + "'"
        compteur += 1
    cur.execute(query)
    rows2 = cur.fetchall()

    return rows, rows2

# cur.close()
# con.close()

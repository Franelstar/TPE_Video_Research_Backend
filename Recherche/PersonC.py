import config
import numpy as np
from .model import *
from .recognition import *


def save_person(data):
    for i, scene in enumerate(data[0]['scenes']):
        image_path = config.PATH_IMAGE_LONG + '/' + scene.get(i)['image_court']
        liste_visage = chercherVisages(image_path)
        scene.get(i)['nbre_person'] = len(liste_visage)
        id_scene = scene.get(i)['id']
        for visage in liste_visage:
            descripteur = ''
            for des in visage:
                descripteur += str(des) + ' '
            retro, id_visage = cherche_visage(visage)
            if retro:
                save_person_scene_db(id_visage, id_scene)
            else:
                id_visage = save_person_db(descripteur)
                save_person_scene_db(id_visage, id_scene)

    return True, data


def cherche_visage(visage):
    visage_DB = get_visageDB()
    if visage_DB:
        visages_connus = []
        for visag in visage_DB:
            face_encode = reconstruire_descripteur(visag[1])
            visages_connus.append(face_encode)
        retro, index = sameVisage(visages_connus, [visage])
        if retro:
            return True, visage_DB[index][0]
    return False, 0


def reconstruire_descripteur(visage):
    desc = visage.split(' ')
    return np.array([float(desc[i]) for i in range(128)])


def find_person(path_image):
    image_path = config.PATH_IMAGE_LONG + '/' + path_image
    visages = chercherVisages(image_path)
    liste_scene = []
    for visage in visages:
        retro, id_visage = cherche_visage(visage)
        if retro:
            list_scenes = get_visage_sceneDB(id_visage)
            id_scenes = [str(sc[0]) for sc in list_scenes]

            scene_db, liste = get_scene_by_id(id_scenes)
            path_image = config.URL + config.PATH_IMAGE_SHORT
            path_scene = config.URL + config.PATH_VIDEO_SCENE_SHORT
            path_video = config.URL + config.uploads_dir_SHORT
            for scene in scene_db:
                objs = []
                for l in liste:
                    if l[0] == scene[0]:
                        o = {'id_objet': l[1], 'proba': l[2], 'nom_objet': l[3].split(',')[0]}
                        objs.append(o)

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
                       'nbre_objet': len(objs),
                       'liste_objets': objs,
                       'vue': False}
                liste_scene.append(one)

    return liste_scene



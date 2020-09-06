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
            liste_scene.append(str(get_visage_sceneDB(id_visage)))
    return liste_scene



from nltk.tokenize import word_tokenize
import string
from math import *
from .sceneC import chercher_scene, prediction_image_
from .objetC import chercher_objet, extraire_objet_image
from .PersonC import find_person
from .model import get_all_lieux_scene, get_all_objet_scene
import config


def recherche(scenes, objets, page, image_name=""):
    global scene_scene
    global scene_objet
    global scene_person
    scene_person = []
    if image_name != "":
        scene_person = find_person(image_name)
    if scenes:
        scenes += scene_person
        scene_scene = chercher_scene(scenes)
    if objets:
        scene_objet = chercher_objet(objets)

    liste_des_scenes = []

    if not scenes and not objets:
        return []
    if not scenes:
        liste_des_scenes = sorted(scene_objet, key=lambda x: len(x['liste_objets']), reverse=True)
    if not objets:
        liste_des_scenes = scene_scene
    if scenes and objets:
        liste_des_scenes = sorted(scene_objet, key=lambda x: len(x['liste_objets']), reverse=True)
        for l1 in scene_scene:
            trouve = False
            for l2 in liste_des_scenes:
                if l1['id_scene'] == l2['id_scene']:
                    trouve = True
            if not trouve:
                liste_des_scenes.append(l1)

    data = {}
    debut = config.PAR_PAGE * (page - 1)
    fin = config.PAR_PAGE * page
    data['data'] = liste_des_scenes[debut:fin]
    data['current'] = page
    data['next'] = {'active': len(liste_des_scenes) > fin, 'page': page+1}
    data['preview'] = {'active': page > 1, 'page': page - 1}
    data['list_page'] = [{'page': i+1, 'active': i+1 == page}
                         for i in range(ceil(len(liste_des_scenes) / config.PAR_PAGE))]
    data['resultat_total'] = len(liste_des_scenes)

    return data


def get_scene_image(path_image, model0, model1_1, model1_2, model2_1, model2_2):
    return prediction_image_(path_image, model0, model1_1, model1_2, model2_1, model2_2)


def get_objet_image(path_image, model, preprocess_input, decode_predictions):
    result = extraire_objet_image(path_image, model, preprocess_input, decode_predictions)
    liste = []
    for r in result:
        liste.append(r[0])
    return liste


def recherche_texte(text, page):
    if text == "":
        return []
    punctuations = list(string.punctuation)
    words = [i.lower() for i in word_tokenize(text) if i not in punctuations]
    if not words:
        return []

    objets = []
    scenes = []

    lieux_scene = get_all_lieux_scene()
    if lieux_scene:
        for l_s in lieux_scene:
            lieu = [i.lower() for i in word_tokenize(l_s[1]) if i not in punctuations]
            for li in lieu:
                if li in words and str(l_s[2]) not in scenes:
                    scenes.append(str(l_s[2]))

    objets_scene = get_all_objet_scene()
    if objets_scene:
        for o_s in objets_scene:
            objs = [i.lower() for i in word_tokenize(o_s[1]) if i not in punctuations]
            for ob in objs:
                if ob in words and str(o_s[0]) not in objets:
                    objets.append(str(o_s[0]))

    return recherche(scenes, objets, page=page)

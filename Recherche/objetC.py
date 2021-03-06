from tensorflow.keras.preprocessing.image import load_img, img_to_array
import cv2 as cv
import config
from Recherche.model import save_objets_db, get_list_objets_db, get_objets


def extraire_objet(image_path, model, preprocess_input, decode_predictions):
    image = load_img(image_path, target_size=(299, 299))
    image = img_to_array(image)  # output Numpy-array
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    yhat = model.predict(image)
    label = decode_predictions(yhat, top=1000)
    label = label[0][:]
    list_objet = []
    for obj in label:
        if obj[2] > 0.75:
            list_objet.append(obj)
    return list_objet


def save_objet(data, model, preprocess_input, decode_predictions):
    for i, scene in enumerate(data[0]['scenes']):
        image = scene.get(i)['image_court']
        objet = extraire_objet(config.PATH_IMAGE_LONG + '/' + image, model, preprocess_input, decode_predictions)
        scene.get(i)['liste_objets'] = []
        for j in range(len(objet)):
            scene.get(i)['liste_objets'].append({'id_objet': objet[j][0], 'nom_objet': objet[j][1],
                                                 'proba': str(round(objet[j][2], 4))})

    return save_objets_db(data), data


def get_list_objets():
    objets = get_list_objets_db()
    result = {s[1]: s[0].split(',')[0] for i, s in enumerate(objets)}
    return result


def chercher_objet(objets):
    objets, liste = get_objets(objets)
    result = []
    path_image = config.URL + config.PATH_IMAGE_SHORT
    path_scene = config.URL + config.PATH_VIDEO_SCENE_SHORT
    path_video = config.URL + config.uploads_dir_SHORT
    for scene in objets:
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
        result.append(one)

    return result


def extraire_objet_image(image_path, model, preprocess_input, decode_predictions):
    image = load_img(config.PATH_IMAGE_LONG+'/'+image_path, target_size=(299, 299))
    image = img_to_array(image)  # output Numpy-array
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    yhat = model.predict(image)
    label = decode_predictions(yhat, top=1000)
    label = label[0][:]
    list_objet = []
    for obj in label:
        if obj[2] > 0.50:
            list_objet.append(obj)
    return list_objet

from .sceneC import chercher_scene
from .objetC import chercher_objet


def recherche(scenes, objets, image=None):
    global scene_scene
    global scene_objet
    if scenes:
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


    print(liste_des_scenes)
    return liste_des_scenes

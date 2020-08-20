from .sceneC import chercher_scene
from .objetC import chercher_objet


def recherche(scenes, objets, image=None):
    global scene_scene
    global scene_objet
    if scenes:
        scene_scene = chercher_scene(scenes)
    if objets:
        scene_objet = chercher_objet(objets)

    print(scene_scene)
    liste_des_scenes = scene_scene
    return liste_des_scenes

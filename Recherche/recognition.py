import face_recognition_models
import dlib
import face_recognition
# cmake, dlib, sudo apt-get install libopenblas-dev liblapack-dev
import matplotlib.pyplot
from PIL import Image, ImageDraw


def chercherVisages(image_path):
    image = face_recognition.load_image_file(image_path)
    visage_location = face_recognition.face_locations(image)
    visage_encode = face_recognition.face_encodings(image, visage_location)
    # retourne un tableau contenant
    return visage_encode


def sameVisage(visagesDb, visage_encode):
    if visagesDb:
        for visage_encod in visage_encode:
            matches = face_recognition.compare_faces(visagesDb, visage_encod)
            # s'il ya correspondance
            if True in matches:
                first_match_index = matches.index(True)
                return True, first_match_index
    return False, 0

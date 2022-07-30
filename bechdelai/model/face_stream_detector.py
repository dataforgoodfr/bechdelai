import cv2
from retinaface import RetinaFace

def deep_recognition(frame):

    faces = RetinaFace.detect_faces(frame)

    if type(faces) is dict:
        for face in faces:
            identity = faces[face]
            facial_area = identity["facial_area"]
            frame = cv2.rectangle(frame, (facial_area[2], facial_area[3]), (facial_area[0], facial_area[1]), (255, 255, 255), 1)
        return frame
    else:
        return frame
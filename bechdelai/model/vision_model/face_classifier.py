from deepface import DeepFace

class DeepFaceBech:

    def __init__(self, caracteristique:list, force_pred = False) -> None:
        self.caracteristique = caracteristique
        self.force_pred = force_pred

    def make_pred(self, faces):
        return DeepFace.analyze(faces, actions = self.caracteristique, enforce_detection = self.force_pred)
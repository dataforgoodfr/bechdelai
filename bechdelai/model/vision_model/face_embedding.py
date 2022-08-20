import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from tqdm.auto import tqdm

# DeepFace
from deepface.basemodels import VGGFace
from deepface.commons import functions
from deepface import DeepFace


# https://github.com/serengil/deepface/blob/master/tests/face-recognition-how.py


class FaceEmbedding:
    
    def __init__(self, embedding_model = VGGFace):
        self.model = embedding_model.loadModel()
        self.input_shape = self.model.layers[0].input_shape[0][1:3]

    def _make_array_dataset(self, faces:list, enforce_detection = False):
        faces_array = []
        for face in faces:
            face_array = functions.preprocess_face(face, self.input_shape, enforce_detection = enforce_detection)
            faces_array.append(face_array)
        faces_array = np.concatenate(faces_array,axis = 0)
        return faces_array


    def make_embeddings(self, faces):
        faces_array = self._make_array_dataset(faces)
        embeddings = self.model.predict(faces_array)
        return embeddings


class PostProcessEmbedding:

    def __init__(self, reduce_vector:int) -> None:
        self.reduce_vector = reduce_vector

    def reduce_embeddings(self,embeddings,**kwargs):
        self.reducer = UMAP(n_components = self.reduce_vector,**kwargs)
        embeddings = self.reducer.fit_transform(embeddings)

        return embeddings

    def match_array(self,array,db_path,enforce_detection = False):

        # Find best match in the database using DeepFace face id
        best_match = DeepFace.find(array,db_path = db_path,enforce_detection = enforce_detection)
        parse_path = lambda x : x.split("\\")[1].split("/")[0]
        best_match["character"] = best_match["identity"].map(parse_path) 

        # Take first result with the lowest cosine distance
        best_match = best_match.iloc[0:1]

        return best_match

    def cluster_embeddings(self,embeddings,method = "dbscan",**kwargs):

        self.clustering_model = DBSCAN(**kwargs)
        clusters = self.clustering_model.fit_predict(embeddings)
        embeddings["cluster"] = clusters
        return embeddings,clusters

    def match_faces(self,faces,db_path,enforce_detection = False):

        data = []
        for i,face in enumerate(tqdm(faces)):

            best_match = self.match_array(face.array,db_path,enforce_detection = enforce_detection)
            best_match["frame_id"] = i
            data.append(best_match)

        data = pd.concat(data,ignore_index = True,axis = 0)
        return data
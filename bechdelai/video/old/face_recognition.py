import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.cluster import DBSCAN
from umap import UMAP
from tqdm.auto import tqdm
from PIL import Image

# DeepFace
from deepface.basemodels import VGGFace, OpenFace, Facenet, FbDeepFace
from deepface.commons import functions
from deepface.detectors import FaceDetector
from deepface import DeepFace


# https://github.com/serengil/deepface/blob/master/tests/face-recognition-how.py


class FaceAnalyzer:
    def __init__(self):
        pass


    def load_vgg_model(self):
        self.model = VGGFace.loadModel()
        self.input_shape = self.model.layers[0].input_shape[0][1:3]

    def make_array_dataset(self,faces,enforce_detection = False):
        faces_array = []
        for face in faces:
            face_array = functions.preprocess_face(face.array,self.input_shape,enforce_detection = enforce_detection)
            faces_array.append(face_array)
        faces_array = np.concatenate(faces_array,axis = 0)
        return faces_array


    def make_embeddings(self,faces_array):
        embeddings = self.model.predict(faces_array)
        return embeddings


    def reduce_embeddings(self,embeddings,n_components = 2,**kwargs):
        self.reducer = UMAP(n_components = n_components,**kwargs)
        embeddings = self.reducer.fit_transform(embeddings)
        embeddings = pd.DataFrame(embeddings,columns = ["x","y"])
        return embeddings


    def cluster_embeddings(self,embeddings,method = "dbscan",**kwargs):

        self.clustering_model = DBSCAN(**kwargs)
        clusters = self.clustering_model.fit_predict(embeddings)
        embeddings["cluster"] = clusters
        embeddings["cluster"] = embeddings["cluster"].astype(str)
        return embeddings,clusters


    def show_embeddings2D(self,embeddings2D,faces = None,size = 0.5,opacity = 0.8):

        # Plot scatter plot

        if "cluster" in embeddings2D.columns:
            fig = px.scatter(
                embeddings2D.assign(size = lambda x : 20),
                x="x",
                y="y",
                color="cluster",
                size = "size"
            )
        else:
            fig = px.scatter(
                embeddings2D,
                x="x",
                y="y",
            )

        # Add faces
        if faces is not None:

            for i, face in enumerate(faces):
                row = embeddings2D.iloc[i]
                fig.add_layout_image(
                    dict(
                        source=face.img,
                        xref="x",
                        yref="y",
                        xanchor="center",
                        yanchor="middle",
                        x=row["x"],
                        y=row["y"],
                        sizex = size,
                        sizey = size,
            #             sizex=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
            #             sizey=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
                        sizing="contain",
                        opacity=opacity,
                        # layer="above"
                    )
                )

            # fig.update_layout(height=600, width=1000,, plot_bgcolor="#dfdfdf")

        return fig

    def load_detector(self,name = "retinaface"):
        # https://github.com/serengil/deepface/issues/310
        # name is ssd, mtcnn, dlib, retinaface
        self.detector = FaceDetector.build_model(name)


    def match_array(self,array,db_path,enforce_detection = False):

        # Find best match in the database using DeepFace face id
        best_match = DeepFace.find(array,db_path = db_path,enforce_detection = enforce_detection)
        parse_path = lambda x : x.split("\\")[1].split("/")[0]
        best_match["character"] = best_match["identity"].map(parse_path) 

        # Take first result with the lowest cosine distance
        best_match = best_match.iloc[0:1]

        return best_match


    def match_faces(self,faces,db_path,enforce_detection = False):

        data = []

        for i,face in enumerate(tqdm(faces)):

            best_match = self.match_array(face.array,db_path,enforce_detection = enforce_detection)
            best_match["frame_id"] = i
            data.append(best_match)

        data = pd.concat(data,ignore_index = True,axis = 0)
        return data


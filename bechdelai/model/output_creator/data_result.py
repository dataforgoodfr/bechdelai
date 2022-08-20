import os
import json
from uuid import uuid4
import numpy as np

DICO_DOMINANCE_MEDIUM = {"age": "age", 
    "gender": "gender", 
    "emotion": "dominant_emotion", 
    "race":"dominant_race"
}


class Result_Face_Creator:

    def __init__(self, output_dir = "output") -> None:
        self.output_dir = output_dir
        self._create_archi()

    def _create_archi(self):

        """
        Permet de créer une certaine architecture pour placer les fichiers
        """

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        if not os.path.exists(os.path.join(self.output_dir, "face_output")):
            os.makedirs(os.path.join(self.output_dir, "face_output"))
            os.makedirs(os.path.join(self.output_dir,"face_output","data"))
            os.makedirs(os.path.join(self.output_dir,"face_output","visualisation"))

        self.output_dir_data = os.path.join(self.output_dir,"face_output","data")
        self.output_dir_viz = os.path.join(self.output_dir,"face_output","visualisation")

    def _create_optional_archi(self):
        if not os.path.exists(os.path.join(self.output_dir,"face_output","embedding")):
            os.makedirs(os.path.join(self.output_dir,"face_output","embedding"))

    def _write_dict(self, dico:dict, num_batch:int):

        """
        Only to create JSON
        """

        # Serializing json
        json_object = json.dumps(dico, indent=4)
        
        # Writing to sample.json
        with open(os.path.join(self.output_dir_data, str(num_batch) + ".json"), "w") as outfile:
            outfile.write(json_object)

    def _specifier(self, dico:dict):
        simplify={}
        for i in dico:
            if i in DICO_DOMINANCE_MEDIUM:
                simplify[i]=dico[DICO_DOMINANCE_MEDIUM[i]]
        return simplify

    def write_minimal_batch_res(self, result:list, numero_batch:int):
        dict_batch = {}
        for num_im in range(len(result)):

            dict_batch[num_im]={}
            perso=0
            
            for (x,y,w,h) in result[num_im]:
                dict_batch[num_im][perso] = {
                    "X_Origin":int(x),
                    "Y_Origin":int(y),
                    "Width":int(w),
                    "Height":int(h),
                }
                perso+=1

        self._write_dict(dict_batch, numero_batch)

    def write_medium_batch_res(self, result:list, numero_batch:int, dominant=True):
        
        self._create_optional_archi()
        dict_batch = {}
        for num_im in range(len(result)):
            dict_batch["Image " + str(num_im)]={}
            perso=0
            for (x,y,w,h), spec, emb in zip(result[num_im][0], result[num_im][1], result[num_im][2]):              
                id_embedding = str(uuid4())  
                dict_batch["Image " + str(num_im)]["Face " + str(perso)] = {
                    "X_Origin":int(x),
                    "Y_Origin":int(y),
                    "Width":int(w),
                    "Height":int(h),
                    "Specification":self._specifier(result[num_im][1][spec]) if dominant else result[num_im][1][spec],
                    "Embedding": os.path.join(self.output_dir,"face_output","embedding", id_embedding, ".npy")
                }
                np.save(os.path.join(self.output_dir,"face_output","embedding", id_embedding + ".npy"), emb)
                perso+=1

        self._write_dict(dict_batch, numero_batch)


    def write_large_batch_res(self, result:list, numero_batch:int, dominant=True):
        
        self._create_optional_archi()
        dict_batch = {}
        for num_im in range(len(result)):
            dict_batch["Image " + str(num_im)]={}
            perso=0
            for (x,y,w,h), spec, emb in zip(result[num_im][0], result[num_im][1], result[num_im][2]):              
                id_embedding = str(uuid4())  
                dict_batch["Image " + str(num_im)]["Face " + str(perso)] = {
                    "X_Origin":int(x),
                    "Y_Origin":int(y),
                    "Width":int(w),
                    "Height":int(h),
                    "Specification":self._specifier(result[num_im][1][spec]) if dominant else result[num_im][1][spec],
                    "Embedding": os.path.join(self.output_dir,"face_output","embedding", id_embedding, ".npy"),
                }
                np.save(os.path.join(self.output_dir,"face_output","embedding", id_embedding + ".npy"), emb)
                perso+=1
            dict_batch["Image " + str(num_im)]["Action"] = result[num_im][3]

        self._write_dict(dict_batch, numero_batch)
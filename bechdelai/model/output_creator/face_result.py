import os
import numpy as np
import json

class Result_Face_Creator:

    def __init__(self, output_dir = "output") -> None:
        self.output_dir = output_dir
        self._create_archi()

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        if not os.path.exists(os.path.join(self.output_dir, "face_output")):
            os.makedirs(os.path.join(self.output_dir, "face_output"))
            os.makedirs(os.path.join(self.output_dir,"face_output","data"))
            os.makedirs(os.path.join(self.output_dir,"face_output","visualisation"))

        self.output_dir_data = os.path.join(self.output_dir,"face_output","data")
        self.output_dir_viz = os.path.join(self.output_dir,"face_output","visualisation")

    def write_minimal_batch_res(self, result:tuple, numero_batch:int, best=True):
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

        # Serializing json
        json_object = json.dumps(dict_batch, indent=4)
        
        # Writing to sample.json
        with open(os.path.join(self.output_dir_data, str(numero_batch) + ".json"), "w") as outfile:
            outfile.write(json_object)

    def show_examples_pred(self):
        pass

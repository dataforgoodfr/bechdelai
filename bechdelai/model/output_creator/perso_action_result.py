import os
import numpy as np
import json

class Result_Action_Creator:

    def __init__(self, output_dir = "output") -> None:
        self.output_dir = output_dir
        self._create_archi()

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        if not os.path.exists(os.path.join(self.output_dir, "action_output")):
            os.makedirs(os.path.join(self.output_dir, "action_output"))
            os.makedirs(os.path.join(self.output_dir,"action_output","data"))
            os.makedirs(os.path.join(self.output_dir,"action_output","visualisation"))

        self.output_dir_data = os.path.join(self.output_dir,"action_output","data")
        self.output_dir_viz = os.path.join(self.output_dir,"action_output","visualisation")

    def write_batch_res(self, result:tuple, label:list, numero_batch:int, best=True):
        numimg = 0
        dict_batch = {}
        if best:
            for pred, prob in zip(result[0].detach().numpy(), result[1].detach().numpy()):
                idx = np.argmax(prob)
                dict_batch[numimg] = {
                    "NumImg":numimg,
                    "Label":label[idx],
                    "Proba":str(prob[idx]),
                    "Proximity":str(pred[idx]),
                }
                numimg+=1

            # Serializing json
            json_object = json.dumps(dict_batch, indent=4)
            
            # Writing to sample.json
            with open(os.path.join(self.output_dir_data, str(numero_batch) + ".json"), "w") as outfile:
                outfile.write(json_object)

    def show_examples_pred(self):
        pass

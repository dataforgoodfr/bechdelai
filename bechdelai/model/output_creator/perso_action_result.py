import os
import numpy as np
import json

class Result_Creator:

    def __init__(self, output_dir = "output") -> None:
        self.output_dir = output_dir
        self._create_archi()

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        os.makedirs(os.path.join(self.output_dir,"data"))
        os.makedirs(os.path.join(self.output_dir,"visualisation"))

    def write_batch_res(self, result:tuple, label:list, numero_batch:int, best=True):
        if best:
            for prob, pred in result:
                idx = np.argmax(prob)
                res = {
                    "Label":label[idx],
                    "Probabilité":prob[idx],
                    "Text proximity": pred[idx]
                }

                # Serializing json
                json_object = json.dumps(res, indent=4)
                
                # Writing to sample.json
                with open(os.path.join(self.output_dir, "data", str(numero_batch), ".json"), "w") as outfile:
                    outfile.write(json_object)

    def show_examples_pred(self):
        pass

import cv2
import matplotlib.pyplot as plt
import logging
import numpy as np
import onnxruntime
from progressbar import progressbar

from .detector_utils import preprocess_image
from .video_utils import get_interest_frames_from_video


def dummy(x):
    return x


class Detector:
    detection_model = None
    classes = None

    def __init__(self, model_name="default", checkpoint_path = "model/detector_v2_default_checkpoint.onnx", classes_path = "model/detector_v2_default_classes", ):
        """
        model = Detector()
        """

        self.detection_model = onnxruntime.InferenceSession(checkpoint_path)
        self.classes = [c.strip() for c in open(classes_path).readlines() if c.strip()]

    def detect_video(self, video_path, mode="default", min_prob=0.6, batch_size=2, show_progress=True):
        frame_indices, frames, fps, video_length = get_interest_frames_from_video(
            video_path
        )
        logging.debug(
            f"VIDEO_PATH: {video_path}, FPS: {fps}, Important frame indices: {frame_indices}, Video length: {video_length}"
        )
        if mode == "fast":
            frames = [
                preprocess_image(frame, min_side=480, max_side=800) for frame in frames
            ]
        else:
            frames = [preprocess_image(frame) for frame in frames]

        scale = frames[0][1]
        frames = [frame[0] for frame in frames]
        all_results = {
            "metadata": {
                "fps": fps,
                "video_length": video_length,
                "video_path": video_path,
            },
            "preds": {},
        }

        progress_func = progressbar

        if not show_progress:
            progress_func = dummy

        for _ in progress_func(range(int(len(frames) / batch_size) + 1)):
            batch = frames[:batch_size]
            batch_indices = frame_indices[:batch_size]
            frames = frames[batch_size:]
            frame_indices = frame_indices[batch_size:]
            if batch_indices:
                outputs = self.detection_model.run(
                    [s_i.name for s_i in self.detection_model.get_outputs()],
                    {self.detection_model.get_inputs()[0].name: np.asarray(batch)},
                )

                labels = [op for op in outputs if op.dtype == "int32"][0]
                scores = [op for op in outputs if isinstance(op[0][0], np.float32)][0]
                boxes = [op for op in outputs if isinstance(op[0][0], np.ndarray)][0]

                boxes /= scale
                for frame_index, frame_boxes, frame_scores, frame_labels in zip(
                    frame_indices, boxes, scores, labels
                ):
                    if frame_index not in all_results["preds"]:
                        all_results["preds"][frame_index] = []

                    for box, score, label in zip(
                        frame_boxes, frame_scores, frame_labels
                    ):
                        if score < min_prob:
                            continue
                        box = box.astype(int).tolist()
                        label = self.classes[label]

                        all_results["preds"][frame_index].append(
                            {
                                "box": [int(c) for c in box],
                                "score": float(score),
                                "label": label,
                            }
                        )

        return all_results

    def detect(self, img_path, mode="default", min_prob=None):
        if mode == "fast":
            image, scale = preprocess_image(img_path, min_side=480, max_side=800)
            if not min_prob:
                min_prob = 0.5
        else:
            image, scale = preprocess_image(img_path)
            if not min_prob:
                min_prob = 0.6

        outputs = self.detection_model.run(
            [s_i.name for s_i in self.detection_model.get_outputs()],
            {self.detection_model.get_inputs()[0].name: np.expand_dims(image, axis=0)},
        )

        labels = [op for op in outputs if op.dtype == "int32"][0]
        scores = [op for op in outputs if isinstance(op[0][0], np.float32)][0]
        boxes = [op for op in outputs if isinstance(op[0][0], np.ndarray)][0]

        boxes /= scale
        processed_boxes = []
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < min_prob:
                continue
            box = box.astype(int).tolist()
            label = self.classes[label]
            processed_boxes.append(
                {"box": [int(c) for c in box], "score": float(score), "label": label}
            )

        return processed_boxes

    def censor(self, img_path, out_path=None, visualize=False, parts_to_blur=[]):
        if not out_path and not visualize:
            print(
                "No out_path passed and visualize is set to false. There is no point in running this function then."
            )
            return

        image = cv2.imread(img_path)
        boxes = self.detect(img_path)

        if parts_to_blur:
            boxes = [i["box"] for i in boxes if i["label"] in parts_to_blur]
        else:
            boxes = [i["box"] for i in boxes]

        for box in boxes:
            part = image[box[1] : box[3], box[0] : box[2]]
            image = cv2.rectangle(
                image, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), cv2.FILLED
            )

        if visualize:
            cvt_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(cvt_img)
            #cv2.imshow("Blurred image", image)
            #cv2.waitKey(0)
            plt.show()

        if out_path:
            cv2.imwrite(out_path, image)

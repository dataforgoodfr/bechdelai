import cv2
import os

class Extract_Video_Stream():

    def __init__(self, url_channel:str, quality="worst") -> None:

        self.stream = os.popen("streamlink --stream-url "+  url_channel + " " + quality).read().replace('\n', '')
        print(self.stream)

    
    def read_video(self, treatment_model):
    
        vcap = cv2.VideoCapture(self.stream)
        
        while(True):
            # Capture frame-by-frame
            ret, frame = vcap.read()
            #print cap.isOpened(), ret
            if frame is not None:
                # Display the resulting frame
                cv2.imshow("Stream", treatment_model(frame))

                if cv2.waitKey(22) & 0xFF == ord('q'):
                    break
            else:
                print("Frame is None")
                break

        # When everything done, release the capture
        vcap.release()
        cv2.destroyAllWindows()
    
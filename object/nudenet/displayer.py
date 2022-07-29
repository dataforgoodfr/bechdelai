import matplotlib.pyplot as plt
import cv2
import time

"""
w, h = 2, 2
fig = plt.figure(figsize=(8, 8))
columns, rows = 2, 2

fig.add_subplot(2, 2, 1)
im = cv2.imread("examples/sexy/sexy.jpeg")
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
fig.add_subplot(2, 2, 2)
im = cv2.imread("examples/sexy/censored_sexy.jpeg")
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
fig.add_subplot(2, 2, 3)
im = cv2.imread("examples/sexy/sexy_3.jpeg")
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
fig.add_subplot(2, 2, 4)
im = cv2.imread("examples/sexy/censored_sexy_3.jpeg")
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))

plt.savefig("ex.png")
"""

cap = cv2.VideoCapture("https://tf1-hls-live.tf1.fr/video/pwEdpd1UpcchzotQH31z4w/1659109799/out/v1/c2e382be3aa2486e8753747e7bb6157e/index_4.m3u8")
if not cap.isOpened():
    print("Cannot open camera")


while True:

    #print('About to start the Read command')
    ret, frame = cap.read()
    #print('About to show frame of Video.')
    cv2.imshow("Capturing",frame)
    time.sleep(0.04)
    #print('Running..')

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
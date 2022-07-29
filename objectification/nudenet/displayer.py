import matplotlib.pyplot as plt
import cv2

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
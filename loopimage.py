import cv2
import numpy as np
from bitplane import *

cap = cv2.VideoCapture('kojima.png')

height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
plane_img = np.zeros((height, width), dtype='uint8')
print(plane_img.shape)

plane = 7
FRAME_DELAY_MS = 1000
while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', set_bit_plane(gray, plane, plane_img))
    else:
        print('restarting')
        cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        cv2.imshow('frame', set_bit_plane(gray, plane, plane_img))
    
    if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
        break

    print(plane)
    plane = (plane + 1) % 8

cap.release()
cv2.destroyAllWindows()
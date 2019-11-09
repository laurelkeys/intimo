import cv2
import numpy as np
from bitplane import *

cap = cv2.VideoCapture('kojima.png')

height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
plane_img = np.zeros((height, width), dtype='uint8')
print(plane_img.shape)

i = 0
done = False
FRAME_DELAY_MS = 250
while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', set_bit_plane_partial(gray, 6, plane_img, changed_bits=i))
    else:
        # print('restarting')
        cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        cv2.imshow('frame', set_bit_plane_partial(gray, 6, plane_img, changed_bits=i))
    
    if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
        break

    if not done:
        plane_img.ravel()[i:i+10000] = 0 # 0 or 1
        i += 10000
        if i > plane_img.size: # FIXME prevent 'overshooting'
            print('done')
            done = True

cap.release()
cv2.destroyAllWindows()
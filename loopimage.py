import cv2
import numpy as np

cap = cv2.VideoCapture('kojima.png')
FRAME_DELAY_MS = 1000

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', gray)
    else:
       print('restarting')
       cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
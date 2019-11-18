import sys
import cv2
import queue
import numpy as np
import sounddevice as sd

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from bitplane import set_bit_plane_partial

#########################################

MONO, STEREO = 1, 2 # number of audio channels
SAMPLE_RATE  = 8000 # 8kHz for voice recording

WINDOW_ms = 200
INTERVAL_ms = 30

#########################################

# mic setup
device_info = sd.query_devices(kind='input')
print(device_info)

# camera setup
cap = cv2.VideoCapture('kojima.png') # TODO change to cv2.VideoCapture(0) to use the webcam

height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
hidden_plane = np.zeros((height, width), dtype='uint8')
print(hidden_plane.shape)

#########################################

q = queue.Queue()

# this is called (from a separate thread) for each audio block
def in_stream_callback(in_data, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # create a (necessary) copy of the input audio
    q.put(np.copy(in_data))

# NOTE the number of frames passed to the stream callback can be set with the 'blocksize' param
stream = sd.InputStream(channels=MONO, samplerate=SAMPLE_RATE,
                        callback=in_stream_callback)
with stream:
    curr_bit = 0 # next bit to write to (indexed on the flattened hidden_plane)
    done = False
    FRAME_DELAY_MS = 250
    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        cv2.imshow('frame', set_bit_plane_partial(gray_frame, 6, hidden_plane, changed_bits=curr_bit))
        
        if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
            break

        try:
            in_data = q.get_nowait()
            assert in_data.shape[1] == 1
            in_data = in_data.reshape(-1)
            length = in_data.size
        except queue.Empty:
            print("q is empty")
            break

        if not done:
            hidden_plane.ravel()[curr_bit : curr_bit + length] = in_data # TODO make sure we don't actually need np.copy(in_data)
            curr_bit += length
            if curr_bit > hidden_plane.size: # FIXME prevent 'overshooting'
                print('done')
                done = True
    cap.release()
    cv2.destroyAllWindows()
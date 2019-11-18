import sys
import cv2
import queue
import numpy as np
import sounddevice as sd

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from bitplane import set_bit_plane_partial
from converter import convert
from item_store import ItemStore

#########################################

MONO, STEREO = 1, 2 # number of audio channels
SAMPLE_RATE  = 44100 # 8kHz for voice recording

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

in_data_list = ItemStore() # thread-safe list of audio blocks

# this is called (from a separate thread) for each audio block
def in_stream_callback(in_data, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # create a (necessary) copy of the input audio
    in_data_list.add(np.copy(in_data))

# NOTE the number of frames passed to the stream callback can be set with the 'blocksize' param
stream = sd.InputStream(channels=MONO, samplerate=SAMPLE_RATE, dtype='int16',
                        callback=in_stream_callback)
with stream:
    hidden_bits = 0 # next bit to write to (indexed on the flattened hidden_plane)
    done = False
    FRAME_DELAY_MS = 250
    while cap.isOpened() and not done:
        ret, frame = cap.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        cv2.imshow('frame', set_bit_plane_partial(gray_frame, 6, hidden_plane, changed_bits=hidden_bits))
        
        if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
            break

        in_data = np.concatenate(in_data_list.getAll()) # concatenate the stored audio blocks
        assert in_data.dtype == np.int16
        in_data = convert(_in_data.reshape(-1), to='uint8')
        length = in_data.size

        if not done:
            if hidden_bits + length > hidden_plane.size:
                print(f'length = {length} but hidden_bits = {hidden_bits}')
                # TODO verify if we can add a partial block, i.e.:
                hidden_plane.ravel()[hidden_bits : ] = in_data[ : hidden_plane.size - hidden_bits]
                print('done')
                done = True
            else:
                hidden_plane.ravel()[hidden_bits : hidden_bits + length] = in_data
            hidden_bits += length
    cap.release()
    cv2.destroyAllWindows()

from scipy.io import wavfile
print(':)')
assert hidden_plane.dtype == np.uint8
cap_audio = convert(hidden_plane.flatten(), to='int16')
wavfile.write('out.wav', SAMPLE_RATE, hidden_plane.ravel()) # FIXME the audio is corrupted
print(':D')
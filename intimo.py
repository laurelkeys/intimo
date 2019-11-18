import sys
import cv2
import time
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

BIT_PLANE = 6

#########################################

# mic setup
device_info = sd.query_devices(kind='input')
print("\ndevice_info")
print(device_info)

# camera setup
cap = cv2.VideoCapture('kojima.png') # TODO change to cv2.VideoCapture(0) to use the webcam

height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
hidden_plane = np.zeros((height, width), dtype='uint8')
print("\nhidden_plane.shape")
print(hidden_plane.shape)

#########################################

in_data_list = ItemStore() # thread-safe list of audio blocks

# this is called (from a separate thread) for each audio block
def in_stream_callback(in_data, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    in_data_list.add(np.copy(in_data))

# NOTE the number of frames passed to the stream callback can be set with the 'blocksize' param
stream = sd.InputStream(channels=MONO, samplerate=SAMPLE_RATE, dtype='int16',
                        callback=in_stream_callback)
with stream:
    hidden_bits = 0 # next bit to write to (indexed on the flattened hidden_plane)
    done = False
    FRAME_DELAY_MS = 250 # TODO decrease when using the webcam
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            in_frame = frame
            # gray_frame = cv2.cvtColor(in_frame, cv2.COLOR_BGR2GRAY)
            pass
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, -1)
        out_frame = np.copy(in_frame)
        for ch in [0, 1, 2]:
            out_frame[..., ch] = set_bit_plane_partial(in_frame[..., ch], BIT_PLANE, hidden_plane, changed_bits=hidden_bits)
        # out_frame = set_bit_plane_partial(gray_frame, BIT_PLANE, hidden_plane, changed_bits=hidden_bits)
        print("shapes:", in_frame.shape, out_frame.shape)
        cv2.imshow('frame', out_frame)
        if done:
            fname = time.strftime("%Y%m%d-%H%M%S") + ".png"
            cv2.imwrite(fname, out_frame)
            # reset
            hidden_bits = 0
            done = False
            print(f"saved to {fname}")

        if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
            break

        in_data = np.concatenate(in_data_list.getAll()) # concatenate the stored audio blocks
        assert in_data.dtype == np.int16
        in_data = convert(in_data.reshape(-1), to='uint8')
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
wavfile.write('out.wav', SAMPLE_RATE, cap_audio)
print(':D')

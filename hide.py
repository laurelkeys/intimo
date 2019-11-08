import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

import soundfile as sf
import sounddevice as sd

from sys import argv
from codec import *
from converter import *
from scipy.io.wavfile import write

def print_stats(arr, arr_name=''):
    print(f'{arr_name}:', arr.dtype, arr.shape, arr.min(), arr.max())

def show(bgr_img):
    plt.axis('off')
    rgb_img = cv2.cvtColor(bgr_img.astype('uint8'), cv2.COLOR_BGR2RGB)
    plt.imshow(rgb_img, vmin=0, vmax=255)
    plt.show()

SHOW_IMAGE = True
PLAY_AUDIO = True
OUTPUT_FOLDER = '.'

audio_fname = 'output-mono.wav'
mono_audio, sr = sf.read(audio_fname, dtype='int16')
if PLAY_AUDIO: sd.play(mono_audio, sr); sd.wait() # wait until file is done playing

img_fname = 'kojima.png'
bgr_img = cv2.imread(img_fname, cv2.IMREAD_COLOR)
if SHOW_IMAGE: show(bgr_img)

# the hidden message is the audio 'converted' from int16 to uint8
message = int8_to_uint8(int16_to_int8(mono_audio))

print_stats(mono_audio, 'mono_audio')
print_stats(bgr_img, 'bgr_img')
print_stats(message, 'message')
print((int8_to_int16(uint8_to_int8(message)) == mono_audio).all())

BIT_PLANE = 7

__bgr_img = encode(bgr_img, BIT_PLANE, message)
print_stats(__bgr_img, '__bgr_img')
if SHOW_IMAGE: show(__bgr_img)
cv2.imwrite('kojima-mono-7.png', __bgr_img)

__message = decode(__bgr_img, BIT_PLANE)
__message = __message[:message.size] # FIXME add an 'end of message' marker on `encode`
print_stats(__message, '__message')
print((__message == message).all())

__mono_audio = int8_to_int16(uint8_to_int8(__message))
print_stats(__mono_audio, '__mono_audio')
print((__mono_audio == mono_audio).all())

# play the message that was decoded from the image and 'converted' from uint8 to int16
if PLAY_AUDIO: sd.play(__mono_audio, 8000); sd.wait()

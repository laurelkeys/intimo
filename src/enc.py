import os
import sys
import time
import pprint
import argparse
import warnings

import cv2
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from codec import *
from bitplane import set_bit_plane_partial
from converter import convert

def get_parser():
    parser = argparse.ArgumentParser(
        description="Real-time steganography. "
                    "Hiding audio data into image frames from a live camera input stream.")
    parser.add_argument("--n_of_channels", "-ch", type=int, choices=[1, 2], default=1, 
                        help="Number of audio channels (1=mono, 2=stereo)  (defaults to %(default)d)")
    parser.add_argument("--sample_rate", "-sr", type=int, choices=[8000, 44100], default=8000, 
                        help="Sample rate of audio recording  (defaults to %(default)dHz)")
    parser.add_argument("--bit_plane", "-b", type=int, choices=range(0, 8), default=6, 
                        help="Bit plane in which to hide the captured audio  (defaults to %(default)d)")
    parser.add_argument("--output_folder", "-o", type=str, default=".", 
                        help="Output folder to store the saved image frames  (defaults to '%(default)s/')")
    parser.add_argument("--save_audio", "-a", action="store_true", 
                        help="Save the audio file retrieved from the image as well")
    parser.add_argument("--grayscale", "-g", action="store_true", 
                        help="Use grayscale frames instead of RGB")
    parser.add_argument("--wait", "-w", action="store_true", 
                        help="Wait for a key press to save frames")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Increase verbosity")
    return parser

###############################################################################

def setup_camera(args):
    if args.verbose:
        print("device_info:")
        pprint.pprint(sd.query_devices(kind='input'))
        
        start = time.time()
    
    # DirectShow (via videoInput)
    cap = cv2.VideoCapture(index=0, apiPreference=cv2.CAP_DSHOW)
    
    if args.verbose:
        print(f"Camera setup took {(time.time() - start):.1f}s")

    # NOTE cv2.VideoCapture(0) may take a few seconds
    if not cap.read()[0]:
        raise Exception("No camera found")

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    depth  = 1 if args.grayscale else 3
    if depth == 1:
        warnings.warn("\nWarning: grayscale video isn't currently supported")
    
    return cap, height, width, depth

def save_frame(__frame, message_uint8, stream, args):
    if args.wait:
        # FIXME check if a key (e.g. space) was pressed to save this finished frame
        warnings.warn("\nWarning: waiting for key press isn't currently supported")
    
    fname = f"{time.strftime('%Y%m%d-%H%M%S')}_{stream._samplerate:.0f}_{stream._channels:.0f}"
    fname = os.path.join(args.output_folder, fname)

    cv2.imwrite(filename=fname + ".png", img=__frame)
    if args.verbose:
        print(f"Saved image to '{fname}.png'")

    # TODO get audio from __frame instead of message_uint8
    if args.save_audio:
        #decoded_audio = decode(__frame, args.bit_plane)
        decoded_audio = message_uint8
        decoded_audio = convert(decoded_audio, to='int16')
        
        if stream._channels == 2:
            # FIXME convert decoded_audio to a 2D array if it's stereo
            warnings.warn("\nWarning: stereo audio isn't currently supported")
        
        wavfile.write(filename=fname + ".wav", rate=int(stream._samplerate), data=decoded_audio)
        if args.verbose:
            print(f"Saved audio to '{fname}.wav'")

def main(args):
    if args.n_of_channels == 2:
        warnings.warn("\nWarning: stereo audio isn't currently supported")
    if args.grayscale:
        warnings.warn("\nWarning: grayscale video isn't currently supported")
    if args.wait:
        warnings.warn("\nWarning: waiting for key press isn't currently supported")

    cap, height, width, depth = setup_camera(args) # NOTE this takes around 20s
    message_uint8 = np.zeros(dtype='uint8', shape=height * width * depth // 8 )
    if args.verbose:
        print(f"(height, width, depth)=({height}, {width}, {depth})")
        print(f"message_uint8: shape={message_uint8.shape} | size={message_uint8.size}")

    # list to store the audio blocks captured by the audio input stream
    in_data_list = []
    def in_stream_callback(in_data, frames, time, status):
        if status:
            print(status, file=sys.stderr if not args.verbose else sys.stdout)
        in_data_list.append(np.copy(in_data)) # append audio block
    
    stream = sd.InputStream(dtype='int16',
                            channels=args.n_of_channels,
                            samplerate=args.sample_rate,
                            callback=in_stream_callback)
    if args.verbose:
        print("sample rate:", stream._samplerate)
        print("number of audio channels:", stream._channels, 
              "(mono)" if stream._channels == 1 else "(stereo)")

    with stream: # listen for live audio input
        hidden_bytes, done, __frame = 0, False, None
        a = False
        while cap.isOpened():
            ret, frame = cap.read() # get image from camera
            if not ret:
                print(f"cap.read() returned {ret}", 
                      file=sys.stderr if not args.verbose else sys.stdout)
                break
            else:
                if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
                    break

                if a: a = not a

                if done:
                    save_frame(__frame, message_uint8, stream, args)
                    hidden_bytes, done = 0, False # reset values
                    a = True

                __frame = encode(frame, args.bit_plane, message_uint8, debug=a)
                cv2.imshow('frame', __frame)
                
                # get all audio blocks that have been captured since the last loop iteration
                stored_audio_blocks, in_data_list = in_data_list, []

                if len(stored_audio_blocks) > 0:
                    # concatenate the stored audio blocks (uint16)
                    in_audio = np.concatenate(stored_audio_blocks)

                    audio_uint8 = convert(in_audio.reshape(-1), to='uint8')
                    length = audio_uint8.size

                    if hidden_bytes + length < message_uint8.size:
                        message_uint8.ravel()[hidden_bytes : hidden_bytes + length] = audio_uint8
                        hidden_bytes += length
                    else:
                        max_length = message_uint8.size - hidden_bytes
                        if args.verbose:
                            print(f"Hiding {max_length} bytes (audio_uint8.size={length} but "
                                  f"hidden_bytes={hidden_bytes} and message_uint8.size={hidden_plane_img.size})")
                        
                        # TODO verify if we can add partial blocks, i.e.:
                        message_uint8.ravel()[hidden_bytes : ] = audio_uint8[ : max_length]

                        # TODO save the audio data that didn't fit in message_uint8
                        #      to hide it in the next frame (audio_uint8[max_length : ])
                        done = True
        
        cap.release()
        cv2.destroyAllWindows()

###############################################################################

FRAME_DELAY_MS = 10
if __name__ == '__main__':
    args = get_parser().parse_args()
    args.verbose = True # FIXME remove after testing
    main(args)

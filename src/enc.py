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
    parser.add_argument("--no_wait", "-n", action="store_true", 
                        help="Don't wait for a key press to starting saving frames")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Increase verbosity")
    return parser

###############################################################################

def main(args):
    # mic setup
    device_info = sd.query_devices(kind='input')
    if args.verbose:
        print("device_info:")
        pprint.pprint(device_info)

    # camera setup
    start = time.time()
    try:
        cap = cv2.VideoCapture(0) # NOTE this may take a few seconds
        if not cap.read()[0]:
            raise Exception
        FRAME_DELAY_MS = 10
    except:
        print("No camera found")
        # cap = cv2.VideoCapture('kojima.png')
        FRAME_DELAY_MS = 250
        exit() # TODO allow static image use by passing an image file
    if args.verbose:
        print(f"Camera setup took {(time.time() - start):.1f}s")

    height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hidden_plane_img = np.zeros((height, width), dtype='uint8')
    if args.verbose:
        print("hidden_plane_img.shape:", hidden_plane_img.shape)
        print("hidden_plane_img.size:", hidden_plane_img.size)

    # audio input stream setup
    in_data_list = [] # list to store the audio blocks (in_data) captured by sd.InputStream

    # this is called (from a separate thread) for each audio block
    def in_stream_callback(in_data, frames, time, status):
        if status:
            print(status, file=sys.stderr if not args.verbose else sys.stdout)
        in_data_list.append(np.copy(in_data))
    
    # NOTE the number of frames passed to the stream callback can be set with the blocksize param
    #      the special value blocksize = 0 (which is the default) may be used to request that the 
    #      stream callback will receive an optimal (and possibly varying) number of frames 
    stream = sd.InputStream(
        channels=args.n_of_channels, 
        samplerate=args.sample_rate, 
        blocksize=0, 
        dtype='int16',
        callback=in_stream_callback)
    if args.verbose:
        print("sample rate:", stream._samplerate)
        print("number of audio channels:", stream._channels, "(mono)" if stream._channels == 1 else "stereo")

    with stream: # listen for live audio input

        hidden_bits = 0 # next bit to write to (indexed on the flattened hidden_plane_img)
        
        done = False # True if hidden_plane_img is full

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
                    break

                # __frame = set_bit_plane_partial(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), args.bit_plane, 
                #                                 hidden_plane_img, changed_bits=hidden_bits)            
                __frame = np.copy(frame)
                for ch in [0, 1, 2]:
                    __frame[..., ch] = set_bit_plane_partial(frame[..., ch], args.bit_plane, 
                                                             hidden_plane_img, changed_bits=hidden_bits)

                cv2.imshow('frame', __frame)

                if done:
                    if not args.no_wait:
                        # FIXME check if a key (e.g. space) was pressed to save this finished frame
                        warnings.warn("\nWarning: current behaviour is the same as when using --no_wait")
                        continue

                    fname = f"{time.strftime('%Y%m%d-%H%M%S')}_{stream._samplerate:.0f}_{stream._channels:.0f}"
                    fname = os.path.join(args.output_folder, fname)
                    cv2.imwrite(filename=fname + ".png", img=__frame)
                    if args.verbose:
                        print(f"Saved image to '{fname}.png'")

                    if args.save_audio:
                        # TODO get audio from __frame instead of hidden_plane_img
                        assert hidden_plane_img.dtype == np.uint8
                        decoded_audio = convert(hidden_plane_img.flatten(), to='int16')
                        if stream._channels == 2:
                            # FIXME convert decoded_audio to a 2D array if it's stereo
                            warnings.warn("\nWarning: stereo audio isn't currently supported")
                        wavfile.write(filename=fname + ".wav", rate=int(stream._samplerate), data=decoded_audio)
                        if args.verbose:
                            print(f"Saved audio to '{fname}.wav'")
                    
                    # reset values
                    hidden_bits, done = 0, False
                
                # get all audio blocks that have been captured since the last loop iteration
                stored_audio_blocks, in_data_list = in_data_list, []
                if len(stored_audio_blocks) == 0:
                    if args.verbose:
                        print("No audio blocks stored in the last iteration "
                              "(you may consider changing blocksize or samplerate)")
                else:
                    # concatenate the stored audio blocks (uint16)
                    in_audio = np.concatenate(stored_audio_blocks)
                    assert in_audio.dtype == np.int16
                    __audio = convert(in_audio.reshape(-1), to='uint8')
                    length = __audio.size

                    if hidden_bits + length < hidden_plane_img.size:
                        hidden_plane_img.ravel()[hidden_bits : hidden_bits + length] = __audio
                        hidden_bits += length
                    else:
                        max_length = hidden_plane_img.size - hidden_bits
                        if args.verbose:
                            print(f"Hiding {max_length} bits (length={length} but "
                                  f"hidden_bits={hidden_bits} and hidden_plane_img.size={hidden_plane_img.size})")
                        
                        # TODO verify if we can add partial blocks, i.e.:
                        hidden_plane_img.ravel()[hidden_bits : ] = __audio[ : max_length]

                        # TODO save the audio data that didn't fit in hidden_plane_img
                        #      to hide it in the next frame (__audio[max_length : ])
                        
                        done = True
            else:
                print(f"cap.read() returned {ret}", file=sys.stderr if not args.verbose else sys.stdout)
                break
        
        cap.release()
        cv2.destroyAllWindows()

###############################################################################

if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)

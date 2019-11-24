import os, sys, time
import argparse
import warnings

import cv2
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from codec import *
from converter import convert

def get_parser():
    parser = argparse.ArgumentParser(
        description="Real-time steganography: "
                    "hiding captured audio data into image frames from a live camera input stream.")
    
    parser.add_argument("--n_of_channels", "-ch", type=int, choices=[1, 2], default=1, 
                        help="Number of audio channels (1=mono, 2=stereo)  (defaults to %(default)d)")
    parser.add_argument("--sample_rate", "-sr", type=int, choices=[8000, 44100], default=8000, 
                        help="Sample rate of audio recording  (defaults to %(default)dHz)")
    parser.add_argument("--bit_plane", "-b", type=int, choices=range(0, 8), default=5, 
                        help="Bit plane in which to hide the captured audio  (defaults to %(default)d)")
    
    parser.add_argument("--output_folder", "-o", type=str, default=".", 
                        help="Output folder to store the saved image frames  (defaults to '%(default)s/')")
    
    parser.add_argument("--save_audio", action="store_true", 
                        help="Save the audio file retrieved from the image as well")
    parser.add_argument("--grayscale", action="store_true", 
                        help="Use grayscale frames instead")
    parser.add_argument("--wait", action="store_true", 
                        help="Wait for a key press to save frames")
    
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Increase verbosity")
    return parser

###############################################################################

def setup_camera(args):
    cap = cv2.VideoCapture(apiPreference=cv2.CAP_DSHOW, # DirectShow (via videoInput)
                           index=0)
    if not cap.read()[0]:
        raise Exception("No camera found")
    height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), \
                    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    return cap, height, width

def save_frame(__frame, message_uint8, stream, args):
    if args.wait: pass
    # TODO check if a key (e.g. space) was pressed to save this finished frame

    # "channels_samplerate_bitplane_YYYYmmdd-HHMMSS"
    fname = '_'.join([str(int(stream._channels)),
                      str(int(stream._samplerate)),
                      str(args.bit_plane),
                      time.strftime('%Y%m%d-%H%M%S')])
    fname = os.path.join(args.output_folder, fname)

    cv2.imwrite(filename=fname + ".png", img=__frame)
    if args.verbose:
        print(f"Saved image to '{fname}.png'")

    if args.save_audio:
        decoded_audio = decode(__frame, args.bit_plane)
        decoded_audio = convert(decoded_audio, to='int16')
        
        if stream._channels == 2: pass
        # TODO convert decoded_audio to a 2D array if it's stereo
        
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

    if args.verbose:
        print("device_info: {")
        for k, v in sd.query_devices(kind='input').items():
            print(f"  {k}: {v}")
        print("}")

    cap, height, width = setup_camera(args)
    depth = 3 # 1 if args.grayscale else 3
    print()

    buffer_factor = 1.2
    message_uint8 = np.zeros(dtype='uint8', shape=int(buffer_factor * (height * width * depth) // 8 ))
    if args.verbose:
        print(f"(height, width, depth): ({height}, {width}, {depth})")
        print("message_uint8.size:", message_uint8.size)
        print("buffer_factor:", buffer_factor)

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

    print()
    with stream: # listen for live audio input

        hidden_bytes, done = 0, False
        while cap.isOpened():

            ret, frame = cap.read() # get image from camera
            if not ret:
                print(f"cap.read() returned {ret}", 
                      file=sys.stderr if not args.verbose else sys.stdout)
                break
            else:
                if cv2.waitKey(FRAME_DELAY_MS) & 0xFF == ord('q'):
                    break

                __frame, done = encode(frame, args.bit_plane, message_uint8[ : hidden_bytes])
                cv2.imshow('frame', __frame)

                if done:
                    save_frame(__frame, message_uint8, stream, args)
                    
                    _, max_bits = max_bytes_and_bits(height, width, depth)
                    message_bits = np.unpackbits(message_uint8[ : hidden_bytes])
                    remaining_bits = message_bits.size - max_bits
                    if remaining_bits > 0:
                        if args.verbose:
                            print(f"> {remaining_bits} bits left out")
                        remaining_bytes = remaining_bits // 8
                        message_uint8[ : remaining_bytes] = message_uint8[hidden_bytes - remaining_bytes : hidden_bytes]

                    hidden_bytes, done = remaining_bytes, False # reset values
                    print()
                
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
                        # NOTE we shouldn't get here if buffer_factor is large enough
                        max_length = message_uint8.size - hidden_bytes
                        if args.verbose:
                            print(f"Hiding {max_length} bytes (audio_uint8.size={length} but "
                                  f"hidden_bytes={hidden_bytes} and message_uint8.size={message_uint8.size})")
                        
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
    main(args)

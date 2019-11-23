import os
import sys
import argparse
import warnings

import cv2
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from codec import decode
from converter import convert

def get_parser():
    parser = argparse.ArgumentParser(
        description="Retrieve WAV audio data from an image bit plane.")
    parser.add_argument("enc_image", type=str, 
                        help="File name (with path) of a PNG image with audio encoded")
    parser.add_argument("--n_of_channels", "-ch", type=int, choices=[1, 2], default=1, 
                        help="Number of audio channels (1=mono, 2=stereo)  (defaults to %(default)d)")
    parser.add_argument("--sample_rate", "-sr", type=int, choices=[8000, 44100], default=8000, 
                        help="Sample rate of audio recording  (defaults to %(default)dHz)")
    parser.add_argument("--bit_plane", "-b", type=int, choices=range(0, 8), default=6, 
                        help="Bit plane in which to hide the captured audio  (defaults to %(default)d)")
    parser.add_argument("--output_folder", "-o", type=str, default=".", 
                        help="Output folder to store the decoded audio  (defaults to '%(default)s/')")
    parser.add_argument("--playback_audio", "-p", action="store_true", 
                        help="Play the decoded audio as well")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Increase verbosity")
    parser.add_argument("--info_in_fname", "-iifn", action="store_true", 
                        help="Gets the number of channels, sample rate, and bit plane from the image file name")
    return parser

###############################################################################

def main(args):
    enc_img = cv2.imread(args.enc_image)
    if args.verbose:
        print(f"enc_img.shape:", enc_img.shape)
        print(f"enc_img.size:", enc_img.size)
        print(f"enc_img.ndim:", enc_img.ndim)

    decoded_audio = decode(enc_img, args.bit_plane)
    assert decoded_audio.dtype == np.uint8
    decoded_audio = convert(decoded_audio, to='int16')

    if args.n_of_channels == 2:
        # FIXME convert decoded_audio to a 2D array if it's stereo
        warnings.warn("\nWarning: stereo audio isn't currently supported")
    
    fname, _ = os.path.splitext(os.path.basename(args.enc_image))
    fname = os.path.join(args.output_folder, fname + "-decoded")
    wavfile.write(filename=fname + ".wav", rate=args.sample_rate, data=decoded_audio)
    if args.verbose:
        print(f"Saved audio to '{fname}.wav'")
    
    if args.playback_audio:
        if args.verbose:
            print(f"Playing audio (~{decoded_audio.size // args.sample_rate}s)..")
        sd.play(decoded_audio, args.sample_rate)
        sd.wait() # wait until it is done playing
        if args.verbose:
            print("done.")

###############################################################################

if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)
import os
import sys
import argparse
import warnings

import cv2
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from bitplane import get_bit_plane
from converter import convert

def get_parser():
    parser = argparse.ArgumentParser(
        description="Retrieve WAV audio data from an image bit plane.")
    parser.add_argument("enc_image", type=str, 
                        help="File name (with path) of an image with audio encoded")
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
    # TODO receive an image as input and return the hidden audio file
    pass

###############################################################################

if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)
import os, sys
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

    parser.add_argument("enc_img_path", type=str, 
                        help="File name (with path) of a PNG image with audio encoded")
    
    parser.add_argument("--n_of_channels", "-ch", type=int, choices=[1, 2], default=1, 
                        help="Number of audio channels (1=mono, 2=stereo)  (defaults to %(default)d)")
    parser.add_argument("--sample_rate", "-sr", type=int, choices=[8000, 44100], default=8000, 
                        help="Sample rate of audio recording  (defaults to %(default)dHz)")
    parser.add_argument("--bit_plane", "-b", type=int, choices=range(0, 8), default=5, 
                        help="Bit plane in which to hide the captured audio  (defaults to %(default)d)")
    
    parser.add_argument("--output_folder", "-o", type=str, default=".", 
                        help="Output folder to store the decoded audio  (defaults to '%(default)s/')")
    parser.add_argument("--info_in_fname", "-iifn", action="store_true", 
                        help="Get the number of channels, sample rate, and bit plane from the image file name "
                             "(other arguments will be ignored)")

    parser.add_argument("--playback", action="store_true", 
                        help="Play the decoded audio as well")
    
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Increase verbosity")
    return parser

###############################################################################

def main(args):
    enc_img = cv2.imread(args.enc_img_path)

    if args.info_in_fname:
        # "channels_samplerate_bitplane_YYYYmmdd-HHMMSS"
        fname, _ = os.path.splitext(os.path.basename(args.enc_img_path))
        try:
            ch, sr, b, *_ = fname.split('_')
            args.n_of_channels = int(ch)
            args.sample_rate = int(sr)
            args.bit_plane = int(b)
            if args.verbose:
                print("Info taken from file name:")
                print(" - channels:", args.n_of_channels)
                print(" - samplerate:", args.sample_rate)
                print(" - bitplane:", args.bit_plane)
        except:
            print("When using --info_in_fname, the expected file name must be in the format: "
                  "'channels_samplerate_bitplane_YYYYmmdd-HHMMSS.png'")
            exit()

    decoded_audio = decode(enc_img, args.bit_plane)
    assert decoded_audio.dtype == np.uint8
    decoded_audio = convert(decoded_audio, to='int16')

    if args.n_of_channels == 2:
        warnings.warn("\nWarning: stereo audio isn't currently supported")
        # TODO convert decoded_audio to a 2D array if it's stereo
    
    fname, _ = os.path.splitext(os.path.basename(args.enc_img_path))
    fname = os.path.join(args.output_folder, fname + "-decoded")
    wavfile.write(filename=fname + ".wav", rate=args.sample_rate, data=decoded_audio)
    if args.verbose:
        print(f"\nSaved audio to '{fname}.wav'")
    
    if args.playback:
        if args.verbose:
            print(f"\nPlaying (~{decoded_audio.size // args.sample_rate}s) audio..", end='')
        sd.play(decoded_audio, args.sample_rate)
        sd.wait() # wait until it is done playing
        if args.verbose:
            print(". done.")

###############################################################################

if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args)
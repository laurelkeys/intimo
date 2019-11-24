# intimo
Hiding audio on video frames in real-time

## Install dependencies
> pip3 install numpy opencv-python sounddevice

## Example usage
`$ python3 enc.py -v --save_audio`
`$ python3 dec.py path/to/enc_img.png -v --playback`

## [enc.py](https://github.com/laurelkeys/intimo/blob/master/src/enc.py) (Encoding)
```
usage: enc.py [-h] [--n_of_channels {1,2}] [--sample_rate {8000,44100}]
              [--bit_plane {0,1,2,3,4,5,6,7}] [--output_folder OUTPUT_FOLDER]
              [--save_audio] [--grayscale] [--wait] [--verbose]

Real-time steganography: hiding captured audio data into image frames from a
live camera input stream.

optional arguments:
  -h, --help            show this help message and exit
  --n_of_channels {1,2}, -ch {1,2}
                        Number of audio channels (1=mono, 2=stereo)
                        (defaults to 1)
  --sample_rate {8000,44100}, -sr {8000,44100}
                        Sample rate of audio recording
                        (defaults to 8000Hz)
  --bit_plane {0,1,2,3,4,5,6,7}, -b {0,1,2,3,4,5,6,7}
                        Bit plane in which to hide the captured audio
                        (defaults to 5)
  --output_folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Output folder to store the saved image frames
                        (defaults to './')
  --save_audio          Save the audio file retrieved from the image as well
  --grayscale           Use grayscale frames instead
  --wait                Wait for a key press to save frames
  --verbose, -v         Increase verbosity
```

## [dec.py](https://github.com/laurelkeys/intimo/blob/master/src/dec.py) (Decoding)
```
usage: dec.py [-h] [--n_of_channels {1,2}] [--sample_rate {8000,44100}]
              [--bit_plane {0,1,2,3,4,5,6,7}] [--output_folder OUTPUT_FOLDER]
              [--info_in_fname] [--playback] [--verbose]
              enc_img_path

Retrieve WAV audio data from an image bit plane.

positional arguments:
  enc_img_path          File name (with path) of a PNG image with audio
                        encoded

optional arguments:
  -h, --help            show this help message and exit
  --n_of_channels {1,2}, -ch {1,2}
                        Number of audio channels (1=mono, 2=stereo)
                        (defaults to 1)
  --sample_rate {8000,44100}, -sr {8000,44100}
                        Sample rate of audio recording
                        (defaults to 8000Hz)
  --bit_plane {0,1,2,3,4,5,6,7}, -b {0,1,2,3,4,5,6,7}
                        Bit plane in which to hide the captured audio
                        (defaults to 5)
  --output_folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Output folder to store the decoded audio
                        (defaults to './')
  --info_in_fname, -iifn
                        Get the number of channels, sample rate, and bit plane
                        from the image file name (other arguments will be ignored)
  --playback            Play the decoded audio as well
  --verbose, -v         Increase verbosity
```
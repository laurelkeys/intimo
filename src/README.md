> pip3 install numpy opencv-python sounddevice

## Example usage
`$ python record.py -n -a -v`

## [record.py](https://github.com/laurelkeys/intimo/blob/master/src/record.py)
```
usage: record.py [-h]
                 [--n_of_channels {1,2}]
                 [--sample_rate {8000,44100}]
                 [--bit_plane {0,1,2,3,4,5,6,7}]
                 [--no_wait]
                 [--save_audio]
                 [--verbose]

Real-time steganography. 
Hiding audio data into image frames from a live camera input stream.

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
                        (defaults to 6)
  --no_wait, -n         Don't wait for a key press to starting saving frames
  --save_audio, -a      Save the audio file retrieved from the image as well
  --verbose, -v         Increase verbosity
```

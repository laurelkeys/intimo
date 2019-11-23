import os
import soundfile as sf
import sounddevice as sd

from sys import argv
from prompt_yes_no import *
from scipy.io.wavfile import write

DTYPE = "int16"

MONO, STEREO = 1, 2 # number of audio channels

SAMPLE_RATE = 8000 # voice recording

# OUTPUT_FOLDER = os.path.join("D:\\", "Music")
OUTPUT_FOLDER = '.'

def record(duration_in_sec, fs=SAMPLE_RATE, mode='mono', wait=True):
    assert mode in ['mono', 'stereo']
    recording = sd.rec(frames=int(duration_in_sec * SAMPLE_RATE), samplerate=fs, 
                       channels=MONO if mode == 'mono' else STEREO, dtype=DTYPE)
    if wait:
        sd.wait() # wait until recording is finished
    return recording

def save(fname, recording, fs=SAMPLE_RATE):
    write(fname, fs, recording) # save as WAV file

filename = argv[1].strip() if len(argv) > 1 else "output-mono"
filename = os.path.join(OUTPUT_FOLDER, filename + ".wav")
# if os.path.exists(filename):
#     if prompt_yes_no(f"'{filename}' will be overwritten. Continue?", True):
#         os.remove(filename)
#     else:
#         exit()

# recording = record(duration_in_sec=3)
# print(recording.dtype, recording.shape, recording.min(), recording.max())
# save(filename, recording)

__recording, __fs = sf.read(filename, dtype=DTYPE)
print(__recording.dtype, __recording.shape, __recording.min(), __recording.max())
# sd.play(__recording, __fs)
# status = sd.wait() # wait until file is done playing

# print((recording == __recording).all())


# ref.: https://realpython.com/playing-and-recording-sound-python/
#       http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
#       https://web.archive.org/web/20141213140451/https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
#       https://web.archive.org/web/20140221054954/http://home.roadrunner.com/~jgglatt/tech/wave.htm
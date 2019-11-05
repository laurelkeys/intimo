import os
import soundfile as sf
import sounddevice as sd

from sys import argv
from prompt_yes_no import *
from scipy.io.wavfile import write

DTYPE = "int16"

SAMPLE_RATE = 8000 # voice recording

# OUTPUT_FOLDER = os.path.join("D:\\", "Music")
OUTPUT_FOLDER = '.'

filename = argv[1].strip() if len(argv) > 1 else "output"
filename = os.path.join(OUTPUT_FOLDER, filename + ".wav")
if os.path.exists(filename):
    if prompt_yes_no(f"'{filename}' will be overwritten. Continue?", True):
        os.remove(filename)
    else:
        exit()

fs = SAMPLE_RATE
seconds = 3 # duration of recording
recording = sd.rec(frames=int(seconds * SAMPLE_RATE), samplerate=fs, channels=2, dtype=DTYPE)
sd.wait() # wait until recording is finished

print(recording.dtype, recording.shape, recording.min(), recording.max())
write(filename, fs, recording) # save as WAV file

__recording, __fs = sf.read(filename, dtype=DTYPE)
sd.play(__recording, __fs)
status = sd.wait() # wait until file is done playing
print(__recording.dtype, __recording.shape, __recording.min(), __recording.max())

print((recording == __recording).all())

# ref.: https://realpython.com/playing-and-recording-sound-python/
#       http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
#       https://web.archive.org/web/20141213140451/https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
#       https://web.archive.org/web/20140221054954/http://home.roadrunner.com/~jgglatt/tech/wave.htm
import time
import wave
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from openwakeword.model import Model
import openwakeword
from faster_whisper import WhisperModel

WAKE_WORD = "hey jarvis"
WAKE_THRESHOLD = 0.5

KEYWORKDS = [
    "start",
    "stop",
]
    
SAMPLE_RATE = 16000
WAKE_FRAME_SIZE = 1280
COMMAND_SECONDS = 4 # record this many seconds after wake word

openwakeword.utils.download_models()
print("downloading openwakeword models if needed..")


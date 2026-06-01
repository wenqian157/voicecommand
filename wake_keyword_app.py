import time
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from openwakeword.model import Model
import openwakeword
from faster_whisper import WhisperModel
import pyttsx3

# there is an known issue with pyttsx3 2.90 on Windows where it can cause crashes. Downgrading to 2.71 seems to fix it:
# pip uninstall pyttsx3
# pip install pyttsx3==2.71

WAKE_WORD = "hey jarvis" # Try: "hey jarvis", "alexa", "hey mycroft"
WAKE_THRESHOLD = 0.5

KEYWORDS = {
    "start": ["start", "begin", "commence"],
    "stop": ["stop", "halt", "end"],
    "open": ["open", "unlock"],
    "close": ["close", "shut", "lock"],
    "turn on": ["turn on", "activate", "enable"],
    "turn off": ["turn off", "deactivate", "disable"],
    "play": ["play", "resume"],
    "pause": ["pause", "hold"],
    "next": ["next", "skip"],
    "previous": ["previous", "back"],
    'fetch': ['fetch', 'get', 'bring']
}
#region Prep
#-----------------------------
# Settings
#-----------------------------

SAMPLE_RATE = 16000
WAKE_FRAME_SIZE = 1280
COMMAND_SECONDS = 4 # record this many seconds after wake word

openwakeword.utils.download_models()
print("downloading openwakeword models if needed..")

#-----------------------------
# Setup
#-----------------------------

wake_model = Model(wakeword_models=[WAKE_WORD])

print("Loading Whisper model...")
# tiny.en is fast and small for English.
# Use "base.en" for better accuracy but slower.
whisper_model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8"
)

#-----------------------------
# Functions
#----------------------------- 

def record_command(seconds=COMMAND_SECONDS):
    # print(f"Listening for command for {seconds} seconds...")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    return audio.flatten()

def save_temp_wav(audio):
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write(temp_file.name, SAMPLE_RATE, audio)
    return temp_file.name

def transcribe_audio(audio):
    wav_path = save_temp_wav(audio)

    segments, info = whisper_model.transcribe(
        wav_path,
        language="en",
        beam_size=1
    )

    text = " ".join(segment.text for segment in segments).strip()
    return text

def detect_keywords(text):
    text_lower = text.lower()
    found = []

    for intent, phrases in KEYWORDS.items():
        for phrase in phrases:
            if phrase in text_lower:
                found.append(intent)

    return found

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)   

def say(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_wakeword():
    print(f"Listening for wake word: '{WAKE_WORD}'")

    with sd.InputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype="int16",
        blocksize=WAKE_FRAME_SIZE,
    ) as stream:

        while True:
            audio_chunk, _ = stream.read(WAKE_FRAME_SIZE)
            audio_chunk = np.squeeze(audio_chunk)

            prediction = wake_model.predict(audio_chunk)
            score = prediction.get(WAKE_WORD, 0)

            if score > WAKE_THRESHOLD:
                print(f"\nWake word detected! Score: {score:.2f}")
                return
#endregion

try:
    while True:
        listen_for_wakeword()

        time.sleep(0.3)
        say("Yes Yes?")

        command_audio = record_command()
        text = transcribe_audio(command_audio)

        print(f"you said: {text}")

        # keyword 
        keywords = detect_keywords(text)
        
        if keywords:
            print(f"Detected keywords: {keywords[0]}")
            say(f"Ok, I will {keywords[0]}.")
        else:
            print("No keyword detected.")
            say("Sorry, I didn't understand.")
        # Small cooldown before listening again
        time.sleep(1.0)

        # Optional: reset openWakeWord internal state
        try:
            wake_model.reset()
        except AttributeError:
            pass

except KeyboardInterrupt:
    print("\nStopped.")

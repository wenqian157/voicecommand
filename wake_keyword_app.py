import time
import wave
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from openwakeword.model import Model
import openwakeword
from faster_whisper import WhisperModel

WAKE_WORD = "hey jarvis" # Try: "hey jarvis", "alexa", "hey mycroft"
WAKE_THRESHOLD = 0.5

KEYWORDS = [
    "start",
    "stop",
]
    
SAMPLE_RATE = 16000
WAKE_FRAME_SIZE = 1280
COMMAND_SECONDS = 4 # record this many seconds after wake word

openwakeword.utils.download_models()
print("downloading openwakeword models if needed..")

wake_model = Model(wakeword_models=[WAKE_WORD])

print("Loading Whisper model...")
# tiny.en is fast and small for English.
# Use "base.en" for better accuracy but slower.
whisper_model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8"
)

def record_command(seconds=COMMAND_SECONDS):
    print(f"Listening for command for {seconds} seconds...")
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

    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            found.append(keyword)

    return found


# -----------------------------
# Main loop
# -----------------------------

print(f"Listening for wake word: '{WAKE_WORD}'")
print("Press Ctrl+C to stop.")

try:
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

                command_audio = record_command()
                text = transcribe_audio(command_audio)

                print(f"You said: {text}")

                keywords = detect_keywords(text)

                if keywords:
                    print(f"Detected keywords: {keywords}")
                else:
                    print("No keyword detected.")

                print(f"\nListening again for wake word: '{WAKE_WORD}'")

except KeyboardInterrupt:
    print("\nStopped.")
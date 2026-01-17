import sounddevice as sd
import soundfile as sf
import pyttsx3
import os
from datetime import datetime

class VoiceEngine:
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'audio')
        os.makedirs(self.audio_dir, exist_ok=True)

    def record_voice(self, duration=5, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.wav"
        filepath = os.path.join(self.audio_dir, filename)

        samplerate = 44100
        print("Recording...")
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float64')
        sd.wait()
        print("Recording finished.")

        sf.write(filepath, recording, samplerate)
        return filepath

    def generate_ai_voice(self, text, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_voice_{timestamp}.wav"
        filepath = os.path.join(self.audio_dir, filename)

        engine = pyttsx3.init()
        engine.save_to_file(text, filepath)
        engine.runAndWait()

        return filepath
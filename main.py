import io
import os
import pyaudio
import requests
from pypdf import PdfReader


class TextToSpeechConverter:
    def __init__(self, file):
        self.key = os.environ.get('API_KEY')
        self.reader = PdfReader(file)
        self.text_segments = []
        self.response = None

        self.run_app()

    def convert_pdf_into_text(self):
        """API service is limited in length, hence this division in 1000 chars"""
        for x in range(0, len(self.reader.pages)):
            page = self.reader.pages[x]
            text = page.extract_text()
            for y in range(0, len(text), 1000):
                segment = text[y:y + 1000].replace('\n', "")
                self.text_segments.append(segment)

    def covert_text_into_sound_via_api(self, text):
        url = "https://api.voicerss.org/"

        parameters = {
            "key": self.key,
            "src": text,
            "hl": "cs-cz",
            "f": "16khz_16bit_stereo",
        }

        self.response = requests.get(url, params=parameters)

    def play_sound(self):
        audio_data = self.response.content

        wav_file = io.BytesIO(audio_data)
        wav_file.seek(0)

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=2,
                            rate=16000,
                            output=True)
        data = wav_file.read()
        stream.write(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def run_app(self):
        self.convert_pdf_into_text()
        for item in self.text_segments:
            self.covert_text_into_sound_via_api(item)
            if self.response.status_code == 200:
                self.play_sound()


app = TextToSpeechConverter("Proměna - Franz Kafka.pdf")

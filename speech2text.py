import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import queue
import tempfile
import os
from threading import Thread
import torch
import numpy as np
import enum


class AudioModel(enum.Enum):
    TINY = 'tiny'
    BASE = 'base'
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class Speech2Text:
    audio_queue = queue.Queue()
    transcribe_queue = queue.Queue()

    def __init__(self):
        self.model = AudioModel.BASE.value

    def start(self, english=True):
        model = self.model
        if model != "large" and english:
            model = model + ".en"
        audio_model = whisper.load_model(model)

        record = Record(Speech2Text.audio_queue)
        record.start()

        transcribe = Transcribe(audio_model, Speech2Text.audio_queue, Speech2Text.transcribe_queue, english=english)
        transcribe.start()


class Record(Thread):
    def __init__(self, audio_queue, energy=300, pause=0.8, dynamic_energy=False, save_file=False):
        Thread.__init__(self)
        self.audio_queue = audio_queue
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.save_file = save_file
        self.temp_dir = tempfile.mkdtemp() if save_file else None

    def run(self):
        self.record_audio()

    def set_pause(self, pause):
        self.pause = pause

    def get_pause(self):
        return self.pause

    def set_energy(self, energy):
        self.energy = energy

    def get_energy(self):
        return self.energy

    def set_dynamic_energy(self, flag):
        self.dynamic_energy = flag

    def get_dynamic_energy(self):
        return self.dynamic_energy

    def set_last_audio(self, audio):
        self.audio_queue.put_nowait(audio)

    def get_last_audio(self):
        return self.audio_queue.get()

    def record_audio(self):
        r = sr.Recognizer()
        r.energy_threshold = self.get_energy()
        r.pause_threshold = self.get_pause()
        r.dynamic_energy_threshold = self.get_dynamic_energy()

        with sr.Microphone(sample_rate=16000) as source:
            print("Say something!")
            i = 0
            while True:
                audio = r.listen(source)
                if self.save_file:
                    data = io.BytesIO(audio.get_wav_data())
                    audio_clip = AudioSegment.from_file(data)
                    filename = os.path.join(self.temp_dir, f"temp{i}.wav")
                    audio_clip.export(filename, format="wav")
                    audio_data = filename
                else:
                    torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                    audio_data = torch_audio

                self.set_last_audio(audio_data)
                i += 1


class Transcribe(Thread):
    def __init__(self, audio_model, audio_queue, transcribe_queue, save_file=False, english=True):
        Thread.__init__(self)
        self.transcribe_queue = transcribe_queue
        self.audio_model = audio_model
        self.audio_queue = audio_queue
        self.english = english
        self.save_file = save_file

    def run(self):
        self.transcribe_forever()

    def set_audio_model(self, model):
        self.audio_model = model

    def get_audio_model(self):
        return self.audio_model

    def get_last_transcribe(self):
        if self.transcribe_queue.qsize() > 0:
            return self.transcribe_queue.get()

    def set_last_transcribe(self, transcribe):
        transcribe = transcribe['text']
        transcribe = transcribe.strip()
        if len(transcribe) > 1:
            self.transcribe_queue.put_nowait(transcribe)

    def get_audio_data(self):
        return self.audio_queue.get()

    def transcribe_forever(self):
        while True:
            audio_data = self.get_audio_data()
            if self.english:
                result = self.audio_model.transcribe(audio_data, language='english')
            else:
                result = self.audio_model.transcribe(audio_data)

            self.set_last_transcribe(result)

            if self.save_file:
                self.remove(audio_data)

    def remove(self, audio_data):
        os.remove(audio_data)
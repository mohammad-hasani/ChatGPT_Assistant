from TTS.api import TTS


class Text2Speech:
    def __init__(self):
        self.model_name = TTS.list_models()[7]
        self.tts = TTS(self.model_name)

    def convert(self, text):
        filepath = 'output.wav'
        self.tts.tts_to_file(text=text, file_path=filepath)

        return filepath
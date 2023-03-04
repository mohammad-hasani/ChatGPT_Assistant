from text2speech import Text2Speech
import wave
import pyaudio


class Player():
    def __init__(self):
        pass

    def play(self, sound):
        p = pyaudio.PyAudio()

        with wave.open(sound, 'rb') as wave_file:
            sample_rate = wave_file.getframerate()
            n_channels = wave_file.getnchannels()
            sample_width = wave_file.getsampwidth()
            n_frames = wave_file.getnframes()
            data = wave_file.readframes(n_frames)

            stream = p.open(format=p.get_format_from_width(sample_width),
                            channels=n_channels,
                            rate=sample_rate,
                            output=True)

            stream.start_stream()
            stream.write(data)
            stream.stop_stream()
            stream.close()

        p.terminate()
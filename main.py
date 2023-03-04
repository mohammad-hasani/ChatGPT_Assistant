from speech2text import Speech2Text
from openAIWrapper import ChatGPT, api_key
from text2speech import Text2Speech
from player import Player


#Do FFT to reduce noise 


def main():
    s2t = Speech2Text()
    s2t.start()
    gpt = ChatGPT(api_key)
    t2s = Text2Speech()
    media_player = Player()
    while True:
        transcribed = Speech2Text.transcribe_queue.get()
        print('-------' + transcribed)
        response = gpt.ask(transcribed)
        sound = t2s.convert(response)
        media_player.play(sound)


if __name__ == '__main__':
    main()
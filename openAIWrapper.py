import openai
import enum
from threading import Thread
import random


api_key = 'OpenAI API Key Goes Here'


class EngineType(enum.Enum):
    TEXT_DAVINVI_003 = 'text-davinci-003'
    CODE_DAVINCI_002 = 'code-davinci-002'


class ChatGPT():
    def __init__(self, api_key=None, engine=EngineType.TEXT_DAVINVI_003.value):
        Thread.__init__(self)
        self.api_key = ''
        self.set_api_key(api_key)
        self.model_engine = engine
        self.stop = None
        self.history = list()
        self.conversation_id = self.get_random_conversation_id()

    def set_api_key(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def set_engine(self, engine):
        self.model_engine = engine

    def get_engine(self):
        return self.model_engine

    def get_random_conversation_id(self):
        rnd = random.random()
        rnd = str(rnd)
        rnd = rnd.split('.')[1]
        return rnd

    def append_to_history(self, sender, message):
        m = sender + ': ' + message
        self.history.append(m)

    def get_history(self):
        prompt = '\n'.join(self.history)
        while len(prompt) > 2500:
            del self.history[0]
            prompt = '\n'.join(self.history)

        return prompt

    def split_message_part(self, message):
        try:
            return message.split(':')[1]
        except:
            return message


    def ask(self, prompt):
        self.append_to_history('You', prompt)

        completion = openai.Completion.create(
            engine=self.get_engine(),
            prompt=self.get_history(),
            max_tokens=2048,
            n=1,
            stop=self.stop,
            temperature=0.5,
        )

        message = completion.choices[0].text
        self.append_to_history('GPT-3', message)
        return self.split_message_part(message)


def main():
    model = ChatGPT(api_key)
    while True:
        prompt = input('>')
        message = model.ask(prompt)
        print(message)


if __name__ == '__main__':
    main()
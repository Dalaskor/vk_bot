#!/usr/bin/env python3
from random import randint

from _token import token
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

RAND_MIN = 0
RAND_MAX = 2147483647
group_id = 213300834

class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)

        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            print("===Get Event===")
            try:
                self.on_event(event)
            except Exception as err:
                print(err)

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            print("Type:", event.type)
            print("Message:", event.obj["message"]["text"])
            # print(event.obj)

            rand_id = randint(RAND_MIN, RAND_MAX)
            usr_id = event.obj["message"]["from_id"]
            msg_text = event.obj["message"]["text"]

            self.api.messages.send(random_id=rand_id, user_id=usr_id, message=msg_text)
        else:
            print("SKIP", event.type)

if __name__ == "__main__":
    bot = Bot(group_id, token)
    bot.run()
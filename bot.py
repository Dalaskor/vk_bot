#!/usr/bin/env python3

import logging
from random import randint

from _token import token
import vk_api # TODO fix version!!
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

RAND_MIN = 0
RAND_MAX = 2147483647
group_id = 213300834

log = logging.getLogger("bot")

def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("bot.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)

class Bot:
    """
    Echo bot for vk.com

    Use pyhton3.7
    """
    def __init__(self, group_id, token):
        """

        :param group_id: group id from vk group
        :param token: secret token from vk group
        """
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)

        self.api = self.vk.get_api()

    def run(self):
        """Launch bot."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception("Error event")

    def on_event(self, event: VkBotEventType):
        """Send message back, if message is string

            :param event: TODO
            :return: None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.info("Send message")

            rand_id = randint(RAND_MIN, RAND_MAX)
            usr_id = event.obj["message"]["from_id"]
            msg_text = event.obj["message"]["text"]

            self.api.messages.send(random_id=rand_id,
                                   user_id=usr_id,
                                   message=msg_text)
        else:
            log.info(f"SKIP {event.type}")

if __name__ == "__main__":
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
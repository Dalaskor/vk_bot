#!/usr/bin/env python3

import logging
import random

import handlers
from random import randint

try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token!')

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

RAND_MIN = 0
RAND_MAX = 2147483647

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

class UserState:
    """Состояние пользователя внутри сценария."""
    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}

class Bot:
    """
    Сценарий регистрации на конференцию через vk.com
    Use pyhton3.7

    Поддерживает ответы на вопросы про дату, место проведения и сценарий регистрации:
    - спрашиваем имя
    - спрашиваем email
    - говорим об успешной регистрации
    Если шаг не пройден, задаем уточняющий вопрос пока шаг не будет пройден.
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
        self.user_states = dict() # user_id (peer_id)

    def run(self):
        """Launch bot."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception("Error event")

    def on_event(self, event: VkBotEventType):
        """Send message back, if message is string

            :param event: VkBotMessageEvent object
            :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info(f"SKIP {event.type}")
            return

        user_id = event.obj['message']['peer_id']
        text = event.obj['message']['text']

        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, text)
        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text for token in intent['tokens']):
                    # run intent
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
                else:
                    text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id
        )

    def start_scenario(self, user_id, scenarion_name):
        scenario = settings.SCENARIOS[scenarion_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenarion_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                self.user_states.pop(user_id)
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)

        return text_to_send


if __name__ == "__main__":
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    configure_logging()
    bot.run()
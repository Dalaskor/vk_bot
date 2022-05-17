from random import randint
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot


class Test1(TestCase):
    RAW_EVENT = {'group_id': 213300834, 'type': 'message_new', 'event_id': 'd74bb1eec3e2d4e6a64cc2d7c91e15d48e75fc67', 'v': '5.131', 'object': {
        'message': {
            'date': 1652796229, 'from_id': 703794378, 'id': 74, 'out': 0, 'attachments': [], 'conversation_message_id': 70, 'fwd_messages': [], 'important': False, 'is_hidden': False, 'peer_id': 703794378, 'random_id': 0, 'text': 'unit test'
        }, 'client_info': {
            'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 3
        }}}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count # [{}, {}, ...]
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('','')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    def test_on_event(self ):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll'):
                bot = Bot('','')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            random_id=ANY,
            user_id=self.RAW_EVENT['object']['message']['from_id'],
            message=self.RAW_EVENT['object']['message']['text']
        )
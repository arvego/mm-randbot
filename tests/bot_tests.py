#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import telebot
import pytest

token = os.getenv('TG_TOKEN')
chat_id = os.getenv('TG_CHATID')

if token is None or chat_id is None:
    pytest.fail(msg="Environment vars TG_TOKEN and TG_CHATID should be set")

my_bot = telebot.TeleBot(token, threaded=True)


def test_example():
    assert True is True

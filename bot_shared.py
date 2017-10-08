#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
import time
from builtins import any

# Сторонние модули
import telebot

# Модули проекта
from data import constants
from data import tokens

# Инициализация бота
my_bot = telebot.TeleBot(tokens.bot, threaded=False)
my_bot_name = '@' + my_bot.get_me().username


def commands_handler(cmnds, inline=False):
    def wrapped(msg):
        if not msg.text:
            return False
        split_message = re.split(r'[^\w@/]', msg.text.lower())
        if not inline:
            s = split_message[0]
            return ((s in cmnds)
                    or (s.endswith(my_bot_name) and s.split('@')[0] in cmnds))
        else:
            return any(cmnd in split_message
                       or cmnd + my_bot_name in split_message
                       for cmnd in cmnds)

    return wrapped


def user_action_log(message, text):
    print("{0}\nUser {1} (@{2}) {3}\n".format(time.strftime(data.constants.time, time.gmtime()), message.from_user.id,
                                              message.from_user.username, text))

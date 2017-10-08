#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
import time
from builtins import any

# сторонние модули
import telebot

# модуль с настройками
import data
# модуль с токенами
import tokens

# бот
my_bot = telebot.TeleBot(tokens.bot, threaded=False)
my_bot_name = '@' + my_bot.get_me().username


# new command handler function
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
    print("{0}\nUser {1} (@{2}) {3}\n".format(time.strftime(data.time, time.gmtime()),
                                              message.from_user.id,
                                              message.from_user.username,
                                              text))

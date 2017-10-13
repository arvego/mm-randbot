#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
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
    def wrapped(message):
        if not message.text:
            return False
        split_message = re.split(r'[^\w@/]', message.text.lower())
        if not inline:
            s = split_message[0]
            return ((s in cmnds)
                    or (s.endswith(my_bot_name) and s.split('@')[0] in cmnds))
        else:
            return any(cmnd in split_message
                       or cmnd + my_bot_name in split_message
                       for cmnd in cmnds)

    return wrapped

def is_command():
    def wrapped(message):
        if not message.text or not message.text.startswith('/'):
            return False
        return True
    return wrapped

# Декораторы команд для разграничения прав доступа
def bot_admin_command(func):
    def wrapped(message):
        if message.from_user.id in constants.admin_ids:
          return func(message)
        return
    return wrapped

# TODO (@uburuntu): Cache result for 5 min
def chat_admin_command(func):
    def wrapped(message):
        if message.from_user.id in my_bot.get_chat_administrators(constants.my_chatID):
            return func(message)
        return
    return wrapped

# TODO: добавить аргументы для ограничения по количеству вызовов и т.п.
def command_with_delay(delay=10):
    def my_decorator(func):
        def wrapped(message):
            if not hasattr(func, "last_call"):
              func.last_call = datetime.datetime.utcnow() - datetime.timedelta(seconds=delay + 1)
            diff = datetime.datetime.utcnow() - func.last_call
            if diff.total_seconds() < delay:
                user_action_log(message, "attempted to call {} after {} ({}) seconds".format(func, diff.total_seconds(), delay))
                return
            func.last_call = datetime.datetime.utcnow()

            return func(message)
        return wrapped
    return my_decorator


def user_action_log(message, text):
    print("{0}\nUser {1} (@{2}) {3}\n".format(time.strftime(constants.time, time.gmtime()), message.from_user.id,
                                              message.from_user.username, text))

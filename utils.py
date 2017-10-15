#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
import re
import time
from builtins import any

import telebot

import config
import tokens

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


def user_action_log(message, text):
    print("{0}\nUser {1} (@{2}) {3}\n".format(time.strftime(config.time, time.gmtime()), message.from_user.id,
                                              message.from_user.username, text))


def is_command():
    def wrapped(message):
        if not message.text or not message.text.startswith('/'):
            return False
        return True

    return wrapped


# Декораторы команд для разграничения прав доступа
def bot_admin_command(func):
    def wrapped(message):
        if message.from_user.id in config.admin_ids:
            return func(message)
        return

    return wrapped


# TODO (@uburuntu): Cache result for 5 min
def chat_admin_command(func):
    def wrapped(message):
        if message.from_user.id in my_bot.get_chat_administrators(config.my_chatID):
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
                user_action_log(message,
                                "attempted to call {} after {} ({}) seconds".format(func, diff.total_seconds(), delay))
                return
            func.last_call = datetime.datetime.utcnow()

            return func(message)

        return wrapped

    return my_decorator


def cut_long_text(text, max_len=4000):
    '''
    Функция для нарезки длинных сообщений по переносу строк или по точке в конце предложения
    :param text: тескт для нарезки
    :param max_len: длина, которую нельзя превышать
    :return: список текстов меньше max_len, суммарно дающий text
    '''
    last_cut = 0
    dot_anchor = 0
    nl_anchor = 0

    if len(text) < max_len:
        yield text[last_cut:]
        return

    for i in range(len(text)):
        if text[i] == '\n':
            nl_anchor = i + 1
        if text[i] == '.' and text[i + 1] == ' ':
            dot_anchor = i + 2

        if i - last_cut > max_len:
            if nl_anchor > last_cut:
                yield text[last_cut:nl_anchor]
                last_cut = nl_anchor
            elif dot_anchor > last_cut:
                yield text[last_cut:dot_anchor]
                last_cut = dot_anchor
            else:
                yield text[last_cut:i]
                last_cut = i

            if len(text) - last_cut < max_len:
                yield text[last_cut:]
                return

    yield text[last_cut:]


def value_from_file(file_name, default=0):
    value = default
    with open(file_name, 'r', encoding='utf-8') as file:
        file_data = file.read()
        if file_data.isdigit():
            value = int(file_data)
    return value


def value_to_file(file_name, value):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(value)

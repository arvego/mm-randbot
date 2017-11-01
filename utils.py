#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import pickle
import re
import threading
import time
from builtins import any
from datetime import datetime, timedelta
from os import path

import telebot

import config
import tokens

# Инициализация бота
my_bot = telebot.TeleBot(tokens.bot, threaded=True)
my_bot_name = '@' + my_bot.get_me().username

global_lock = threading.Lock()  # TODO: bad, temporary

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


def curr_time():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def user_info(user):
    # Required fields
    user_id = str(user.id)
    first_name = user.first_name
    # Optional fields
    last_name = ' ' + user.last_name if isinstance(user.last_name, str) else ''
    username = ', @' + user.username if isinstance(user.username, str) else ''
    language_code = ', ' + user.language_code if isinstance(user.language_code, str) else ''
    # Output
    return user_id + ' (' + first_name + last_name + username + language_code + ')'


def chat_info(chat):
    if chat.type == 'private':
        return 'private'
    else:
        return chat.type + ': ' + chat.title + ' (' + str(chat.id) + ')'


def action_log(text):
    print("{}\n{}\n".format(curr_time(), text))


def user_action_log(message, text):
    print("{}, {}\nUser {} {}\n".format(curr_time(), chat_info(message.chat), user_info(message.from_user), text))


def is_command():
    def wrapped(message):
        if not message.text or not message.text.startswith('/'):
            return False
        return True

    return wrapped


def chat_admins():
    if not config.debug_mode:
        return [admin.user.id for admin in my_bot.get_chat_administrators(config.my_chatID)] + [207275675]
    else:
        return config.admin_ids


def chat_admin_command(func):
    def wrapped(message):
        if message.from_user.id in chat_admins():
            return func(message)
        return

    return wrapped


def bot_admin_command(func):
    def wrapped(message):
        if message.from_user.id in config.admin_ids:
            return func(message)
        return

    return wrapped


# TODO: добавить аргументы для ограничения по количеству вызовов и т.п.
def command_with_delay(delay=10):
    def my_decorator(func):
        def wrapped(message):
            if message.chat.type != 'private':
                now = datetime.now().timestamp()
                diff = now - func.last_call if hasattr(func, 'last_call') else now
                if diff < delay:
                    user_action_log(message, "called {} after {} sec, delay is {}".format(func, round(diff), delay))
                    return
                func.last_call = now

            return func(message)

        return wrapped

    return my_decorator


def cut_long_text(text, max_len=4500):
    """
    Функция для нарезки длинных сообщений по переносу строк или по точке в конце предложения
    :param text: тескт для нарезки
    :param max_len: длина, которую нельзя превышать
    :return: список текстов меньше max_len, суммарно дающий text
    """
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
    if path.isfile(file_name):
        global_lock.acquire()
        with open(file_name, 'r', encoding='utf-8') as file:
            file_data = file.read()
            if file_data.isdigit():
                value = int(file_data)
        global_lock.release()
    return value


def value_to_file(file_name, value):
    global_lock.acquire()
    with open(file_name, 'w+', encoding='utf-8') as file:
        file.write(str(value))
    global_lock.release()


def dump_message(message):
    chat_name = message.chat.title if isinstance(message.chat.title, str) else message.chat.username
    if not chat_name:
        chat_name = ''
    dump_filename = config.my_gen_dir + 'dump/chat' + str(abs(message.chat.id)) + '_' + '_'.join(
        chat_name.lower().replace('/', '_').split()) + '_dump.pickle'

    global_lock.acquire()
    if path.isfile(dump_filename):
        with open(dump_filename, 'rb') as f:
            messages = pickle.load(f)
    else:
        messages = []
    messages.append(message)
    with open(dump_filename, 'wb+') as f:
        pickle.dump(messages, f, pickle.HIGHEST_PROTOCOL)

    global_lock.release()
    if len(messages) % 1000 == 0:
        print("Dump size: {}".format(len(messages)))

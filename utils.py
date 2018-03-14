#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import pickle
import re
import threading
from builtins import any
from datetime import datetime
from os import path

import telebot
from apscheduler.schedulers.background import BackgroundScheduler

import config
import tokens

# Инициализация бота
# Note: Многопоточность намеренно отключена из-за возникающего бага
#       с RecursionError внутри библиотеки Telebot
my_bot = telebot.TeleBot(tokens.bot, threaded=False)
my_bot_name = '@' + my_bot.get_me().username
scheduler = BackgroundScheduler()
scheduler.start()

# TODO: Удалить тред-локи, если не будет необходимости включить многопоточность
global_lock = threading.Lock()  # TODO: bad, temporary
message_dump_lock = threading.Lock()


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


class TimeMemoize(object):
    """Memoize with timeout"""
    _caches = {}
    _delays = {}

    def __init__(self, delay=10):
        self.delay = delay

    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (datetime.now().timestamp() - self._caches[func][key][1]) < self._delays[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._delays[f] = self.delay

        def func(*args, **kwargs):
            kw = sorted(kwargs.items())
            key = (args, tuple(kw))
            time = datetime.now().timestamp()
            try:
                v = self.cache[key]
                if (time - v[1]) > self.delay:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args, **kwargs), time
            return v[0]

        func.func_name = f.__name__
        return func


@TimeMemoize(delay=2 * 60)
def chat_admins():
    if not config.debug_mode:
        return [admin.user.id for admin in my_bot.get_chat_administrators(config.mm_chat)] + [207275675]
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


def cut_long_text(text, max_len=4250):
    """
    Функция для нарезки длинных сообщений по переносу строк или по точке в конце предложения или по пробелу
    :param text: тескт для нарезки
    :param max_len: длина, которую нельзя превышать
    :return: список текстов меньше max_len, суммарно дающий text
    """
    last_cut = 0
    space_anchor = 0
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
        if text[i] == ' ':
            space_anchor = i

        if i - last_cut > max_len:
            if nl_anchor > last_cut:
                yield text[last_cut:nl_anchor]
                last_cut = nl_anchor
            elif dot_anchor > last_cut:
                yield text[last_cut:dot_anchor]
                last_cut = dot_anchor
            elif space_anchor > last_cut:
                yield text[last_cut:space_anchor]
                last_cut = space_anchor
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


def dump_messages(all_messages):
    if not hasattr(dump_messages, "dumps"):
        dump_messages.dumps = {}
        dump_messages.dumps_counter = {}

    groups = {}
    for message in all_messages:
        dump_filename = config.dump_dir + 'dump_' + message.chat.type + '_' + str(message.chat.id) + '.pickle'
        if dump_filename in groups:
            lst = groups[dump_filename]
        else:
            lst = []
            groups[dump_filename] = lst
        lst.append(message)

    message_dump_lock.acquire()
    for dump_filename, messages in groups.items():
        if dump_filename in dump_messages.dumps:
            dump_messages.dumps[dump_filename].extend(messages)
        elif path.isfile(dump_filename):
            with open(dump_filename, 'rb+') as f:
                try:
                    dump_messages.dumps[dump_filename] = pickle.load(f)
                except EOFError:
                    dump_messages.dumps[dump_filename] = []
            dump_messages.dumps[dump_filename].extend(messages)
        else:
            dump_messages.dumps[dump_filename] = messages

        if dump_filename in dump_messages.dumps_counter:
            dump_messages.dumps_counter[dump_filename] += 1
        else:
            dump_messages.dumps_counter[dump_filename] = 1
        if dump_messages.dumps_counter[dump_filename] % config.dump_frequency == 0:
            with open(dump_filename, 'wb+') as f:
                pickle.dump(dump_messages.dumps[dump_filename], f, pickle.HIGHEST_PROTOCOL)
            print('Messages dumped into {}'.format(dump_filename))
    message_dump_lock.release()


def char_escaping(text, mode='html'):
    # TODO: markdown
    if mode == 'html':
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
    return text


def compress_msgs(message, target_user, target_fname, target_lname, num):
    count = 0
    shithead_msg = ''
    # Идём в наш pickle-файл
    dump_filename = config.dump_dir + 'dump_' + message.chat.type + '_' + str(message.chat.id) + '.pickle'
    # Проверка на то, что наше N не превосходит допустимого максимума
    if num > config.compress_num_max:
        return
    message_dump_lock.acquire()

    if dump_filename in dump_messages.dumps:
        msgs_from_db = dump_messages.dumps[dump_filename]
    elif path.isfile(dump_filename):
        with open(dump_filename, 'rb') as f:
            try:
                dump_messages.dumps[dump_filename] = pickle.load(f)
            except EOFError:
                dump_messages.dumps[dump_filename] = []
        msgs_from_db = dump_messages.dumps[dump_filename]
    else:
        msgs_from_db = []
    message_dump_lock.release()
    # Анализируем предыдущие сообщения от позднего к раннему на наличие текста
    # от нашего флудера
    if ((message.from_user.username == target_user) or \
        (message.from_user.first_name == target_fname and \
        message.from_user.last_name == target_lname)) and \
        message.text.startswith('/compress'):
        num_min = 2
    else:
        num_min = 1
    for i in range(num_min, config.compress_num_max + 1):
        msg_from = msgs_from_db[-i].from_user.username
        msg_from_fname = msgs_from_db[-i].from_user.first_name
        msg_from_lname = msgs_from_db[-i].from_user.last_name
        if (msg_from == target_user) or (msg_from_fname == target_fname and msg_from_lname == target_lname):
            msg_id = msgs_from_db[-i].message_id
            try:
                my_bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                count += 1
                # Если есть какой-то текст, то сохраняем его
                if not msgs_from_db[-i].text is None:
                    msg_text = msgs_from_db[-i].text
                else:
                    msg_text = ''
                try:
                    msg_text = "<i>Стикер:</i> {}".format(msgs_from_db[-i].sticker.emoji)
                except Exception:
                    pass
                shithead_msg = msg_text + ' ' + shithead_msg
            except Exception:
                logging.exception("del message")
        if count >= num:
            break
    shithead_msg = '<i>{}{} {} тут высрал:</i>\n'.format(target_user, target_fname, target_lname) + shithead_msg
    my_bot.send_message(message.chat.id, shithead_msg, parse_mode="HTML")
    # my_bot.reply_to(message, shithead_msg, parse_mode="HTML")

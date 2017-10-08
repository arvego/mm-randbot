#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
import random
import sys

# сторонние модули
import pytz

# модуль с настройками
import data.constants
# shared bot parts
from bot_shared import my_bot

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def morning_msg():
    # TODO: добавить генерацию разных вариантов приветствий
    text = ''

    text += 'Доброе утро, народ!'
    # TODO: Проверять на наличие картинки
    text += ' [😺](https://t.me/funkcat/{})'.format(random.randint(1, 730))
    text += '\n'

    month_names = [u'января', u'февраля', u'марта',
                   u'апреля', u'мая', u'июня',
                   u'июля', u'августа', u'сентября',
                   u'октября', u'ноября', u'декабря']

    weekday_names = [u'понедельник', u'вторник', u'среда', u'четверг', u'пятница', u'суббота', u'воскресенье']

    now = datetime.now(pytz.timezone('Europe/Moscow'))

    text += 'Сегодня *{} {}*, *{}*.'.format(now.day, month_names[now.month - 1], weekday_names[now.weekday()])
    text += '\n\n'

    text += 'Котик дня:'

    # Отправить и запинить сообщение без уведомления
    msg = my_bot.send_message(data.my_chatID, text, parse_mode="Markdown", disable_web_page_preview=False)
    # TODO: Раскомментировать строчку, когда функция начнет делать что-то полезное
    # my_bot.pin_chat_message(data.my_chatID, msg.message_id, disable_notification=True)

    print('{}\nScheduled message sent\n'.format(now.strftime(data.time)))

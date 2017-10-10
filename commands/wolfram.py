#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import io
import sys
import time

# сторонние модули
import requests
from PIL import Image

# модуль с настройками
import data.constants
from bot_shared import my_bot, user_action_log
# модуль с токенами
from data import tokens

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def wolframSolver(message):
    '''
    обрабатывает запрос и посылает пользователю картинку с результатом в случае удачи
    :param message:
    :return:
    '''
    # сканируем и передаём всё, что ввёл пользователь после '/wolfram ' или '/wf '
    if not len(message.text.split()) == 1:
        my_bot.send_chat_action(message.chat.id, 'upload_photo')
        your_query = ' '.join(message.text.split()[1:])
        user_action_log(message,
                        "entered this query for /wolfram:\n"
                        "{0}".format(your_query))
        response = requests.get("https://api.wolframalpha.com/v1/simple?appid="
                                + tokens.wolfram,
                                params={'i': your_query})
        # если всё хорошо, и запрос найден
        if response.status_code == 200:
            img_original = Image.open(io.BytesIO(response.content))
            img_cropped = img_original.crop((0, 95, 540,
                                             img_original.size[1] - 50))
            print("{}  {}".format(img_cropped.size[0], img_cropped.size[1]))
            temp = io.BytesIO()
            img_cropped.save(temp, format="png")
            temp.seek(0)
            if img_cropped.size[1] / img_cropped.size[0] > data.constants.wolfram_max_ratio:
                print("Big image here.")
                my_bot.send_document(message.chat.id, temp,
                                     reply_to_message_id=message.message_id)
            else:
                my_bot.send_photo(message.chat.id, temp,
                                  reply_to_message_id=message.message_id)
                user_action_log(message,
                                "has received this Wolfram output:\n"
                                "{0}".format(response.url))
        # если всё плохо
        else:
            my_bot.reply_to(message,
                            "Запрос не найдён.\nЕсли ты ввёл его на русском, "
                            "то попробуй ввести его на английском.")
            user_action_log(message,
                            "didn't received any data".format(time.strftime(
                                data.constants.time,
                                time.gmtime()),
                                message.from_user.id))
            # если пользователь вызвал /wolfram без аргумента
    else:
        my_bot.reply_to(message,
                        "Я не понял запрос.\nДля вызова Wolfram вводи команду "
                        "в виде `/wolfram <запрос>` или `/wf <запрос>`.")
        user_action_log(message, "called /wolfram without any arguments")

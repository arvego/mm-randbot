#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import io
import sys

import requests
from PIL import Image
from telebot import types

import config
import tokens
from utils import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


wolfram_max_ratio = 2.5


def wolfram_parser(query):
    splited_query = query.split(maxsplit=1)
    if len(splited_query) <= 1:
        return 0, None, None

    response = requests.get("https://api.wolframalpha.com/v1/simple?appid=" + tokens.wolfram,
                            params={'i': splited_query[1]})

    if response.status_code == 200:
        img_original = Image.open(io.BytesIO(response.content))
        img_cropped = img_original.crop((0, 95, 540, img_original.size[1] - 50))
        io_img = io.BytesIO()
        io_img.name = "wolfram {}.png".format(query.replace("/", "_"))
        img_cropped.save(io_img, format="png")
        io_img.seek(0)

        return 1, io_img, img_cropped.size[1] / img_cropped.size[0]

    else:
        return -1, None, None


def wolfram_command(message):
    code, result, ratio = wolfram_parser(message.text)

    if code == 1:
        my_bot.send_chat_action(message.chat.id, 'upload_photo')
        if ratio > wolfram_max_ratio:
            my_bot.send_document(message.chat.id, result, reply_to_message_id=message.message_id)
        else:
            my_bot.send_photo(message.chat.id, result, reply_to_message_id=message.message_id)

    elif code == -1:
        my_bot.reply_to(message, "Запрос не найдён.\nЕсли ты ввёл его на русском, "
                                 "то попробуй ввести его на английском.")

    else:
        my_bot.reply_to(message, "Использование: `/wolfram <запрос>` или `/wf <запрос>`", parse_mode="Markdown")


def wolfram_inline(query):
    code, result, ratio = wolfram_parser(query.query)

    if code == 1:
        if ratio > wolfram_max_ratio:
            d = my_bot.send_document(config.reacheight_chatID, result)
            r = types.InlineQueryResultCachedDocument(id='1', title=result.name,
                                                      document_file_id=d.document.file_id)
            my_bot.answer_inline_query(query.id, [r])

        else:
            p = my_bot.send_photo(config.reacheight_chatID, result)
            r = types.InlineQueryResultCachedPhoto(id='1', photo_file_id=p.photo[-1].file_id)
            my_bot.answer_inline_query(query.id, [r])
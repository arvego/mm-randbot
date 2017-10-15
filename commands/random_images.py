#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import sys

import config
from utils import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


# TODO: refactor

def rand_image_task(message):
    path = config.dir_location_task
    difficulty = ["1", "2", "3"]

    user_action_log(message, "asked for a challenge")
    if not len(message.text.split()) == 1:
        your_difficulty = message.text.split()[1]
        if your_difficulty in difficulty:
            all_imgs = os.listdir(path)
            rand_img = random.choice(all_imgs)
            while not rand_img.startswith(your_difficulty):
                rand_img = random.choice(all_imgs)
            your_img = open(path + rand_img, "rb")
            my_bot.send_photo(message.chat.id, your_img,
                              reply_to_message_id=message.message_id)
            user_action_log(message,
                            "chose a difficulty level '{0}' "
                            "and got that image:\n{1}".format(your_difficulty, your_img.name))
            your_img.close()
        else:
            my_bot.reply_to(message,
                            "Доступно только три уровня сложности:\n"
                            "{0}"
                            "\nВыбираю рандомную задачу:".format(difficulty))
            all_imgs = os.listdir(path)
            rand_img = random.choice(all_imgs)
            your_img = open(path + rand_img, "rb")
            my_bot.send_photo(message.chat.id, your_img,
                              reply_to_message_id=message.message_id)
            user_action_log(message,
                            "chose a non-existent difficulty level '{0}' "
                            "and got that image:\n{1}".format(your_difficulty, your_img.name))
            your_img.close()
    else:
        all_imgs = os.listdir(path)
        rand_img = random.choice(all_imgs)
        your_img = open(path + rand_img, "rb")
        my_bot.send_photo(message.chat.id, your_img,
                          reply_to_message_id=message.message_id)
        user_action_log(message,
                        "got that image:\n{0}".format(your_img.name))
        your_img.close()


def rand_image_maths(message):
    path = config.dir_location_maths
    subjects = ["algebra", "calculus", "funcan"]

    user_action_log(message, "asked for maths")
    if not len(message.text.split()) == 1:
        your_subject = message.text.split()[1].lower()
        if your_subject in subjects:
            all_imgs = os.listdir(path)
            rand_img = random.choice(all_imgs)
            while not rand_img.startswith(your_subject):
                rand_img = random.choice(all_imgs)
            your_img = open(path + rand_img, "rb")
            my_bot.send_photo(message.chat.id, your_img,
                              reply_to_message_id=message.message_id)
            user_action_log(message,
                            "chose subject '{0}' "
                            "and got that image:\n"
                            "{1}".format(your_subject, your_img.name))
            your_img.close()
        else:
            my_bot.reply_to(message,
                            "На данный момент доступны факты"
                            " только по следующим предметам:\n{0}\n"
                            "Выбираю рандомный факт:".format(subjects)
                            )
            all_imgs = os.listdir(path)
            rand_img = random.choice(all_imgs)
            your_img = open(path + rand_img, "rb")
            my_bot.send_photo(message.chat.id, your_img,
                              reply_to_message_id=message.message_id)
            user_action_log(message,
                            "chose a non-existent subject '{0}' "
                            "and got that image:\n"
                            "{1}".format(your_subject, your_img.name))
            your_img.close()
    else:
        all_imgs = os.listdir(path)
        rand_img = random.choice(all_imgs)
        your_img = open(path + rand_img, "rb")
        my_bot.send_photo(message.chat.id, your_img,
                          reply_to_message_id=message.message_id)
        user_action_log(message,
                        "got that image:\n{0}".format(your_img.name))
        your_img.close()


# идёт в соответствующую папку и посылает рандомную картинку
def my_rand_img(message):
    for command in str(message.text).lower().split():
        if command.startswith('/task'):
            rand_image_task(message)
        elif command.startswith('/maths'):
            rand_image_maths(message)

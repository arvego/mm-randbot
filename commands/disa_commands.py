#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import random
import sys
import time

import vk_api

import config
import tokens
from utils import my_bot, user_action_log, action_log, global_lock

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def disa_vk_report(disa_chromo, message):
    login, password = tokens.vk_disa_login, tokens.vk_disa_password
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()
    wall = vk.wall.get(owner_id=config.vk_disa_groupID, count=1)
    if time.localtime(wall['items'][0]['date'])[2] == time.localtime()[2]:
        disa_chromo_post = disa_chromo - 46
        try:
            old_chromo = int(wall['items'][0]['text'])
            disa_chromo_post += old_chromo
        except Exception as ex:
            logging.error(ex)
            disa_chromo_post = disa_chromo
        vk.wall.edit(owner_id=config.vk_disa_groupID,
                     post_id=wall['items'][0]['id'],
                     message=str(disa_chromo_post))
    else:
        disa_chromo_post = 46 + disa_chromo
        vk.wall.post(owner_id=config.vk_disa_groupID,
                     message=str(disa_chromo_post))

    if 1 < disa_chromo - 46 % 10 < 5:
        chromo_end = "ы"
    elif disa_chromo - 46 % 10 == 1:
        chromo_end = "а"
    else:
        chromo_end = ""

    my_bot.reply_to(message,
                    "С последнего репорта набежало {0} хромосом{1}.\n"
                    "Мы успешно зарегистрировали этот факт: "
                    "https://vk.com/disa_count".format((disa_chromo - 46), chromo_end))
    action_log("Disa summary printed")
    disa_chromo = 46
    global_lock.acquire()
    with open(config.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))
    global_lock.release()
    disa.disa_first = True


def disa(message):
    if not hasattr(disa, "disa_first"):
        disa.disa_first = True
    if not hasattr(disa, "disa_bang"):
        disa.disa_bang = time.time()
    if not hasattr(disa, "disa_crunch"):
        disa.disa_crunch = disa.disa_bang + 60 * 60

    disa_init = False
    global_lock.acquire()
    # пытаемся открыть файл с количеством Дисиных хромосом
    try:
        with open(config.file_location_disa, 'r', encoding='utf-8') as file_disa_read:
            disa_chromo = int(file_disa_read.read())
    except (IOError, OSError, ValueError):
        disa_chromo = 46
        pass
    disa_chromo += 1
    with open(config.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))
    global_lock.release()

    user_action_log(message, "added chromosome to Disa")
    if message.chat.type == "supergroup":
        if disa.disa_first:
            disa.disa_bang = time.time()
            disa.disa_crunch = disa.disa_bang + 60 * 60
            disa.disa_first = False
        elif (not disa.disa_first) and (time.time() >= disa.disa_crunch):
            disa_init = True

    # запись счетчика в вк
    if disa_init:
        disa_vk_report(disa_chromo, message)


def anti_disa(message):
    global_lock.acquire()
    try:
        with open(config.file_location_disa, 'r', encoding='utf-8') as file_disa_read:
            disa_chromo = int(file_disa_read.read())
    except (IOError, OSError, ValueError):
        disa_chromo = 46
        pass
    disa_chromo -= 1

    with open(config.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))
    global_lock.release()
    user_action_log(message, "removed chromosome to Disa")


def check_disa(message):
    # добавления счетчика в функцию
    if not hasattr(check_disa, "disa_counter"):
        check_disa.disa_counter = 0

    # проверяем Диса ли это
    if message.from_user.id != config.disa_id:
        return

    # проверяем что идет серия из коротких предложений
    if len(message.text) > config.length_of_stupid_message:
        check_disa.disa_counter = 0
        return

    check_disa.disa_counter += 1

    # проверяем, будем ли отвечать Дисе
    disa_trigger = random.randint(1, 6)
    if check_disa.disa_counter >= config.too_many_messages and disa_trigger == 2:
        my_bot.reply_to(message, random.choice(config.stop_disa))
        check_disa.disa_counter = 0

    # записываем в файл увеличенный счетчик хромосом
    try:
        with open(config.file_location_disa, 'r+', encoding='utf-8') as file:
            disa_chromo = str(int(file.read()) + 1)
            file.seek(0)
            file.write(disa_chromo)
            file.truncate()
    except Exception as ex:
        logging.error(ex)
        pass

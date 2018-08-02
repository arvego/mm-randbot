#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import random
import time

import vk_api

import config
import tokens
from utils import my_bot, user_action_log, action_log, value_from_file, value_to_file, compress_msgs


# TODO: починить авторизацию. Нас там заблокировали
def disa_vk_report(disa_chromo, message):
    login, password = tokens.vk_disa_login, tokens.vk_disa_password
    vk_session = vk_api.VkApi(login, password, config_filename=config.file_location['vk_config'])
    vk_session.auth()
    vk = vk_session.get_api()
    wall = vk.wall.get(owner_id=config.disa_vk_group, count=1)
    if time.localtime(wall['items'][0]['date'])[2] == time.localtime()[2]:
        disa_chromo_post = disa_chromo - 46
        try:
            old_chromo = int(wall['items'][0]['text'])
            disa_chromo_post += old_chromo
        except Exception as ex:
            logging.error(ex)
            disa_chromo_post = disa_chromo
        vk.wall.edit(owner_id=config.disa_vk_group,
                     post_id=wall['items'][0]['id'],
                     message=str(disa_chromo_post))
    else:
        disa_chromo_post = 46 + disa_chromo
        vk.wall.post(owner_id=config.disa_vk_group,
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

    value_to_file(config.file_location['chromo'], 46)
    disa.disa_first = True


def disa(message):
    if not hasattr(disa, "disa_first"):
        disa.disa_first = True
    if not hasattr(disa, "disa_bang"):
        disa.disa_bang = time.time()
    if not hasattr(disa, "disa_crunch"):
        disa.disa_crunch = disa.disa_bang + 60 * 60

    disa_init = False

    # пытаемся открыть файл с количеством Дисиных хромосом
    disa_chromo = value_from_file(config.file_location['chromo'], 46)
    disa_chromo += 1
    value_to_file(config.file_location['chromo'], disa_chromo)

    user_action_log(message, "added chromosome to Disa")
    if message.chat.type == "supergroup":
        if disa.disa_first:
            disa.disa_bang = time.time()
            disa.disa_crunch = disa.disa_bang + 60 * 60
            disa.disa_first = False
        elif (not disa.disa_first) and (time.time() >= disa.disa_crunch):
            disa_init = True

    # запись счетчика в вк
    if disa_init and False:
        disa_vk_report(disa_chromo, message)


def anti_disa(message):
    disa_chromo = value_from_file(config.file_location['chromo'], 46)
    value_to_file(config.file_location['chromo'], disa_chromo - 1)
    user_action_log(message, "removed chromosome to Disa")


def ro_roll(text, chat_id=config.mm_chat, max_time=100):
    time.sleep(0.25)
    ro_roll_val = random.randint(1, max_time)
    release_time = time.time() + ro_roll_val * 60
    roll_bot_msg = my_bot.send_message(chat_id, "/ROll")
    my_bot.reply_to(roll_bot_msg, str(ro_roll_val).zfill(2))
    my_bot.send_message(chat_id, text.format(str(ro_roll_val).zfill(2)))
    return release_time

def flood_counter(message):
    # добавления счетчика в функцию
    if not hasattr(flood_counter, "disa_counter"):
        flood_counter.disa_counter = 0
    if not hasattr(flood_counter, "disa_id"):
        flood_counter.disa_id = 0


    if message.from_user.id != flood_counter.disa_id:
        flood_counter.disa_id = message.from_user.id
        flood_counter.disa_counter = 0
        return

    flood_counter.disa_counter += 1

def flood_kik(message):
    if int(message.from_user.id) in config.admin_ids:
        return
    empty_name = ''
    chat_id = message.chat.id
    compress_msgs(message, empty_name, message.from_user.first_name, message.from_user.last_name, message.from_user.id, config.too_many_messages)
    release_time = ro_roll(
            "Эй, {}.\n".format(message.from_user.first_name) + "Твой флуд обеспечил тебе {} мин. РО. Поздравляю!",
            chat_id=chat_id, max_time=100)
    my_bot.restrict_chat_member(chat_id=chat_id, user_id=flood_counter.disa_id, until_date=release_time,
                                    can_send_messages=False, can_send_media_messages=False,
                                    can_send_other_messages=False,
                                    can_add_web_page_previews=False)
    flood_counter.disa_counter = 0

def flood_count(message):
    flood_counter(message)
    if flood_counter.disa_counter >= config.too_many_messages:
        flood_kik(message)

def check_disa(message):
    # добавления счетчика в функцию
    if not hasattr(flood_counter, "disa_counter"):
        flood_counter.disa_counter = 0
    if not hasattr(flood_counter, "disa_id"):
        flood_counter.disa_id = 0

    # проверяем что идет серия из коротких предложений
    try:
        msg_len = len(message.text)
    except TypeError:
        msg_len = 0
    if msg_len <= config.length_of_stupid_message:
        flood_counter(message)

    # проверяем, будем ли отвечать Дисе
    disa_trigger = random.randint(1, 2)
    if flood_counter.disa_counter >= config.too_many_messages and disa_trigger == 2:
        # my_bot.reply_to(message, random.choice(config.stop_disa))
        flood_kik(message)


    # записываем в файл увеличенный счетчик хромосом
    disa_chromo = value_from_file(config.file_location['chromo'], 46)
    value_to_file(config.file_location['chromo'], disa_chromo + 1)

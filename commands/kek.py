#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import os
import random
import time

import config
from commands import weather
from commands.disa_commands import ro_roll
from utils import my_bot, user_action_log


def my_kek(message):
    """
    открывает соответствующие файл и папку, кидает рандомную строчку из файла, или рандомную картинку или гифку из папки
    :param message:
    :return:
    """
    if not hasattr(my_kek, "kek_bang"):
        my_kek.kek_bang = time.time()
    if not hasattr(my_kek, "kek_crunch"):
        my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
    if not hasattr(my_kek, "kek_enable"):
        my_kek.kek_enable = True
    if not hasattr(my_kek, "kek_counter"):
        my_kek.kek_counter = 0
    if not hasattr(weather.my_weather, "weather_bold"):
        weather.my_weather.weather_bold = False

    kek_init = True

    if message.chat.id == int(config.mm_chat):
        if my_kek.kek_counter == 0:
            my_kek.kek_bang = time.time()
            my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
            my_kek.kek_counter += 1
            kek_init = True
        elif (my_kek.kek_counter >= config.limit_kek
              and time.time() <= my_kek.kek_crunch):
            kek_init = False
        elif time.time() > my_kek.kek_crunch:
            my_kek.kek_counter = -1
            kek_init = True

    if not (kek_init and my_kek.kek_enable):
        return
    if message.chat.id == config.mm_chat:
        my_kek.kek_counter += 1
    your_destiny = random.randint(1, 30)  # если при вызове не повезло, то кикаем из чата
    if your_destiny == 13 and str(message.chat.id) == config.mm_chat:
        my_bot.reply_to(message,
                        "Предупреждал же, что кикну. "
                        "Если не предупреждал, то ")
        my_bot.send_document(message.chat.id, config.gif_links[0],
                             reply_to_message_id=message.message_id)
        try:
            if int(message.from_user.id) in config.admin_ids:
                my_bot.reply_to(message, "... Но против хозяев не восстану.")
                user_action_log(message, "can't be kicked out")
            else:
                # кикаем кекуна из чата (можно ещё добавить условие,
                # что если один юзер прокекал больше числа n за время t,
                # то тоже в бан)
                release_time = ro_roll(
                    "Эй, {}.\n".format(
                        message.from_user.first_name) + "Твой /kek обеспечил тебе {} мин. бана. Поздравляю!",
                    chat_id=message.chat.id, max_time=15)

                time.sleep(5)
                my_bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=release_time)
                user_action_log(message, "has been kicked out until {}".format(release_time))
        except Exception as ex:
            logging.exception(ex)
            pass
    else:
        type_of_kek = random.randint(1, 33)
        # 1/33 шанс на картинку или гифку
        if type_of_kek == 9:
            all_imgs = os.listdir(config.kek_dir)
            rand_file = random.choice(all_imgs)
            your_file = open(config.kek_dir + rand_file, "rb")
            if rand_file.endswith(".gif"):
                my_bot.send_document(message.chat.id, your_file,
                                     reply_to_message_id=message.message_id)
            else:
                my_bot.send_photo(message.chat.id, your_file,
                                  reply_to_message_id=message.message_id)
            your_file.close()
            user_action_log(message,
                            "got that kek:\n{0}".format(your_file.name))
        elif type_of_kek == 10:
            my_bot.send_document(message.chat.id, random.choice(config.gif_links),
                                 reply_to_message_id=message.message_id)
        elif type_of_kek < 10:
            your_kek = ''
            file_kek = open(config.file_location['kek_file_ids'], 'r', encoding='utf-8')
            # while your_kek == '\n':
            your_kek = random.choice(file_kek.readlines())
            # если попалась строчка вида '<sticker>ID', то шлём стикер по ID
            if str(your_kek).startswith("<sticker>"):
                sticker_id = str(your_kek[9:]).strip()
                my_bot.send_sticker(message.chat.id, sticker_id, reply_to_message_id=message.message_id)
            # если попалась строчка вида '<audio>ID', то шлём аудио по ID
            elif str(your_kek).startswith("<audio>"):
                audio_id = str(your_kek[7:]).strip()
                my_bot.send_audio(message.chat.id, audio_id, reply_to_message_id=message.message_id)
            # если попалась строчка вида '<voice>ID', то шлём голосовое сообщение по ID
            elif str(your_kek).startswith("<voice>"):
                voice_id = str(your_kek[7:]).strip()
                my_bot.send_voice(message.chat.id, voice_id, reply_to_message_id=message.message_id)
            user_action_log(message,
                            "got that kek:\n{0}".format(str(your_kek).replace("<br>", "\n")[:35]))
        # иначе смотрим файл
        else:
            your_kek = ''
            file_kek = open(config.file_location['/kek'], 'r', encoding='utf-8')
            while your_kek == '':
                your_kek = random.choice(file_kek.readlines())
            my_bot.reply_to(message,
                            str(your_kek).replace("<br>", "\n"))
            file_kek.close()
            user_action_log(message,
                            "got that kek:\n{0}".format(str(your_kek).replace("<br>", "\n")[:35]))

    if my_kek.kek_counter == config.limit_kek - 10:
        time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()),
                                60)
        my_bot.reply_to(message,
                        "<b>Внимание!</b>\nЭтот чат может покекать "
                        "ещё не более {0} раз до истечения кекочаса "
                        "(через {1} мин. {2} сек.).\n"
                        "По истечению кекочаса "
                        "счётчик благополучно сбросится.".format(config.limit_kek - my_kek.kek_counter,
                                                                 time_remaining[0], time_remaining[1]),
                        parse_mode="HTML")
    if my_kek.kek_counter == config.limit_kek - 1:
        time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()), 60)
        my_bot.reply_to(message,
                        "<b>EL-FIN!</b>\n"
                        "Теперь вы сможете кекать "
                        "только через {0} мин. {1} сек.".format(time_remaining[0], time_remaining[1]),
                        parse_mode="HTML")
    my_kek.kek_counter += 1


def add_kek(message):
    add_id = ''
    your_new_kek = ''
    if getattr(message, 'reply_to_message') is not None:
        # msg_media = first((getattr(message.reply_to_message, 'sticker'),
        #                    getattr(message.reply_to_message, 'audio'),
        #                    getattr(message.reply_to_message, 'voice')), key=lambda x: x is not None)
        if getattr(message.reply_to_message, 'sticker') is not None:
            add_id = '<sticker>{}'.format(message.reply_to_message.sticker.file_id)
        elif getattr(message.reply_to_message, 'audio') is not None:
            add_id = '<audio>{}'.format(message.reply_to_message.audio.file_id)
        elif getattr(message.reply_to_message, 'voice') is not None:
            add_id = '<voice>{}'.format(message.reply_to_message.voice.file_id)
        elif getattr(message.reply_to_message, 'text') is not None:
            add_id = message.reply_to_message.text
        else:
            return
        with open(config.file_location['kek_requests'], 'a') as add_ids:
            add_ids.write('\n{}'.format(add_id))
    elif len(message.text.split()) > 1:
        your_new_kek = ' '.join(message.text.split()[1:])
        with open(config.file_location['kek_requests'], 'a') as add_keks:
            add_keks.write('\n{}'.format(your_new_kek))
    user_action_log(message, "requested a kek:\n{0}{1}".format(add_id, your_new_kek))

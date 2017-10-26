#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import os
import random
import sys
import time

import config
from commands import weather
from utils import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


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

    if message.chat.id == int(config.my_chatID):
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

    if kek_init and my_kek.kek_enable:
        if message.chat.id == config.my_chatID:
            my_kek.kek_counter += 1
        your_destiny = random.randint(1, 30)
        # если при вызове не повезло, то кикаем из чата
        if your_destiny == 13: # and message.chat.id == config.my_chatID: # FIXME: always false
            my_bot.reply_to(message,
                            "Предупреждал же, что кикну. "
                            "Если не предупреждал, то ")
            my_bot.send_document(message.chat.id, 'https://t.me/mechmath/127603',
                                 reply_to_message_id=message.message_id)
            try:
                if int(message.from_user.id) in config.admin_ids:
                    my_bot.reply_to(message, "... Но против хозяев не восстану.")
                    user_action_log(message, "can't be kicked out")
                else:
                    # кикаем кекуна из чата (можно ещё добавить условие,
                    # что если один юзер прокекал больше числа n за время t,
                    # то тоже в бан)
                    my_bot.kick_chat_member(message.chat.id,
                                            message.from_user.id)
                    user_action_log(message, "has been kicked out")
                    my_bot.unban_chat_member(message.chat.id,
                                             message.from_user.id)
                    # тут же снимаем бан, чтобы смог по ссылке к нам вернуться
                    user_action_log(message, "has been unbanned")
            except Exception as ex:
                logging.exception(ex)
                pass
        else:
            type_of_kek = random.randint(1, 33)
            # 1/33 шанс на картинку или гифку
            if type_of_kek == 9:
                all_imgs = os.listdir(config.dir_location_kek)
                rand_file = random.choice(all_imgs)
                your_file = open(config.dir_location_kek + rand_file, "rb")
                if rand_file.endswith(".gif"):
                    my_bot.send_document(message.chat.id, your_file,
                                         reply_to_message_id=message.message_id)
                else:
                    my_bot.send_photo(message.chat.id, your_file,
                                      reply_to_message_id=message.message_id)
                your_file.close()
                user_action_log(message,
                                "got that kek:\n{0}".format(your_file.name))
            # иначе смотрим файл
            else:
                file_kek = open(config.file_location['/kek'], 'r', encoding='utf-8')
                your_kek = random.choice(file_kek.readlines())
                # если попалась строчка вида '<sticker>ID', то шлём стикер по ID
                if str(your_kek).startswith("<sticker>"):
                    sticker_id = str(your_kek[9:]).strip()
                    my_bot.send_sticker(message.chat.id, sticker_id, reply_to_message_id=message.message_id)
                # если попалась строчка вида '<audio>ID', то шлём аудио по ID
                elif str(your_kek).startswith("<audio>"):
                    audio_id = str(your_kek[7:-1]).strip()
                    my_bot.send_audio(message.chat.id, audio_id, reply_to_message_id=message.message_id)
                # если попалась строчка вида '<voice>ID', то шлём голосовое сообщение по ID
                elif str(your_kek).startswith("<voice>"):
                    voice_id = str(your_kek[7:-1]).strip()
                    my_bot.send_voice(message.chat.id, voice_id, reply_to_message_id=message.message_id)
                # иначе просто шлём обычный текст
                else:
                    my_bot.reply_to(message,
                                    str(your_kek).replace("<br>", "\n"))
                file_kek.close()
                user_action_log(message,
                                "got that kek:\n{0}".format(str(your_kek).replace("<br>", "\n")))

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
        if my_kek.kek_counter == config.limit_kek:
            time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()), 60)
            my_bot.reply_to(message,
                            "<b>EL-FIN!</b>\n"
                            "Теперь вы сможете кекать "
                            "только через {0} мин. {1} сек.".format(time_remaining[0], time_remaining[1]),
                            parse_mode="HTML")
        my_kek.kek_counter += 1

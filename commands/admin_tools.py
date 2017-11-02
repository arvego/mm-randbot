# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import subprocess
import sys

import config
import tokens
from utils import my_bot, user_action_log, global_lock

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def admin_post(message):
    if len(message.text.split()) > 1:

        global_lock.acquire()
        if message.text.split()[1] == "edit":
            try:
                with open(config.file_location_lastbotpost, 'r', encoding='utf-8') as file:
                    last_msg_id = int(file.read())
                my_edited_message = ' '.join(message.text.split()[2:])
                my_bot.edit_message_text(my_edited_message, config.my_chatID, last_msg_id, parse_mode="Markdown")
                user_action_log(message, "has edited message {}:\n{}".format(last_msg_id, my_edited_message))
            except (IOError, OSError):
                my_bot.reply_to(message, "Мне нечего редактировать.")
        else:
            my_message = ' '.join(message.text.split()[1:])
            sent_message = my_bot.send_message(config.my_chatID, my_message, parse_mode="Markdown")
            with open(config.file_location_lastbotpost, 'w', encoding='utf-8') as file_lastmsgID_write:
                file_lastmsgID_write.write(str(sent_message.message_id))
            user_action_log(message, "has posted this message:\n{}".format(my_message))
        global_lock.release()
    else:
        my_bot.reply_to(message, "Мне нечего постить.")


def admin_clean(message):
    if not hasattr(admin_clean, "allow_long"):
        admin_clean.allow_long = False
    if not hasattr(admin_clean, "allow_long_id"):
        admin_clean.allow_long_id = -1

    if len(message.text.split()) == 1:
        if admin_clean.allow_long:
            user_action_log(message, "cancelled big cleanup")
            admin_clean.allow_long = False
        return
    else:
        num_str = message.text.split()[1]

    if not num_str.isdigit():
        if admin_clean.allow_long:
            user_action_log(message, "cancelled big cleanup")
            admin_clean.allow_long = False
        return

    num = int(num_str)
    allow_long_str = 'Long cleanup is allowed' if admin_clean.allow_long else 'Long cleanup is not allowed'
    user_action_log(message, "has launched cleanup of {} messages. {}".format(num, allow_long_str))

    if num > 500:
        my_bot.reply_to(message, "Тааак, падажжи, слишком большое число указал, больше 500 не принимаю")
        return

    if num > 128 and (not admin_clean.allow_long or admin_clean.allow_long_id != message.from_user.id):
        my_bot.reply_to(message, "Вы запросили очистку более 128 сообщений. Для подтверждения отправьте "
                                 "команду еще раз. Для отмены отправльте команду с текстовым параметром. "
                                 "С уважением, ваш раб")
        admin_clean.allow_long = True
        admin_clean.allow_long_id = message.from_user.id
        return

    count = 0
    msg_id = message.message_id
    while count < num:
        try:
            my_bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            count += 1
        except:
            pass
        msg_id -= 1

    user_action_log(message, "cleaned up {} messages".format(count))


def admin_prize(message):
    if len(message.text.split()) > 1 and message.text.split()[1] == tokens.my_prize:
        all_imgs = os.listdir(config.dir_location_prize)
        rand_file = random.choice(all_imgs)
        your_file = open(config.dir_location_prize + rand_file, "rb")
        if rand_file.endswith(".gif"):
            my_bot.send_document(message.chat.id, your_file, reply_to_message_id=message.message_id)
        else:
            my_bot.send_photo(message.chat.id, your_file, reply_to_message_id=message.message_id)
        your_file.close()
        user_action_log(message, "got that prize:\n{0}".format(your_file.name))


def kill_bot(message):
    if not hasattr(kill_bot, "check_sure"):
        kill_bot.check_sure = True
        return
    global_lock.acquire()
    try:
        file_killed_write = open(config.bot_killed_filename, 'w', encoding='utf-8')
        file_killed_write.close()
    except RuntimeError:
        pass
    global_lock.release()

    my_bot.send_document(message.chat.id, "https://t.me/mechmath/169445",
                         caption="Ухожу на отдых!", reply_to_message_id=message.message_id)
    user_action_log(message, "remotely killed bot.")
    os._exit(0)


def update_bot(message):
    if not hasattr(update_bot, "check_sure"):
        update_bot.check_sure = True
        return

    global_lock.acquire()
    try:
        file_update_write = open(config.bot_update_filename, 'w', encoding='utf-8')
        file_update_write.close()
    except RuntimeError:
        pass
    global_lock.release()

    my_bot.reply_to(message, "Ух, ухожу на обновление...")
    user_action_log(message, "remotely ran update script.")
    os.execl('/bin/bash', 'bash', 'bot_update.sh')

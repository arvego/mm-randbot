# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import sys

# модуль с настройками
import data
# command modules
import kek
# shared bot parts
from bot_shared import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def admin_post(message):
    user_action_log(message, "has launched post tool")
    if message.text.split()[1] == "edit":
        try:
            with open(data.file_location_lastbotpost, 'r', encoding='utf-8') as file:
                last_msg_id = int(file.read())
            my_edited_message = ' '.join(message.text.split()[2:])
            my_bot.edit_message_text(my_edited_message, data.my_chatID, last_msg_id, parse_mode="Markdown")
            user_action_log(message, "has edited message {}:\n{}\n".format(last_msg_id, my_edited_message))
        except (IOError, OSError):
            my_bot.reply_to(message, "Мне нечего редактировать.")
    else:
        my_message = ' '.join(message.text.split()[1:])
        sent_message = my_bot.send_message(data.my_chatID, my_message, parse_mode="Markdown")
        with open(data.file_location_lastbotpost, 'w', encoding='utf-8') as file_lastmsgID_write:
            file_lastmsgID_write.write(str(sent_message.message_id))
        user_action_log(message, "has posted this message:\n{}\n".format(my_message))


def admin_prize(message):
    if len(message.text.split()) > 1 and message.text.split()[1] == data.my_prize:
        all_imgs = os.listdir(data.dir_location_prize)
        rand_file = random.choice(all_imgs)
        your_file = open(data.dir_location_prize + rand_file, "rb")
        if rand_file.endswith(".gif"):
            my_bot.send_document(message.chat.id, your_file, reply_to_message_id=message.message_id)
        else:
            my_bot.send_photo(message.chat.id, your_file, reply_to_message_id=message.message_id)
        your_file.close()
        user_action_log(message, "got that prize:\n{0}\n".format(your_file.name))


# для админов
def admin_toys(message):
    if not hasattr(kek.my_kek, "kek_enable"):
        kek.my_kek.kek_enable = True

    command = message.text.split()[0].lower()
    if command in ["/post", "/prize", "/kek_enable", "/kek_disable", "/update_bot", "/kill"]:
        user_action_log(message, "has launched admin tools")

    if command == "/post":
        admin_post(message)
    elif command == "/prize":
        admin_prize(message)
    elif command == "/kek_enable":
        kek.my_kek.kek_enable = True
        user_action_log(message, "enabled kek")
    elif command == "/kek_disable":
        kek.my_kek.kek_enable = False
        user_action_log(message, "disabled kek")
    elif command == "/update_bot":
        file_update_write = open(data.bot_update_filename, 'w', encoding='utf-8')
        file_update_write.close()
    elif command.startswith("/kill"):
        if not len(message.text.split()) == 1:
            my_bot.reply_to(message, "Прощай, жестокий чат. ;~;")

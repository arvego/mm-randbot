# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import sys

# модуль с настройками
import data.constants
# shared bot parts
from bot_shared import my_bot, my_bot_name, user_action_log
# command modules
from commands import kek

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def admin_post(message):
    user_action_log(message, "has launched post tool")
    if len(message.text.split()) > 1:
        if message.text.split()[1] == "edit":
            try:
                with open(data.constants.file_location_lastbotpost, 'r', encoding='utf-8') as file:
                    last_msg_id = int(file.read())
                my_edited_message = ' '.join(message.text.split()[2:])
                my_bot.edit_message_text(my_edited_message, data.constants.my_chatID, last_msg_id, parse_mode="Markdown")
                user_action_log(message, "has edited message {}:\n{}\n".format(last_msg_id, my_edited_message))
            except (IOError, OSError):
                my_bot.reply_to(message, "Мне нечего редактировать.")
        else:
            my_message = ' '.join(message.text.split()[1:])
            sent_message = my_bot.send_message(data.constants.my_chatID, my_message, parse_mode="Markdown")
            with open(data.constants.file_location_lastbotpost, 'w', encoding='utf-8') as file_lastmsgID_write:
                file_lastmsgID_write.write(str(sent_message.message_id))
            user_action_log(message, "has posted this message:\n{}\n".format(my_message))
    else:
        my_bot.reply_to(message, "Мне нечего постить.")


def admin_clean(message):
    if len(message.text.split()) == 1:
        return
    num_str = message.text.split()[1]
    if num_str.isdigit():
        num = int(num_str)
        user_action_log(message, "has launched cleanup {} messages".format(num))
        count = 0
        for id in range(message.message_id - 1, message.message_id - num, -1):
            try:
                my_bot.delete_message(chat_id=message.chat.id, message_id=id)
                count = count + 1
            except:
                pass

        user_action_log(message, "cleaned up {} messages".format(count))


def admin_prize(message):
    if len(message.text.split()) > 1 and message.text.split()[1] == data.constants.my_prize:
        all_imgs = os.listdir(data.constants.dir_location_prize)
        rand_file = random.choice(all_imgs)
        your_file = open(data.constants.dir_location_prize + rand_file, "rb")
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
    if command in ["/post", "/prize", "/kek_enable", "/kek_disable", "/update_bot", "/kill", "/clean"]:
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
        file_update_write = open(data.constants.bot_update_filename, 'w', encoding='utf-8')
        file_update_write.close()
    elif command == "/clean":
        admin_clean(message)
    elif command.startswith("/kill"):
        if not len(message.text.split()) == 1:
            if message.text.split()[1] == my_bot_name:
                my_bot.reply_to(message, "Прощай, жестокий чат. ;~;")
                my_bot.send_document(message.chat.id, "https://t.me/mechmath/169445",
                                                reply_to_message_id=message.message_id)
        else:
            return

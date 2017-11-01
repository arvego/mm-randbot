#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import re
import sys
import time

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

import config
import vk_listener
from commands import admin_tools, arxiv_queries, dice, disa_commands, kek, morning_message, random_images, weather, \
    vk_commands, wiki, wolfram
from utils import my_bot, my_bot_name, commands_handler, is_command, command_with_delay, bot_admin_command, \
    chat_admin_command, action_log, user_action_log, user_info, dump_message

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


@my_bot.message_handler(func=commands_handler(['/start', '/help', '/links', '/wifi', '/chats', '/rules']))
@command_with_delay(delay=3)
def my_new_data(message):
    command = message.text.lower().split()[0]
    command_raw = re.split("@+", command)[0]
    with open(config.file_location[command_raw], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {}".format(command))


# Приветствуем нового юзера
@my_bot.message_handler(content_types=['new_chat_members'])
def welcoming_task(message):
    new_members_names = []
    new_members_info = []
    for member in message.new_chat_members:
        new_members_names.append(member.first_name)
        new_members_info.append(user_info(member))
    welcoming_msg = "{}, {}!\nЕсли здесь впервые, то ознакомься с правилами — /rules, " \
                    "и представься, если несложно.".format(random.choice(config.welcome_list),
                                                           ', '.join(new_members_names))
    my_bot.reply_to(message, welcoming_msg)
    action_log("User(s) {} joined the chat.".format(', '.join(new_members_info)))


@my_bot.message_handler(func=commands_handler(['/wolfram', '/wf']))
def wolfram_solver(message):
    wolfram.wolfram_solver(message)


@my_bot.message_handler(func=commands_handler(['/weather']))
@command_with_delay(delay=5 * 60)
def my_weather(message):
    weather.my_weather(message)


@my_bot.message_handler(func=commands_handler(['/wiki']))
@command_with_delay(delay=10)
def my_wiki(message):
    wiki.my_wiki(message)


@my_bot.message_handler(func=commands_handler(['/arxiv']))
@command_with_delay(delay=10)
def arxiv_checker(message):
    arxiv_queries.arxiv_checker(message)


@my_bot.message_handler(func=commands_handler(['/vk_post']))
@command_with_delay(delay=10)
def vk_post(message):
    vk_commands.vk_post(message)


@my_bot.message_handler(func=commands_handler(['/task', '/maths']))
@command_with_delay(delay=5 * 60)
def my_rand_img(message):
    random_images.my_rand_img(message)


@my_bot.message_handler(func=commands_handler(['/kek']))
@command_with_delay(delay=1)
def my_kek(message):
    kek.my_kek(message)


@my_bot.message_handler(func=commands_handler(['/truth']))
def my_truth(message):
    answers = ["да", "нет", "это не важно", "да, хотя зря", "никогда", "100%", "1 из 100"]
    truth = random.choice(answers)
    my_bot.reply_to(message, truth)
    user_action_log(message, "has discovered the Truth:\n{0}".format(truth))


@my_bot.message_handler(func=commands_handler(['/roll']))
def my_roll(message):
    rolled_number = random.randint(0, 100)
    my_bot.reply_to(message, str(rolled_number).zfill(2))
    user_action_log(message, "recieved {0}".format(rolled_number))


@my_bot.message_handler(func=commands_handler(['/d6']))
def my_d6(message):
    dice.my_d6(message)


@my_bot.message_handler(func=commands_handler(['/dn']))
def my_dn(message):
    dice.my_dn(message)


@my_bot.message_handler(func=commands_handler(['/gender']))
def your_gender(message):
    with open(config.file_location['/gender'], 'r', encoding='utf-8') as file_gender:
        gender = random.choice(file_gender.readlines())
        my_bot.reply_to(message, gender)
    user_action_log(message, "has discovered his gender:\n{0}".format(str(gender).replace("<br>", "\n")))


@my_bot.message_handler(func=commands_handler(['/_']))
def underscope_reply(message):
    my_bot.reply_to(message, "_\\")
    user_action_log(message, "called the _\\")


@my_bot.message_handler(func=commands_handler(['/id']))
def id_reply(message):
    my_bot.reply_to(message, "/id")
    user_action_log(message, "called the id")


@my_bot.message_handler(func=commands_handler(['/echo']))
def id_reply(message):
    my_bot.reply_to(message, message.text)
    user_action_log(message, "called echo:\n{}".format(message.text))


@my_bot.message_handler(func=commands_handler(['/disa'], inline=True))
def disa(message):
    disa_commands.disa(message)


@my_bot.message_handler(func=commands_handler(['/antidisa']))
def anti_disa(message):
    disa_commands.anti_disa(message)


@my_bot.message_handler(func=commands_handler(['/kek_enable']))
@chat_admin_command
def kek_enable(message):
    kek.my_kek.kek_enable = True
    user_action_log(message, "enabled kek")


@my_bot.message_handler(func=commands_handler(['/kek_disable']))
@chat_admin_command
def kek_enable(message):
    kek.my_kek.kek_enable = False
    user_action_log(message, "disabled kek")


@my_bot.message_handler(func=commands_handler(['/post']))
@chat_admin_command
def kek_enable(message):
    admin_tools.admin_post(message)


@my_bot.message_handler(func=commands_handler(['/clean']))
@chat_admin_command
def kek_enable(message):
    admin_tools.admin_clean(message)


@my_bot.message_handler(func=is_command())
@bot_admin_command
def admin_toys(message):
    command = message.text.split()[0].lower()
    if command == "/prize":
        admin_tools.admin_prize(message)
    elif command == "/update":
        if message.text.split()[1] == my_bot_name:
            admin_tools.update_bot(message)
    elif command == "/kill":
        if message.text.split()[1] == my_bot_name:
            admin_tools.kill_bot(message)


@my_bot.message_handler(content_types=["text"])
def check_disa(message):
    disa_commands.check_disa(message)


# All messages handler
def handle_messages(messages):
    for message in messages:
        dump_message(message)


while __name__ == '__main__':
    try:
        # если бот запущен .sh скриптом после падения — удаляем алёрт-файл
        try:
            os.remove(config.bot_down_filename)
        except OSError:
            pass
        try:
            os.remove(config.bot_update_filename)
        except OSError:
            pass
        # если бот запущен после вырубания нами — удаляем алёрт-файл
        try:
            os.remove(config.bot_killed_filename)
        except OSError:
            pass

        if config.debug_mode:
            action_log("Running bot in Debug mode!")

        # Background-планировщик задач, чтобы бот продолжал принимать команды
        scheduler = BackgroundScheduler()

        scheduler.add_job(vk_listener.vk_listener, 'interval', id='vk_listener', replace_existing=True, seconds=30)

        scheduler.add_job(morning_message.morning_msg, 'cron', id='morning_msg', replace_existing=True, hour=7,
                          timezone=pytz.timezone('Europe/Moscow'))

        scheduler.add_job(morning_message.unpin_msg, 'cron', id='unpin_msg', replace_existing=True, hour=13,
                          timezone=pytz.timezone('Europe/Moscow'))

        scheduler.start()

        # Запуск Long Poll бота
        my_bot.set_update_listener(handle_messages)
        my_bot.polling(none_stop=True, interval=1, timeout=60)
        time.sleep(1)

    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        action_log("Read Timeout. Because of Telegram API. We are offline. Reconnecting in 5 seconds.")
        time.sleep(5)

    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
        action_log("Connection Error. We are offline. Reconnecting...")
        time.sleep(5)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        action_log("Runtime Error. Retrying in 3 seconds.")
        time.sleep(3)

    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        action_log("Unicode Encode Error. Someone typed in cyrillic. Retrying in 3 seconds.")
        time.sleep(3)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        action_log("Keyboard Interrupt. Good bye.")
        sys.exit()

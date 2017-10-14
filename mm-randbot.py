#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import re
import sys
import time

# Сторонние модули
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

import vk_listener
from bot_shared import my_bot, commands_handler, is_command, command_with_delay, bot_admin_command, user_action_log
from commands import admin_tools, arxiv_queries, dice, disa_commands, kek, morning_message, random_images, weather, \
    wiki, wolfram
from data import constants

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


@my_bot.message_handler(func=commands_handler(['/start', '/help', '/links', '/wifi', '/chats', '/rules']))
@command_with_delay(delay=10)
def my_new_data(message):
    command = message.text.lower().split()[0]
    file_name = re.split("@+", command)[0]
    with open(constants.dir_location[file_name], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {0}\n".format(command))


# Приветствуем нового юзера
@my_bot.message_handler(content_types=['new_chat_members'])
def welcomingTask(message):
    new_members_names = []
    new_members_ids = []
    for member in message.new_chat_members:
        new_members_names.append(member.first_name)
        new_members_ids.append(str(member.id))
    welcoming_msg = "{0}, {1}!\nЕсли здесь впервые, то ознакомься с правилами — /rules, " \
                    "и представься, если несложно.".format(random.choice(constants.welcome_list),
                                                           ', '.join(new_members_names))
    my_bot.send_message(message.chat.id, welcoming_msg, reply_to_message_id=message.message_id)
    print("{0}\nUser(s) {1} joined the chat.\n".format(time.strftime(constants.time, time.gmtime()),
                                                       ', '.join(new_members_ids)))


@my_bot.message_handler(func=commands_handler(['/wolfram', '/wf']))
def wolframSolver(message):
    wolfram.wolfram_solver(message)


@my_bot.message_handler(func=commands_handler(['/weather']))
def my_weather(message):
    weather.my_weather(message)


@my_bot.message_handler(func=commands_handler(['/wiki']))
def my_wiki(message):
    wiki.my_wiki(message)


@my_bot.message_handler(func=commands_handler(['/arxiv']))
@command_with_delay(delay=10)
def arxiv_checker(message):
    arxiv_queries.arxiv_checker(message)


@my_bot.message_handler(func=commands_handler(['/task', '/maths']))
def myRandImg(message):
    random_images.my_rand_img(message)


@my_bot.message_handler(func=commands_handler(['/kek']))
@command_with_delay(delay=1)
def my_kek(message):
    kek.my_kek(message)


@my_bot.message_handler(func=commands_handler(['/truth']))
def myTruth(message):
    if not random.randint(1, 1000) == 666:
        answers = ["да", "нет", "это не важно", "да, хотя зря", "никогда", "100%", "1 из 100"]
        truth = random.choice(answers)
        my_bot.reply_to(message, truth)
        user_action_log(message, "has discovered the Truth:\n{0}".format(truth))
    else:
        my_bot.reply_to(message, constants.the_truth, parse_mode="HTML")
        user_action_log(message, "has discovered the Ultimate Truth.")


@my_bot.message_handler(func=commands_handler(['/roll']))
def myRoll(message):
    rolled_number = random.randint(0, 100)
    my_bot.reply_to(message, str(rolled_number).zfill(2))
    user_action_log(message, "recieved {0}".format(rolled_number))


@my_bot.message_handler(func=commands_handler(['/d6']))
def myD6(message):
    dice.my_d6(message)


@my_bot.message_handler(func=commands_handler(['/dn']))
def myDN(message):
    dice.my_dn(message)


@my_bot.message_handler(func=commands_handler(['/gender']))
def yourGender(message):
    with open(constants.file_location_gender, 'r', encoding='utf-8') as file_gender:
        gender = random.choice(file_gender.readlines())
    my_bot.reply_to(message, gender.replace("<br>", "\n"))
    user_action_log(message, "has discovered his gender:\n{0}".format(str(gender).replace("<br>", "\n")))


@my_bot.message_handler(func=commands_handler(['/_']))
def underscope_reply(message):
    my_bot.reply_to(message, "_\\")
    user_action_log(message, "called the _\\")


@my_bot.message_handler(func=commands_handler(['/id']))
def id_reply(message):
    my_bot.reply_to(message, "/id")
    user_action_log(message, "called the id")


@my_bot.message_handler(func=commands_handler(['/disa'], inline=True))
def disa(message):
    disa_commands.disa(message)


@my_bot.message_handler(func=commands_handler(['/antidisa']))
def antiDisa(message):
    disa_commands.anti_disa(message)


@my_bot.message_handler(func=is_command())
@bot_admin_command
def admin_toys(message):
    admin_tools.admin_toys(message)


@my_bot.message_handler(content_types=["text"])
def check_disa(message):
    disa_commands.check_disa(message)


while __name__ == '__main__':
    try:
        # если бот запущен .sh скриптом после падения — удаляем алёрт-файл
        try:
            os.remove(constants.bot_down_filename)
        except OSError:
            pass
        try:
            os.remove(constants.bot_update_filename)
        except OSError:
            pass
        # если бот запущен после вырубания нами — удаляем алёрт-файл
        try:
            os.remove(constants.bot_killed_filename)
        except OSError:
            pass

        # Background-планировщик задач, чтобы бот продолжал принимать команды
        scheduler = BackgroundScheduler()

        scheduler.add_job(vk_listener.vk_listener, 'interval', id='vkListener', replace_existing=True,
                          seconds=constants.vk_interval)

        scheduler.add_job(morning_message.morning_msg, 'cron', id='morning_msg', replace_existing=True, hour=7,
                          timezone=pytz.timezone('Europe/Moscow'))
        # scheduler.add_job(morning_message.morning_msg, 'interval', id='morning_msg', replace_existing=True, seconds=3)

        scheduler.start()

        # Запуск Long Poll бота
        my_bot.polling(none_stop=True, interval=1, timeout=60)
        time.sleep(1)
    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        #        logging.exception(e)
        print("{0}\nRead Timeout. Because of Telegram API.\nWe are offline. Reconnecting in 5 seconds.\n".format(
            time.strftime(constants.time, time.gmtime())))
        time.sleep(5)
    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
        #        logging.exception(e)
        print(
            "{0}\nConnection Error.\nWe are offline. Reconnecting...\n".format(
                time.strftime(constants.time, time.gmtime())))
        time.sleep(5)
    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        #        logging.exception(e)
        print("{0}\nRuntime Error.\nRetrying in 3 seconds.\n".format(time.strftime(constants.time, time.gmtime())))
        time.sleep(3)
    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        #        logging.exception(e)
        print("{0}\nUnicode Encode Error. Someone typed in cyrillic.\nRetrying in 3 seconds.\n".format(
            time.strftime(constants.time, time.gmtime())))
        time.sleep(3)
    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        #        logging.exception(e)
        print("\n{0}\nKeyboard Interrupt. Good bye.\n".format(time.strftime(constants.time, time.gmtime())))
        sys.exit()

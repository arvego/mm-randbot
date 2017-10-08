#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import re
import subprocess
import sys
import time

# сторонние модули
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

# модуль с настройками
import data.constants
import vk_listener
# shared bot parts
from bot_shared import my_bot, commands_handler, user_action_log
# command modules
from commands import admin_tools, arxiv_queries, dice, disa_commands, kek, morning_message, random_images, weather, \
    wiki, wolfram

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


# приветствуем нового юзера
@my_bot.message_handler(content_types=['new_chat_members'])
def welcomingTask(message):
    new_members_names = []
    new_members_ids = []
    for i in range(0, len(message.new_chat_members)):
        new_members_names.append(message.new_chat_members[i].first_name)
        new_members_ids.append(str(message.new_chat_members[i].id))
    welcoming_msg = \
        "{0}, {1}!\nЕсли здесь впервые, то ознакомься с правилами " \
        "— /rules, и представься, если несложно.".format(random.choice(data.constants.welcome_list),
                                                         ', '.join(new_members_names))
    my_bot.send_message(message.chat.id,
                        welcoming_msg,
                        reply_to_message_id=message.message_id)
    print("{0}\nUser(s) {1} joined the chat.\n".format(time.strftime(data.constants.time, time.gmtime()),
                                                       ', '.join(new_members_ids)))


# команды /start, /help, /links, /wifi, /chats, /rules
@my_bot.message_handler(func=commands_handler(['/start', '/help', '/links',
                                               '/wifi', '/chats', '/rules']))
def my_new_data(message):
    command = message.text.lower().split()[0]
    file_name = re.split("@+", command)[0]
    with open(data.constants.dir_location[file_name], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {0}\n".format(command))


# команды /task и /maths
@my_bot.message_handler(func=commands_handler(['/task', '/maths']))
def myRandImg(message):
    random_images.myRandImg(message)


# команда /d6
@my_bot.message_handler(func=commands_handler(['/d6']))
def myD6(message):
    dice.myD6(message)


# команда /roll
@my_bot.message_handler(func=commands_handler(['/roll']))
# генерует случайное целое число, в зависимости от него может кинуть картинку
# или гифку
def myRoll(message):
    rolled_number = random.randint(0, 100)
    my_bot.reply_to(message, str(rolled_number).zfill(2))
    user_action_log(message, "recieved {0}".format(rolled_number))


# команда /truth
@my_bot.message_handler(func=commands_handler(['/truth']))
def myTruth(message):
    # открывает файл и отвечает пользователю рандомными строками из него
    the_TRUTH = random.randint(1, 1000)
    if not the_TRUTH == 666:
        file_TRUTH = open(data.constants.file_location_truth, 'r', encoding='utf-8')
        TRUTH = random.choice(file_TRUTH.readlines())
        my_bot.reply_to(message, str(TRUTH).replace("<br>", "\n"))
        file_TRUTH.close()
        user_action_log(message,
                        "has discovered the Truth:\n{0}".format(str(TRUTH).replace("<br>", "\n")))
    else:
        my_bot.reply_to(message, data.constants.the_TRUTH, parse_mode="HTML")
        user_action_log(message, "has discovered the Ultimate Truth.")


# команда /gender
@my_bot.message_handler(func=commands_handler(['/gender']))
def yourGender(message):
    # открывает файл и отвечает пользователю рандомными строками из него
    with open(data.constants.file_location_gender, 'r', encoding='utf-8') as file_gender:
        gender = random.choice(file_gender.readlines())
    my_bot.reply_to(message, gender.replace("<br>", "\n"))
    user_action_log(message,
                    "has discovered his gender:\n{0}".format(str(gender).replace("<br>", "\n")))


# команда /wolfram (/wf)
@my_bot.message_handler(func=commands_handler(['/wolfram', '/wf']))
def wolframSolver(message):
    wolfram.wolframSolver(message)


# команда /weather
@my_bot.message_handler(func=commands_handler(['/weather']))
# Получает погоду в Москве на сегодня и на три ближайших дня,
# пересылает пользователю
def my_weather(message):
    weather.my_weather(message)


# команда /wiki
@my_bot.message_handler(func=commands_handler(['/wiki']))
# Обрабатывает запрос и пересылает результат.
# Если запроса нет, выдаёт рандомный факт.
def my_wiki(message):
    wiki.my_wiki(message)


# команда /kek
@my_bot.message_handler(func=commands_handler(['/kek']))
def my_kek(message):
    kek.my_kek(message)


# команда секретного кека
@my_bot.message_handler(func=commands_handler(['/_']))
def underscope_reply(message):
    my_bot.reply_to(message, "_\\")
    user_action_log(message, "called the _\\")


# команда сверхсекретного кека
@my_bot.message_handler(func=commands_handler(['/id']))
def id_reply(message):
    my_bot.reply_to(message, "/id")
    user_action_log(message, "called the id")


# для читерства
@my_bot.message_handler(commands=['dn'])
# рандомно выбирает элементы из списка значков
# TODO: желательно найти способ их увеличить или заменить на ASCII арт
def myDN(message):
    dice.myDN(message)


# команда /arxiv
@my_bot.message_handler(func=commands_handler(['/arxiv']))
def arxiv_checker(message):
    arxiv_queries.arxiv_checker(message)


# команда /disa [V2.069] (от EzAccount)
@my_bot.message_handler(func=commands_handler(['/disa'], inline=True))
def disa(message):
    disa_commands.disa(message)


@my_bot.message_handler(func=commands_handler(['/antidisa']))
def antiDisa(message):
    disa_commands.antiDisa(message)


# Диса тупит (от AChehonte)
@my_bot.message_handler(content_types=["text"])
def check_disa(message):
    disa_commands.check_disa(message)


# для админов
@my_bot.message_handler(func=lambda message: message.from_user.id in data.constants.admin_ids)
def admin_toys(message):
    admin_tools.admin_toys(message)


def update_bot():
    if os.path.isfile(data.constants.bot_update_filename):
        print("{}\nRunning bot update script. Shutting down.".format(time.strftime(data.constants.time, time.gmtime())))
        subprocess.call('bash bot_update.sh', shell=True)


def kill_bot():
    if os.path.isfile(data.constants.bot_killed_filename):
        time.sleep(3)
        # создаём отдельный алёрт для .sh скрипта — перезапустим бот сами
        try:
            file_killed_write = open(data.constants.bot_killed_filename, 'w', encoding='utf-8')
            file_killed_write.close()
            print("{0}\nBot has been killed off remotely by admin.\n".format(
                time.strftime(data.constants.time, time.gmtime())))
            os._exit(-1)
        except RuntimeError:
            os._exit(-1)


while __name__ == '__main__':
    try:
        # если бот запущен .sh скриптом после падения — удаляем алёрт-файл
        try:
            os.remove(data.constants.bot_down_filename)
        except OSError:
            pass
        try:
            os.remove(data.constants.bot_update_filename)
        except OSError:
            pass
        # если бот запущен после вырубания нами — удаляем алёрт-файл
        try:
            os.remove(data.constants.bot_killed_filename)
        except OSError:
            pass

        # Background-планировщик задач, чтобы бот продолжал принимать команды
        scheduler = BackgroundScheduler()

        scheduler.add_job(vk_listener.vkListener, 'interval', id='vkListener', replace_existing=True,
                          seconds=data.constants.vk_interval)
        scheduler.add_job(update_bot, 'interval', id='update_bot', replace_existing=True, seconds=3)
        scheduler.add_job(kill_bot, 'interval', id='kill_bot', replace_existing=True, seconds=3)

        scheduler.add_job(morning_message.morning_msg, 'cron', id='morning_msg', replace_existing=True, hour=7,
                          timezone=pytz.timezone('Europe/Moscow'))
        # scheduler.add_job(morning_msg, 'interval', id='morning_msg', replace_existing=True, seconds=3)

        scheduler.start()

        # Запуск Long Poll бота
        my_bot.polling(none_stop=True, interval=1, timeout=60)
        time.sleep(1)
    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        #        logging.exception(e)
        print("{0}\nRead Timeout. Because of Telegram API.\nWe are offline. Reconnecting in 5 seconds.\n".format(
            time.strftime(data.constants.time, time.gmtime())))
        time.sleep(5)
    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
        #        logging.exception(e)
        print(
            "{0}\nConnection Error.\nWe are offline. Reconnecting...\n".format(
                time.strftime(data.constants.time, time.gmtime())))
        time.sleep(5)
    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        #        logging.exception(e)
        print("{0}\nRuntime Error.\nRetrying in 3 seconds.\n".format(time.strftime(data.constants.time, time.gmtime())))
        time.sleep(3)
    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        #        logging.exception(e)
        print("{0}\nUnicode Encode Error. Someone typed in cyrillic.\nRetrying in 3 seconds.\n".format(
            time.strftime(data.constants.time, time.gmtime())))
        time.sleep(3)
    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        #        logging.exception(e)
        print("\n{0}\nKeyboard Interrupt. Good bye.\n".format(time.strftime(data.constants.time, time.gmtime())))
        sys.exit()

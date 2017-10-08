#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
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

# command modules
import admin_tools
import arxiv_queries
import disa_commands
import kek
import vk_listener
import weather
import wiki
import wolfram

# модуль с настройками
import data
# shared bot parts
from bot_shared import my_bot, commands_handler, user_action_log

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
        "— /rules, и представься, если несложно.".format(random.choice(data.welcome_list), ', '.join(new_members_names))
    my_bot.send_message(message.chat.id,
                        welcoming_msg,
                        reply_to_message_id=message.message_id)
    print("{0}\nUser(s) {1} joined the chat.\n".format(time.strftime(data.time, time.gmtime()),
                                                       ', '.join(new_members_ids)))


# команды /start, /help, /links, /wifi, /chats, /rules
@my_bot.message_handler(func=commands_handler(['/start', '/help', '/links',
                                               '/wifi', '/chats', '/rules']))
def my_new_data(message):
    command = message.text.lower().split()[0]
    file_name = re.split("@+", command)[0]
    with open(data.dir_location[file_name], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {0}\n".format(command))


# команды /task и /maths
@my_bot.message_handler(func=commands_handler(['/task', '/maths']))
# идёт в соответствующую папку и посылает рандомную картинку
def myRandImg(message):
    for command in str(message.text).lower().split():
        if command.startswith('/task'):
            path = data.dir_location_task
            user_action_log(message, "asked for a challenge")
            if not len(message.text.split()) == 1:
                your_difficulty = message.text.split()[1]
                if your_difficulty in data.difficulty:
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    while not rand_img.startswith(your_difficulty):
                        rand_img = random.choice(all_imgs)
                    your_img = open(path + rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img,
                                      reply_to_message_id=message.message_id)
                    user_action_log(message,
                                    "chose a difficulty level '{0}' "
                                    "and got that image:\n{1}".format(your_difficulty, your_img.name))
                    your_img.close()
                else:
                    my_bot.reply_to(message,
                                    "Доступно только три уровня сложности:\n"
                                    "{0}"
                                    "\nВыбираю рандомную задачу:".format(data.difficulty))
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    your_img = open(path + rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img,
                                      reply_to_message_id=message.message_id)
                    user_action_log(message,
                                    "chose a non-existent difficulty level '{0}' "
                                    "and got that image:\n{1}".format(your_difficulty, your_img.name))
                    your_img.close()
            else:
                all_imgs = os.listdir(path)
                rand_img = random.choice(all_imgs)
                your_img = open(path + rand_img, "rb")
                my_bot.send_photo(message.chat.id, your_img,
                                  reply_to_message_id=message.message_id)
                user_action_log(message,
                                "got that image:\n{0}".format(your_img.name))
                your_img.close()
        elif command.startswith('/maths'):
            path = data.dir_location_maths
            user_action_log(message, "asked for maths")
            if not len(message.text.split()) == 1:
                your_subject = message.text.split()[1].lower()
                if your_subject in data.subjects:
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    while not rand_img.startswith(your_subject):
                        rand_img = random.choice(all_imgs)
                    your_img = open(path + rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img,
                                      reply_to_message_id=message.message_id)
                    user_action_log(message,
                                    "chose subject '{0}' "
                                    "and got that image:\n"
                                    "{1}".format(your_subject, your_img.name))
                    your_img.close()
                else:
                    my_bot.reply_to(message,
                                    "На данный момент доступны факты"
                                    " только по следующим предметам:\n{0}\n"
                                    "Выбираю рандомный факт:".format(data.subjects)
                                    )
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    your_img = open(path + rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img,
                                      reply_to_message_id=message.message_id)
                    user_action_log(message,
                                    "chose a non-existent subject '{0}' "
                                    "and got that image:\n"
                                    "{1}".format(your_subject, your_img.name))
                    your_img.close()
            else:
                all_imgs = os.listdir(path)
                rand_img = random.choice(all_imgs)
                your_img = open(path + rand_img, "rb")
                my_bot.send_photo(message.chat.id, your_img,
                                  reply_to_message_id=message.message_id)
                user_action_log(message,
                                "got that image:\n{0}".format(your_img.name))
                your_img.close()


# команда /d6
@my_bot.message_handler(func=commands_handler(['/d6']))
# рандомно выбирает элементы из списка значков
# TODO: желательно найти способ их увеличить или заменить на ASCII арт
def myD6(message):
    d6 = data.d6_symbols
    dice = 2
    roll_sum = 0
    symbols = ''
    for _ in str(message.text).lower().split():
        if not len(message.text.split()) == 1:
            try:
                dice = int(message.text.split()[1])
            except ValueError:
                my_bot.reply_to(message,
                                "Не понял число костей. "
                                "Пожалуйста, введи команду "
                                "в виде \'/d6 <int>\', "
                                "где <int> — целое от 1 до 10.")
                return
    if 0 < dice <= 10:
        max_result = dice * 6
        for count in range(dice):
            roll_index = random.randint(0, len(d6) - 1)
            roll_sum += roll_index + 1
            if count < dice - 1:
                symbols += '{0} + '.format(d6[roll_index])
            elif count == dice - 1:
                symbols += '{0} = {1}  ({2})'.format(d6[roll_index], roll_sum,
                                                     max_result)
        my_bot.reply_to(message, symbols)
        user_action_log(message, "got that D6 output: {0}".format(symbols))


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
        file_TRUTH = open(data.file_location_truth, 'r', encoding='utf-8')
        TRUTH = random.choice(file_TRUTH.readlines())
        my_bot.reply_to(message, str(TRUTH).replace("<br>", "\n"))
        file_TRUTH.close()
        user_action_log(message,
                        "has discovered the Truth:\n{0}".format(str(TRUTH).replace("<br>", "\n")))
    else:
        my_bot.reply_to(message, data.the_TRUTH, parse_mode="HTML")
        user_action_log(message, "has discovered the Ultimate Truth.")


# команда /gender
@my_bot.message_handler(func=commands_handler(['/gender']))
def yourGender(message):
    # открывает файл и отвечает пользователю рандомными строками из него
    with open(data.file_location_gender, 'r', encoding='utf-8') as file_gender:
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
    roll_sum = 0
    symbols = ''
    if len(message.text.split()) == 3:
        try:
            dice_max = int(message.text.split()[1])
            dice_n = int(message.text.split()[2])
        except ValueError:
            return
        max_result = dice_n * dice_max
        for count in range(dice_n):
            try:
                roll = random.randint(0, dice_max)
                roll_sum += roll
                if count < dice_n - 1:
                    symbols += '{0} + '.format(roll)
                elif count == dice_n - 1:
                    symbols += '{0} = {1}  ({2})'.format(roll, roll_sum, max_result)
            except ValueError:
                pass
        if not len(symbols) > 4096:
            my_bot.reply_to(message, symbols)
            user_action_log(message,
                            "knew about /dn and got that output: {0}".format(symbols))
        else:
            my_bot.reply_to(message,
                            "Слишком большие числа. "
                            "Попробуй что-нибудь поменьше")
            user_action_log(message, "knew about /dn "
                                     "and the answer was too long "
                                     "to fit one message")


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
@my_bot.message_handler(func=lambda message: message.from_user.id in data.admin_ids)
def admin_toys(message):
    admin_tools.admin_toys(message)


def update_bot():
    if os.path.isfile(data.bot_update_filename):
        print("{}\nRunning bot update script. Shutting down.".format(time.strftime(data.time, time.gmtime())))
        subprocess.call('bash bot_update.sh', shell=True)


def kill_bot():
    if os.path.isfile(data.bot_killed_filename):
        time.sleep(3)
        # создаём отдельный алёрт для .sh скрипта — перезапустим бот сами
        try:
            file_killed_write = open(data.bot_killed_filename, 'w', encoding='utf-8')
            file_killed_write.close()
            print("{0}\nBot has been killed off remotely by admin.\n".format(time.strftime(data.time, time.gmtime())))
            os._exit(-1)
        except RuntimeError:
            os._exit(-1)


def morning_msg():
    # TODO: добавить генерацию разных вариантов приветствий
    text = ''

    text += 'Доброе утро, народ!'
    # TODO: Проверять на наличие картинки
    text += ' [😺](https://t.me/funkcat/{})'.format(random.randint(1, 730))
    text += '\n'

    month_names = [u'января', u'февраля', u'марта',
                   u'апреля', u'мая', u'июня',
                   u'июля', u'августа', u'сентября',
                   u'октября', u'ноября', u'декабря']

    weekday_names = [u'понедельник', u'вторник', u'среда', u'четверг', u'пятница', u'суббота', u'воскресенье']

    now = datetime.now(pytz.timezone('Europe/Moscow'))

    text += 'Сегодня *{} {}*, *{}*.'.format(now.day, month_names[now.month - 1], weekday_names[now.weekday()])
    text += '\n\n'

    text += 'Котик дня:'

    # Отправить и запинить сообщение без уведомления
    msg = my_bot.send_message(data.my_chatID, text, parse_mode="Markdown", disable_web_page_preview=False)
    # TODO: Раскомментировать строчку, когда функция начнет делать что-то полезное
    # my_bot.pin_chat_message(data.my_chatID, msg.message_id, disable_notification=True)

    print('{}\nScheduled message sent\n'.format(now.strftime(data.time)))


while __name__ == '__main__':
    try:
        # если бот запущен .sh скриптом после падения — удаляем алёрт-файл
        try:
            os.remove(data.bot_down_filename)
        except OSError:
            pass
        try:
            os.remove(data.bot_update_filename)
        except OSError:
            pass
        # если бот запущен после вырубания нами — удаляем алёрт-файл
        try:
            os.remove(data.bot_killed_filename)
        except OSError:
            pass

        # Background-планировщик задач, чтобы бот продолжал принимать команды
        scheduler = BackgroundScheduler()

        scheduler.add_job(vk_listener.vkListener, 'interval', id='vkListener', replace_existing=True,
                          seconds=data.vk_interval)
        scheduler.add_job(update_bot, 'interval', id='update_bot', replace_existing=True, seconds=3)
        scheduler.add_job(kill_bot, 'interval', id='kill_bot', replace_existing=True, seconds=3)

        scheduler.add_job(morning_msg, 'cron', id='morning_msg', replace_existing=True, hour=7,
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
            time.strftime(data.time, time.gmtime())))
        time.sleep(5)
    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
        #        logging.exception(e)
        print(
            "{0}\nConnection Error.\nWe are offline. Reconnecting...\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(5)
    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        #        logging.exception(e)
        print("{0}\nRuntime Error.\nRetrying in 3 seconds.\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(3)
    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        #        logging.exception(e)
        print("{0}\nUnicode Encode Error. Someone typed in cyrillic.\nRetrying in 3 seconds.\n".format(
            time.strftime(data.time, time.gmtime())))
        time.sleep(3)
    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        #        logging.exception(e)
        print("\n{0}\nKeyboard Interrupt. Good bye.\n".format(time.strftime(data.time, time.gmtime())))
        sys.exit()

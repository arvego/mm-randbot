#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
import io
import logging
import os
import random
import re
import subprocess
import sys
import time
from builtins import any
from copy import copy
from xml.etree import ElementTree

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# сторонние модули
import arxiv
import pyowm
import pytz
import requests
import telebot
import vk_api
import wikipedia
from PIL import Image
from polyglot.detect import Detector
from apscheduler.schedulers.background import BackgroundScheduler
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

try:
    from html import escape
except:
    from cgi import escape

# модуль с настройками
import data
# модуль с токенами
import tokens

my_bot = telebot.TeleBot(tokens.bot, threaded=False)
my_bot_name = '@' + my_bot.get_me().username


# new command handler function
def commands_handler(cmnds, inline=False):
    def wrapped(msg):
        if not msg.text:
            return False
        split_message = re.split(r'[^\w@/]', msg.text.lower())
        if not inline:
            s = split_message[0]
            return ((s in cmnds)
                    or (s.endswith(my_bot_name) and s.split('@')[0] in cmnds))
        else:
            return any(cmnd in split_message
                       or cmnd + my_bot_name in split_message
                       for cmnd in cmnds)

    return wrapped


def user_action_log(message, text):
    print("{0}\nUser {1} (@{2}) {3}\n".format(time.strftime(data.time, time.gmtime()),
                                              message.from_user.id,
                                              message.from_user.username,
                                              text))


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
    # обрабатывает запрос и посылает пользователю картинку с результатом в случае удачи
    # сканируем и передаём всё, что ввёл пользователь после '/wolfram ' или '/wf '
    if not len(message.text.split()) == 1:
        your_query = ' '.join(message.text.split()[1:])
        user_action_log(message,
                        "entered this query for /wolfram:\n"
                        "{0}".format(your_query))
        response = requests.get("https://api.wolframalpha.com/v1/simple?appid="
                                + tokens.wolfram,
                                params={'i': your_query})
        # если всё хорошо, и запрос найден
        if response.status_code == 200:
            img_original = Image.open(io.BytesIO(response.content))
            img_cropped = img_original.crop((0, 95, 540,
                                             img_original.size[1] - 50))
            print("{}  {}".format(img_cropped.size[0], img_cropped.size[1]))
            temp = io.BytesIO()
            img_cropped.save(temp, format="png")
            temp.seek(0)
            if img_cropped.size[1] / img_cropped.size[0] > data.wolfram_max_ratio:
                print("Big image here.")
                my_bot.send_document(message.chat.id, temp,
                                     reply_to_message_id=message.message_id)
            else:
                my_bot.send_photo(message.chat.id, temp,
                                  reply_to_message_id=message.message_id)
                user_action_log(message,
                                "has received this Wolfram output:\n"
                                "{0}".format(response.url))
        # если всё плохо
        else:
            my_bot.reply_to(message,
                            "Запрос не найдён.\nЕсли ты ввёл его на русском, "
                            "то попробуй ввести его на английском.")
            user_action_log(message,
                            "didn't received any data".format(time.strftime(
                                data.time,
                                time.gmtime()),
                                message.from_user.id))
            # если пользователь вызвал /wolfram без аргумента
    else:
        my_bot.reply_to(message,
                        "Я не понял запрос.\nДля вызова Wolfram вводи команду "
                        "в виде `/wolfram <запрос>` или `/wf <запрос>`.")
        user_action_log(message, "called /wolfram without any arguments")


# команда /weather
@my_bot.message_handler(func=commands_handler(['/weather']))
# Получает погоду в Москве на сегодня и на три ближайших дня,
# пересылает пользователю
def my_weather(message):
    if not hasattr(my_weather, "weather_bold"):
        my_weather.weather_bold = False
    my_OWM = pyowm.OWM(tokens.owm)
    # где мы хотим узнать погоду
    my_obs = my_OWM.weather_at_place('Moscow')
    w = my_obs.get_weather()
    # статус погоды сейчас
    status = w.get_detailed_status()
    # температура сейчас
    temp_now = w.get_temperature('celsius')
    # limit=4, т.к. первый результат — текущая погода
    my_forecast = my_OWM.daily_forecast('Moscow,RU', limit=4)
    my_fc = my_forecast.get_forecast()
    # температуры на следующие три дня
    my_fc_temps = []
    # статусы на следующие три дня
    my_fc_statuses = []
    for wth in my_fc:
        my_fc_temps.append(str(wth.get_temperature('celsius')['day']))
        my_fc_statuses.append(str(wth.get_status()))
    # если вызвать /weather из кека
    if my_weather.weather_bold:
        my_bot.send_message(message.chat.id, data.weather_HAARP,
                            parse_mode="HTML")
        my_weather.weather_bold = False
        user_action_log(message, "got HAARP'd")
    # если всё нормально, то выводим результаты
    else:
        forecast = "The current temperature in Moscow is {2} C, " \
                   "and it is {3}.\n\n" \
                   "Tomorrow it will be {4} C, {5}.\n" \
                   "In 2 days it will be {6}, {7}.\n" \
                   "In 3 days it will be {8} C, {9}.\n\n".format(time.strftime(data.time, time.gmtime()),
                                                                 message.from_user.id, temp_now['temp'], status,
                                                                 my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2],
                                                                 my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3])
        my_bot.reply_to(message, forecast)
        user_action_log(message, "got that weather forecast:\n" + forecast)


# команда /wiki
@my_bot.message_handler(func=commands_handler(['/wiki']))
# Обрабатывает запрос и пересылает результат.
# Если запроса нет, выдаёт рандомный факт.
def my_wiki(message):
    # обрабатываем всё, что пользователь ввёл после '/wiki '
    if not len(message.text.split()) == 1:
        your_query = ' '.join(message.text.split()[1:])
        user_action_log(message,
                        "entered this query for /wiki:\n{0}".format(your_query))
        try:
            # определяем язык запроса
            detector = Detector(your_query)
            wikipedia.set_lang(detector.language.code)
            wiki_response = wikipedia.summary(your_query, sentences=7)
            if '\n  \n' in str(wiki_response):
                wiki_response = "{}...\n\n" \
                                "<i>В данной статье " \
                                "имеется математическая вёрстка. " \
                                "Пожалуйста, перейди по ссылке:</i>".format(
                    str(wiki_response).split('\n  \n', 1)[0])
            # print(wiki_response)
            # извлекаем ссылку на саму статью
            wiki_url = wikipedia.page(your_query).url
            # извлекаем название статьи
            wiki_title = wikipedia.page(your_query).title
            my_bot.reply_to(message, "<b>{0}.</b>\n{1}\n\n{2}".format(
                wiki_title,
                wiki_response,
                wiki_url),
                            parse_mode="HTML")
            user_action_log(message,
                            "got Wikipedia article\n{0}".format(str(wiki_title)))
        # всё плохо, ничего не нашли
        except wikipedia.exceptions.PageError:
            my_bot.reply_to(message, "Запрос не найден.")
            user_action_log(message, "didn't received any data.")
        # нашли несколько статей, предлагаем пользователю список
        except wikipedia.exceptions.DisambiguationError as ex:
            wiki_options = ex.options
            my_bot.reply_to(message,
                            "Пожалуйста, уточни запрос. "
                            "Выбери, что из перечисленного имелось в виду, "
                            "и вызови /wiki ещё раз.\n"
                            + "\n".join(map(str, wiki_options)))
            print("There are multiple possible pages for that article.\n")
            # берём рандомную статью на рандомном языке (языки в data.py)
    else:
        wikipedia.set_lang(random.choice(data.wiki_langs))
        try:
            wikp = wikipedia.random(pages=1)
            wikpd = wikipedia.page(wikp)
            wikiFact = wikipedia.summary(wikp, sentences=3)
            my_bot.reply_to(message,
                            "<b>{0}.</b>\n{1}".format(wikpd.title, wikiFact),
                            parse_mode="HTML")
            user_action_log(message,
                            "got Wikipedia article\n{0}".format(str(wikp)))
        except wikipedia.exceptions.DisambiguationError:
            wikp = wikipedia.random(pages=1)
            wikiVar = wikipedia.search(wikp, results=1)
            print("There are multiple possible pages for that article.\n")
            # wikpd = wikipedia.page(str(wikiVar[0]))
            wikiFact = wikipedia.summary(wikiVar, sentences=4)
            my_bot.reply_to(message,
                            "<b>{0}.</b>\n{1}".format(wikp, wikiFact),
                            parse_mode="HTML")


# команда /kek
@my_bot.message_handler(func=commands_handler(['/kek']))
# открывает соответствующие файл и папку, кидает рандомную строчку из файла,
# или рандомную картинку или гифку из папки
def my_kek(message):
    if not hasattr(my_kek, "kek_bang"):
        my_kek.kek_bang = time.time()
    if not hasattr(my_kek, "kek_crunch"):
        my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
    if not hasattr(my_kek, "kek_enable"):
        my_kek.kek_enable = True
    if not hasattr(my_kek, "kek_counter"):
        my_kek.kek_counter = 0
    if not hasattr(my_weather, "weather_bold"):
        my_weather.weather_bold = False

    kek_init = True

    if message.chat.id == int(data.my_chatID):
        if my_kek.kek_counter == 0:
            my_kek.kek_bang = time.time()
            my_kek.kek_crunch = my_kek.kek_bang + 60 * 60
            my_kek.kek_counter += 1
            kek_init = True
        elif (my_kek.kek_counter >= data.limit_kek
              and time.time() <= my_kek.kek_crunch):
            kek_init = False
        elif time.time() > my_kek.kek_crunch:
            my_kek.kek_counter = -1
            kek_init = True

    if kek_init and my_kek.kek_enable:
        if message.chat.id == data.my_chatID:
            my_kek.kek_counter += 1
        your_destiny = random.randint(1, 30)
        # если при вызове не повезло, то кикаем из чата
        if your_destiny == 13:
            my_bot.reply_to(message,
                            "Предупреждал же, что кикну. "
                            "Если не предупреждал, то ")
            my_bot.send_document(message.chat.id,
                                 'https://t.me/mechmath/127603',
                                 reply_to_message_id=message.message_id)
            try:
                if int(message.from_user.id) in data.admin_ids:
                    my_bot.reply_to(message,
                                    "...Но против хозяев не восстану.")
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
            type_of_KEK = random.randint(1, 33)
            # 1/33 шанс на картинку или гифку
            if type_of_KEK == 9:
                all_imgs = os.listdir(data.dir_location_kek)
                rand_file = random.choice(all_imgs)
                your_file = open(data.dir_location_kek + rand_file, "rb")
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
                file_KEK = open(data.file_location_kek, 'r', encoding='utf-8')
                your_KEK = random.choice(file_KEK.readlines())
                my_weather.weather_bold = str(your_KEK) == str("Чекни /weather.\n")
                # если попалась строчка вида '<sticker>ID', то шлём стикер по ID
                if str(your_KEK).startswith("<sticker>"):
                    sticker_id = str(your_KEK[9:]).strip()
                    my_bot.send_sticker(message.chat.id, sticker_id,
                                        reply_to_message_id=message.message_id)
                # иначе просто шлём обычный текст
                else:
                    my_bot.reply_to(message,
                                    str(your_KEK).replace("<br>", "\n"))
                file_KEK.close()
                user_action_log(message,
                                "got that kek:\n{0}".format(str(your_KEK).replace("<br>", "\n")))

        if my_kek.kek_counter == data.limit_kek - 10:
            time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()),
                                    60)
            my_bot.reply_to(message,
                            "<b>Внимание!</b>\nЭтот чат может покекать "
                            "ещё не более {0} раз до истечения кекочаса "
                            "(через {1} мин. {2} сек.).\n"
                            "По истечению кекочаса "
                            "счётчик благополучно сбросится.".format(data.limit_kek - my_kek.kek_counter,
                                                                     time_remaining[0], time_remaining[1]),
                            parse_mode="HTML")
        if my_kek.kek_counter == data.limit_kek:
            time_remaining = divmod(int(my_kek.kek_crunch) - int(time.time()), 60)
            my_bot.reply_to(message,
                            "<b>EL-FIN!</b>\n"
                            "Теперь вы сможете кекать "
                            "только через {0} мин. {1} сек.".format(time_remaining[0], time_remaining[1]),
                            parse_mode="HTML")
        my_kek.kek_counter += 1


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


def disa_vk_report(disa_chromo, message):
    login, password = data.vk_disa_login, data.vk_disa_password
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()
    wall = vk.wall.get(owner_id=data.vk_disa_groupID, count=1)
    if time.localtime(wall['items'][0]['date'])[2] == time.localtime()[2]:
        disa_chromo_post = disa_chromo - 46
        try:
            old_chromo = int(wall['items'][0]['text'])
            disa_chromo_post += old_chromo
        except Exception as ex:
            logging.error(ex)
            disa_chromo_post = disa_chromo
        vk.wall.edit(owner_id=data.vk_disa_groupID,
                     post_id=wall['items'][0]['id'],
                     message=str(disa_chromo_post))
    else:
        disa_chromo_post = 46 + disa_chromo
        vk.wall.post(owner_id=data.vk_disa_groupID,
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
    print("{0}\nDisa summary printed".format(time.strftime(data.time,
                                                           time.gmtime())))
    disa_chromo = 46
    with open(data.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))
    disa.disa_first = True


# команда /disa [V2.069] (от EzAccount)
@my_bot.message_handler(func=commands_handler(['/disa'], inline=True))
def disa(message):
    if not hasattr(disa, "disa_first"):
        disa.disa_first = True
    if not hasattr(disa, "disa_bang"):
        disa.disa_bang = time.time()
    if not hasattr(disa, "disa_crunch"):
        disa.disa_crunch = disa.disa_bang + 60 * 60

    disa_init = False
    # пытаемся открыть файл с количеством Дисиных хромосом
    try:
        with open(data.file_location_disa, 'r', encoding='utf-8') as file_disa_read:
            disa_chromo = int(file_disa_read.read())
    except (IOError, OSError, ValueError):
        disa_chromo = 46
        pass
    disa_chromo += 1
    with open(data.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))
    # если прошёл час с момента первого вызова, то натёкшее число пытаемся
    # загрузить на ВК
    #    if (message.chat.id == int(data.my_chatID)):

    user_action_log(message, "added chromosome to Disa")
    if message.chat.type == "supergroup":
        if disa.disa_first:
            disa.disa_bang = time.time()
            disa.disa_crunch = disa.disa_bang + 60 * 60
            disa.disa_first = False
        elif (not disa.disa_first) and (time.time() >= disa.disa_crunch):
            disa_init = True
        print("{0}\n State: init={1} "
              "first={2} "
              "bang={3} "
              "crunch={4}\n".format(time.strftime(data.time, time.gmtime()),
                                    disa_init, disa.disa_first,
                                    disa.disa_bang, disa.disa_crunch))
    # запись счетчика в вк
    if disa_init:
        disa_vk_report(disa_chromo, message)


@my_bot.message_handler(func=commands_handler(['/antidisa']))
def antiDisa(message):
    try:
        with open(data.file_location_disa, 'r', encoding='utf-8') as file_disa_read:
            disa_chromo = int(file_disa_read.read())
    except (IOError, OSError, ValueError):
        disa_chromo = 46
        pass
    disa_chromo -= 1

    with open(data.file_location_disa, 'w', encoding='utf-8') as file_disa_write:
        file_disa_write.write(str(disa_chromo))


# команда /arxiv
@my_bot.message_handler(func=commands_handler(['/arxiv']))
def arxiv_checker(message):
    delay = 120
    if not hasattr(arxiv_checker, "last_call"):
        arxiv_checker.last_call = datetime.datetime.utcnow() \
                                  - datetime.timedelta(seconds=delay + 1)
    diff = datetime.datetime.utcnow() - arxiv_checker.last_call
    if diff.total_seconds() < delay:
        user_action_log(message,
                        "attempted to call arxiv command "
                        "after {0} seconds".format(diff.total_seconds()))
        return
    arxiv_checker.last_call = datetime.datetime.utcnow()
    if len(message.text.split()) > 1:
        arxiv_search(' '.join(message.text.split(' ')[1:]), message)
    else:
        arxiv_random(message)


def arxiv_search(query, message):
    try:
        arxiv_search_res = arxiv.query(search_query=query, max_results=3)
        query_answer = ''
        for paper in arxiv_search_res:
            end = '…' if len(paper['summary']) > 251 else ''
            query_answer += \
                '• {0}. <a href="{1}">{2}</a>. {3}{4}\n'.format(
                    paper['author_detail']['name'], paper['arxiv_url'],
                    escape(paper['title'].replace('\n', ' ')),
                    escape(paper['summary'][0:250].replace('\n', ' ')),
                    end)
        print(query_answer)
        user_action_log(message,
                        "called arxiv search with query {0}".format(query))
        my_bot.reply_to(message, query_answer, parse_mode="HTML")

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("{0}\nUnknown Exception:\n{1}: {2}\nat {3} line {4}\n\n"
              "Creating the alert file.\n".format(
            time.strftime(data.time, time.gmtime()),
            exc_type, ex, fname, exc_tb.tb_lineno))


def arxiv_random(message):
    user_action_log(message, "made arxiv random query")
    try:
        eastern = pytz.timezone('US/Eastern')
        eastern_time = datetime.datetime.now(eastern)
        # publications on 20:00
        if eastern_time.hour < 20:
            eastern_time -= datetime.timedelta(days=1)
        # no publications on friday and saturday
        if eastern_time.weekday() == 5:
            eastern_time -= datetime.timedelta(days=2)
        elif eastern_time.weekday() == 4:
            eastern_time -= datetime.timedelta(days=1)
        last_published_date = eastern_time.strftime("%Y-%m-%d")
        response = requests.get('http://export.arxiv.org/oai2',
                                params={'verb': 'ListIdentifiers',
                                        'set': 'math',
                                        'metadataPrefix': 'oai_dc',
                                        'from': last_published_date})
        print(
            "{0}\nRandom arxiv paper since {1}\n".format(
                time.strftime(data.time, time.gmtime()),
                last_published_date))
        # если всё хорошо
        if response.status_code == 200:
            response_tree = ElementTree.fromstring(response.content)
            num_of_papers = len(response_tree[2])
            paper_index = random.randint(0, num_of_papers)
            paper_arxiv_id = response_tree[2][paper_index][0].text.split(':')[-1]  # hardcoded
            papep_obj = arxiv.query(id_list=[paper_arxiv_id])[0]
            query_answer = '{0}. <a href="{1}">{2}</a>. {3}\n'.format(
                papep_obj['author_detail']['name'],
                papep_obj['arxiv_url'],
                escape(papep_obj['title'].replace('\n', ' ')),
                escape(papep_obj['summary'].replace('\n', ' '))
            )
            my_bot.reply_to(message, query_answer, parse_mode="HTML")
            paper_link = papep_obj['pdf_url'] + '.pdf'
            user_action_log(message,
                            "arxiv random query was successful: "
                            "got paper {0}\n".format(papep_obj['arxiv_url']))
            # TODO(randl): doesn't send. Download and delete?
            my_bot.send_document(message.chat.id, data=paper_link)
        elif response.status_code == 503:
            # слишком часто запрашиваем
            print("{0}\nToo much queries. "
                  "10 minutes break should be enough\n".format(
                time.strftime(data.time, time.gmtime())))
            arxiv_checker.last_call = datetime.datetime.utcnow() - datetime.timedelta(seconds=610)
        else:
            # если всё плохо
            user_action_log(message, "arxiv random query failed: "
                                     "response {0}\n".format(response.status_code))

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("{0}\nUnknown Exception:\n"
              "{1}: {2}\nat {3} line {4}\n\n".format(
            time.strftime(data.time, time.gmtime()),
            exc_type, ex, fname, exc_tb.tb_lineno))


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
@my_bot.message_handler(func=lambda message: message.from_user.id in data.admin_ids)
def admin_toys(message):
    if not hasattr(my_kek, "kek_enable"):
        my_kek.kek_enable = True

    command = message.text.split()[0].lower()
    if command in ["/post", "/prize", "/kek_enable", "/kek_disable", "/update_bot", "/kill"]:
        user_action_log(message, "has launched admin tools")

    if command == "/post":
        admin_post(message)
    elif command == "/prize":
        admin_prize(message)
    elif command == "/kek_enable":
        my_kek.kek_enable = True
        user_action_log(message, "enabled kek")
    elif command == "/kek_disable":
        my_kek.kek_enable = False
        user_action_log(message, "disabled kek")
    elif command == "/update_bot":
        file_update_write = open(data.bot_update_filename, 'w', encoding='utf-8')
        file_update_write.close()
    elif command.startswith("/kill"):
        if not len(message.text.split()) == 1:
            my_bot.reply_to(message, "Прощай, жестокий чат. ;~;")


# Диса тупит (от AChehonte)
@my_bot.message_handler(content_types=["text"])
def check_disa(message):
    # добавления счетчика в функцию
    if not hasattr(check_disa, "disa_counter"):
        check_disa.disa_counter = 0

    # проверяем Диса ли это
    if message.from_user.id != data.disa_id:
        return

    # проверяем что идет серия из коротких предложений
    if len(message.text) > data.length_of_stupid_message:
        check_disa.disa_counter = 0
        return

    check_disa.disa_counter += 1

    # проверяем, будем ли отвечать Дисе
    disa_trigger = random.randint(1, 6)
    if check_disa.disa_counter >= data.too_many_messages and disa_trigger == 2:
        my_bot.reply_to(message, random.choice(data.stop_disa))
        check_disa.disa_counter = 0

    # записываем в файл увеличенный счетчик хромосом
    try:
        with open(data.file_location_disa, 'r+', encoding='utf-8') as file:
            disa_chromo = str(int(file.read()) + 1)
            file.seek(0)
            file.write(disa_chromo)
            file.truncate()
    except Exception as ex:
        logging.error(ex)
        pass


def vk_find_last_post():
    # коннектимся к API через requests. Берём первые два поста
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': tokens.vk, 'owner_id': data.vkgroup_id, 'count': 2,
                                    'offset': 0})
    try:
        # создаём json-объект для работы
        posts = response.json()['response']
    except Exception as ex:
        time.sleep(3)
        raise ex

    # пытаемся открыть файл с датой последнего поста
    try:
        file_lastdate_read = open(data.vk_update_filename, 'r', encoding='utf-8')
        last_recorded_postdate = file_lastdate_read.read()
        file_lastdate_read.close()
    except IOError:
        last_recorded_postdate = -1
        pass
    try:
        int(last_recorded_postdate)
    except ValueError:
        last_recorded_postdate = -1
        pass
    # сверяем два верхних поста на предмет свежести, т.к. верхний может быть запинен
    post = posts[-2] if posts[-2]['date'] >= posts[-1]['date'] else posts[-1]
    post_date = post['date']

    # наконец, сверяем дату свежего поста с датой, сохранённой в файле
    vk_initiate = False
    if post_date > int(last_recorded_postdate):
        vk_initiate = True
        # записываем дату поста в файл, чтобы потом сравнивать новые посты
        file_lastdate_write = open(data.vk_update_filename, 'w', encoding='utf-8')
        file_lastdate_write.write(str(post_date))
        file_lastdate_write.close()

    return post, vk_initiate


def vk_get_repost_text(post):
    original_poster_id = int(post['copy_owner_id'])
    # если значение ключа 'copy_owner_id' отрицательное, то перед нами репост из группы
    if original_poster_id < 0:
        response_OP = requests.get('https://api.vk.com/method/groups.getById',
                                   params={'group_ids': -original_poster_id})
        name_OP = response_OP.json()['response'][0]['name']
        screenname_OP = response_OP.json()['response'][0]['screen_name']
        # добавляем строку, что это репост из такой-то группы
        return "\n\n<a href=\"<web_preview>\">📢</a> <a href=\"https://vk.com/wall{}_{}\">Репост</a> " \
               "из группы <a href=\"https://vk.com/{}\">{}</a>:\n".format(data.vkgroup_id, post['id'], screenname_OP,
                                                                          name_OP)
    # если значение ключа 'copy_owner_id' положительное, то репост пользователя
    else:
        response_OP = requests.get('https://api.vk.com/method/users.get',
                                   params={'access_token': tokens.vk,
                                           'user_id': original_poster_id})
        name_OP = "{0} {1}".format(response_OP.json()['response'][0]['first_name'],
                                   response_OP.json()['response'][0]['last_name'], )
        screenname_OP = response_OP.json()['response'][0]['uid']
        # добавляем строку, что это репост такого-то пользователя
        return ("\n\n<a href=\"<web_preview>\">📢</a> <a href=\"https://vk.com/wall{}_{}\">Репост</a> "
                "пользователя <a href=\"https://vk.com/id{}\">{}</a>:\n").format(data.vkgroup_id, post['id'],
                                                                                 screenname_OP, name_OP)


def vk_post_get_links(post):
    links = ''
    web_preview_links = []
    vk_annot_link = False
    vk_annot_doc = False
    vk_annot_video = False
    try:
        for attachment in post['attachments']:
            # проверяем есть ли ссылки в посте
            if 'link' in attachment:
                post_url_raw = attachment['link']['url']
                post_url = "<a href=\"{}\">{}</a>\n".format(post_url_raw, attachment['link']['title'])
                if not vk_annot_link:
                    links += '\n— Ссылка:\n'
                    vk_annot_link = True
                links += post_url
                web_preview_links.append(post_url_raw)
                print("Successfully extracted a link:\n{0}\n".format(post_url_raw))

            # проверяем есть ли документы в посте. GIF отрабатываются отдельно
            # в vkListener
            if 'doc' in attachment and attachment['doc']['ext'] != 'gif':
                post_url_raw = attachment['doc']['url']
                doc_name = attachment['doc']['title']
                doc_size = round(attachment['doc']['size'] / 1024 / 1024, 2)
                post_url = "<a href=\"{}\">{}</a>, размер {} Мб\n".format(post_url_raw, doc_name, doc_size)
                if not vk_annot_doc:
                    links += '\n— Приложения:\n'
                    vk_annot_doc = True
                links += post_url
                print("Successfully extracted a document's link:\n{0}\n".format(post_url_raw))

            # проверяем есть ли видео в посте
            if 'video' in attachment:
                post_video_owner = attachment['video']['owner_id']
                post_video_vid = attachment['video']['vid']
                # TODO: fix link for youtube and other
                post_url_raw = "https://vk.com/video{}_{}".format(post_video_owner, post_video_vid)
                post_url = "<a href=\"{}\">{}</a>\n".format(post_url_raw, attachment['video']['title'])
                if not vk_annot_video:
                    links += '\n— Видео:\n'
                    vk_annot_video = True
                links += post_url
                web_preview_links.insert(0, post_url_raw)
                print("Successfully extracted a video's link:\n{0}\n".format(post_url_raw))

    except KeyError:
        pass
    return links, web_preview_links


def vk_send_new_post(destination, vk_final_post, img_src, show_preview):
    # Отправляем текст, нарезая при необходимости
    for text in text_cuts(vk_final_post):
        my_bot.send_message(destination,
                            text,
                            parse_mode="HTML",
                            disable_web_page_preview=not show_preview)

    # Отправляем все изображения
    for img in img_src:
        if img['type'] == 'img':
            my_bot.send_photo(destination, copy(img['data']))
        if img['type'] == 'gif':
            my_bot.send_document(destination, img['data'])


# Вспомогательная функция для нарезки постов ВК
def text_cuts(text):
    max_cut = 3000
    last_cut = 0
    dot_anchor = 0
    nl_anchor = 0

    # я не очень могу в генераторы, так вообще можно писать?
    if len(text) < max_cut:
        yield text[last_cut:]
        return

    for i in range(len(text)):
        if text[i] == '\n':
            nl_anchor = i + 1
        if text[i] == '.' and text[i + 1] == ' ':
            dot_anchor = i + 2

        if i - last_cut > max_cut:
            if nl_anchor > last_cut:
                yield text[last_cut:nl_anchor]
                last_cut = nl_anchor
            elif dot_anchor > last_cut:
                yield text[last_cut:dot_anchor]
                last_cut = dot_anchor
            else:
                yield text[last_cut:i]
                last_cut = i

            if len(text) - last_cut < max_cut:
                yield text[last_cut:]
                return

    yield text[last_cut:]


# проверяет наличие новых постов ВК в паблике Мехмата и кидает их при наличии
def vkListener():
    try:
        # ищем последний пост
        try:
            post, vk_initiate = vk_find_last_post()
        except:
            return

        # инициализируем строку, чтобы он весь текст кидал одним сообщением
        vk_final_post = ''
        show_preview = False
        # если в итоге полученный пост — новый, то начинаем операцию
        if vk_initiate:
            print("{0}\nWe have new post in Mechmath's VK public.\n".format(time.strftime(data.time, time.gmtime())))
            # если это репост, то сначала берём сообщение самого мехматовского поста
            if 'copy_owner_id' in post or 'copy_text' in post:
                if 'copy_text' in post:
                    post_text = post['copy_text']
                    vk_final_post += post_text.replace("<br>", "\n")
                # пробуем сформулировать откуда репост
                if 'copy_owner_id' in post:
                    vk_final_post += vk_get_repost_text(post)

            else:
                response_OP = requests.get('https://api.vk.com/method/groups.getById',
                                           params={'group_ids': -(int(data.vkgroup_id))})
                name_OP = response_OP.json()['response'][0]['name']
                screenname_OP = response_OP.json()['response'][0]['screen_name']
                vk_final_post += (
                    "\n\n<a href=\"<web_preview>\">📃</a> <a href=\"https://vk.com/wall{}_{}\">Пост</a> в группе "
                    "<a href=\"https://vk.com/{}\">{}</a>:\n").format(data.vkgroup_id, post['id'],
                                                                      screenname_OP, name_OP)
            try:
                # добавляем сам текст репоста
                post_text = post['text']
                vk_final_post += post_text.replace("<br>", "\n") + "\n"
            except KeyError:
                pass
            # смотрим на наличие ссылок, если есть — добавляем
            links, web_preview_links = vk_post_get_links(post)
            vk_final_post += links
            # если есть вики-ссылки на профили пользователей ВК вида '[screenname|real name]',
            # то превращаем ссылки в кликабельные
            try:
                pattern = re.compile(r"\[([^|]+)\|([^|]+)\]", re.U)
                results = pattern.findall(vk_final_post, re.U)
                for i in results:
                    screen_name_user = i[0]
                    real_name_user = i[1]
                    link = "<a href=\"https://vk.com/{0}\">{1}</a>".format(screen_name_user, real_name_user)
                    unedited = "[{0}|{1}]".format(screen_name_user, real_name_user)
                    vk_final_post = vk_final_post.replace(unedited, link)
            except Exception as ex:
                logging.exception(ex)

            # смотрим на наличие картинок и GIF
            img_src = []
            try:
                for attachment in post['attachments']:
                    # если есть, то смотрим на доступные размеры.
                    # Для каждой картинки пытаемся выудить ссылку на самое большое расширение, какое доступно
                    if 'photo' in attachment:
                        wegot = False
                        for size in ['src_xxbig', 'src_xbig', 'src_big', 'src']:
                            if size in attachment['photo']:
                                post_attach_src = attachment['photo'][size]
                                wegot = True
                                break

                        if wegot:
                            request_img = requests.get(post_attach_src)
                            img_vkpost = io.BytesIO(request_img.content)
                            img_src.append({'data': img_vkpost,
                                            'type': 'img'})
                            print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                        else:
                            print("Couldn't extract photo URL from a VK post.\n")
                    elif ('doc' in attachment
                          and ('type' in attachment['doc']
                               and attachment['doc']['type'] == 3)
                          or ('ext' in attachment['doc']
                              and attachment['doc']['ext'] == 'gif')):
                        post_attach_src = gif_vkpost = attachment['doc']['url']
                        img_src.append({'data': gif_vkpost,
                                        'type': 'gif'})
                        print("Successfully extracted GIF URL:\n{0}\n".format(post_attach_src))

            except KeyError:
                pass

            for link in web_preview_links:
                show_preview = True
                vk_final_post = vk_final_post.replace("<web_preview>", link)
                break

            vk_final_post = vk_final_post.replace("<br>", "\n")

            vk_send_new_post(data.my_chatID, vk_final_post, img_src, show_preview)
            vk_send_new_post(data.my_channel, vk_final_post, img_src, show_preview)

        time.sleep(5)
    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout:
        # logging.exception(e)
        print(
            "{0}\nRead Timeout in vkListener() function. Because of Telegram API.\n"
            "We are offline. Reconnecting in 5 seconds.\n".format(
                time.strftime(data.time, time.gmtime())))
    # если пропало соединение, то пытаемся снова
    except ConnectionError:
        # logging.exception(e)
        print("{0}\nConnection Error in vkListener() function.\nWe are offline. Reconnecting...\n".format(
            time.strftime(data.time, time.gmtime())))
    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError:
        # logging.exception(e)
        print("{0}\nRuntime Error in vkListener() function.\nRetrying in 3 seconds.\n".format(
            time.strftime(data.time, time.gmtime())))


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

        scheduler.add_job(vkListener, 'interval', id='vkListener', replace_existing=True, seconds=data.vk_interval)
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

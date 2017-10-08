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

# сторонние модули
import pyowm
import pytz
import requests
import wikipedia
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from polyglot.detect import Detector
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

# модуль с настройками
import data
# модуль с токенами
import tokens
from bot_shared import my_bot, commands_handler, user_action_log
import arxiv_queries, disa_commands
import vk_listener

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
    try:
        my_OWM = pyowm.OWM(tokens.owm)
        # где мы хотим узнать погоду
        my_obs = my_OWM.weather_at_place('Moscow')
    except pyowm.exceptions.unauthorized_error.UnauthorizedError:
        print("Your API subscription level does not allow to check weather")
        return
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

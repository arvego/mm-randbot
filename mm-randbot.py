#!/usr/bin/env python
#_*_ coding: utf-8 _*_
import io
import logging
import os
import random
import re
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import sys
import threading
import time

#сторонние модули
import pyowm
import telebot
import wikipedia

#модуль с настройками
import data
#модуль с токенами
import tokens


my_bot = telebot.TeleBot(tokens.bot, threaded=False)
'''
global user_registr
global user_id
global user_correct_num
global user_status
global user_max
user_registr={}
'''
global weather_bold
weather_bold = False

global kek_counter
kek_counter = 0
global kek_bang
global kek_crunch

#global access
#access = False

reload(sys)
sys.setdefaultencoding('utf-8')


#команды /start, /help, /links и /wifi
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ('/start', '/help', '/links', '/links@algebrach_bot', '/wifi', '/wifi@algebrach_bot'))
def myData(message):
    command = message.text.lower().split()[0]
    if command == '/start':
        file_name = data.file_location_start
        print("{0}\nUser {1} started using the bot.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif command == '/help':
        file_name = data.file_location_help
        print("{0}\nUser {1} looked for help.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif (command == '/links') or (command == '/links@algebrach_bot'):
        file_name = data.file_location_links
        print("{0}\nUser {1} requested Mechmath links.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif (command == '/wifi') or (command == '/wifi@algebrach_bot'):
        file_name =  data.file_location_wifi
        print("{0}\nUser {1} requested the Wi-Fi list.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    else:
        return
    with open(file_name, 'r') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)

#команды /task и /maths
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ('/task', '/task@algebrach_bot', '/maths', '/maths@algebrach_bot'))
#идёт в соответствующую папку и посылает рандомную картинку
def myRandImg(message):
    for s in str(message.text).lower().split():
        if (s == "/task" or s == "/task@algebrach_bot"):
            path = data.dir_location_task
            print("{0}\nUser {1} asked for a challenge.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            if not len(message.text.split()) == 1:
                if (s == "/task"):
                    your_difficulty = message.text[6:]
                elif (s == "/task@algebrach_bot"):
                    your_difficulty = message.text[20:]
                if your_difficulty in data.difficulty:
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    while (not rand_img.startswith(your_difficulty)):
                        rand_img = random.choice(all_imgs)
                    your_img = open(path+rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                    print("{0}\nUser {1} chose a difficulty level \'{2}\' and got that image:\n{3}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_difficulty, your_img.name))
                    your_img.close()
                else:
                    my_bot.reply_to(message, "Доступно только три уровня сложности:\n{0}\nВыбираю рандомную задачу:".format(data.difficulty))
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    your_img = open(path+rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                    print("{0}\nUser {1} chose a non-existent difficuly level \'{2}\' and got that image:\n{3}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_difficulty, your_img.name))
                    your_img.close()
            else:
                all_imgs = os.listdir(path)
                rand_img = random.choice(all_imgs)
                your_img = open(path+rand_img, "rb")
                my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                print("{0}\nUser {1} got that image:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_img.name))
                your_img.close()
        elif (s == "/maths" or s == "/maths@algebrach_bot"):
            path = data.dir_location_maths
            print("{0}\nUser {1} asked for maths.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            if not len(message.text.split()) == 1:
                if (s == "/maths"):
                    your_subject = message.text[7:]
                elif (s == "/maths@algebrach_bot"):
                    your_subject = message.text[21:]
                your_subject = your_subject.lower()
                if your_subject in data.subjects:
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    while (not rand_img.startswith(your_subject)):
                        rand_img = random.choice(all_imgs)
                    your_img = open(path+rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                    print("{0}\nUser {1} chose subject \'{2}\' and got that image:\n{3}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_subject, your_img.name))
                    your_img.close()
                else:
                    my_bot.reply_to(message, "На данный момент доступны факты только по следующим предметам:\n{0}\nВыбираю рандомный факт:".format(data.subjects))
                    all_imgs = os.listdir(path)
                    rand_img = random.choice(all_imgs)
                    your_img = open(path+rand_img, "rb")
                    my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                    print("{0}\nUser {1} chose a non-existent subject \'{2}\' and got that image:\n{3}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_subject, your_img.name))
                    your_img.close()
            else:
                all_imgs = os.listdir(path)
                rand_img = random.choice(all_imgs)
                your_img = open(path+rand_img, "rb")
                my_bot.send_photo(message.chat.id, your_img, reply_to_message_id=message.message_id)
                print("{0}\nUser {1} got that image:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_img.name))
                your_img.close()

#команда /d6
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ('/d6', '/d6@algebrach_bot'))
#рандомно выбирает элементы из списка значков
###желательно найти способ их увеличить или заменить на ASCII арт
def myD6(message):
    d6 = data.d6_symbols
    roll1 = random.choice(d6)
    roll2 = random.choice(d6)
    my_bot.reply_to(message, "{0}  {1}".format(roll1, roll2))
    print("{0}\nUser {1} got that D6 output: {2}  {3}.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, roll1, roll2))

#команда /roll
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ('/roll', '/roll@algebrach_bot'))
#генерует случайное целое число, в засимости от него может кинуть картинку или гифку
def myRoll(message):
    rolled_number = random.randint(0,100)
    my_bot.reply_to(message, str(rolled_number).zfill(2))
    print("{0}\nUser {1} recieved {2}.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, rolled_number))


#команда /truth
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['/truth', '/truth@algebrach_bot'])
def myTruth(message):
#открывает файл и отвечает пользователю рандомными строками из него
    the_TRUTH = random.randint(1, 1000)
    if not the_TRUTH == 666:
        file_TRUTH = open(data.file_location_truth, 'r')
        TRUTH = random.choice(file_TRUTH.readlines())
        my_bot.reply_to(message, str(TRUTH).replace("<br>", "\n"))
        file_TRUTH.close()
        print("{0}\nUser {1} has discovered the Truth:\n{2}".format(time.strftime(data.time, time.gmtime()), message.from_user.id, str(TRUTH).replace("<br>", "\n")))
    else:
        my_bot.reply_to(message, data.the_TRUTH, parse_mode="HTML")
        print("{0}\nUser {1} has discovered the Ultimate Truth.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))

#команда /wolfram (/wf)
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['/wolfram', '/wolfram@algebrach_bot', '/wf'])
def wolframSolver(message):
#обрабатывает запрос и посылает пользователю картинку с результатом в случае удачи
    wolfram_query = []
#сканируем и передаём всё, что ввёл пользователь после '/wolfram ' или '/wf '
    if not len(message.text.split()) == 1:
        for s in message.text.lower().split():
            if s == "/wolfram":
                your_query = message.text[9:]
                break
            elif s == "/wolfram@algebrach_bot":
                your_query = message.text[23:]
                break
            elif s == "/wf":
                your_query = message.text[4:]
                break
        print("{0}\nUser {1} entered this query for /wolfram:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_query))
        response = requests.get("https://api.wolframalpha.com/v1/simple?appid="+tokens.wolfram, params={'i': your_query})
#если всё хорошо, и запрос найден
        if response.status_code == 200:
            img_wolfram = io.BytesIO(response.content)
            my_bot.send_photo(message.chat.id, img_wolfram, reply_to_message_id=message.message_id)
            print("{0}\nUser {1} has received this Wolfram output:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, response.url))
#если всё плохо
        else:
            my_bot.reply_to(message, "Запрос не найдён.\nЕсли ты ввёл его на русском, то попробуй ввести его на английском.")
            print("{0}\nUser {1} didn't received any data.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
#если пользователь вызвал /wolfram без аргумента
    else:
        my_bot.reply_to(message, "Я не понял запрос.\nДля вызова Wolfram вводи команду в виде \'/wolfram <запрос>\' или \'/wf <запрос>\'.")
        print("{0}\nUser {1} called /wolfram without any arguments.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))

#команда /weather
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['/weather', '/weather@algebrach_bot'])
#получает погоду в Москве на сегодня и на три ближайших дня, пересылает пользователю
def myWeather(message):
    global weather_bold
    my_OWM = pyowm.OWM(tokens.owm)
#где мы хотим узнать погоду
    my_obs = my_OWM.weather_at_place('Moscow')
    w = my_obs.get_weather()
#статус погоды сейчас
    status = w.get_detailed_status()
#температура сейчас
    temp_now = w.get_temperature('celsius')
#limit=4, т.к. первый результат -- текущая погода
    my_forecast = my_OWM.daily_forecast('Moscow,RU', limit=4)
    my_fc = my_forecast.get_forecast()
#температуры на следующие три дня
    my_fc_temps = []
#статусы на следующие три дня
    my_fc_statuses = []
    for wth in my_fc:
        my_fc_temps.append(str(wth.get_temperature('celsius')['day']))
        my_fc_statuses.append(str(wth.get_status()))
#если вызвать /weather из кека
    if weather_bold:
        my_bot.send_message(message.chat.id, data.weather_HAARP, parse_mode="HTML")
        weather_bold = False
        print("{0}\nUser {1} got HAARP'd.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
#если всё нормально, то выводим результаты
    else:
        my_bot.reply_to(message, "The current temperature in Moscow is {2} C, and it is {3}.\n\nTomorrow it will be {4} C, {5}.\nIn 2 days it will be {6}, {7}.\nIn 3 days it will be {8} C, {9}.\n\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, temp_now['temp'], status, my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2], my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3]))
        print("{0}\nUser {1} got that weather forecast:\nThe current temperature in Moscow is {2} C, and it is {3}.\nTomorrow it will be {4} C, {5}.\nIn 2 days it will be {6}, {7}.\nIn 3 days it will be {8} C, {9}.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, temp_now['temp'], status, my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2], my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3]))

#команда /wiki
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['/wiki', '/wiki@algebrach_bot'])
#обрабатывает запрос и пересылает результат, или выдаёт рандомный факт в случае отсутствия запроса
def myWiki(message):
    wiki_query = []
#обрабатываем всё, что пользователь ввёл после '/wiki '
    if not len(message.text.split()) == 1:
        s = message.text.lower().split()[0]
        if (s == "/wiki"):
            your_query = message.text[6:]
        elif (s == "/wiki@algebrach_bot"):
            your_query = message.text[20:]
        print("{0}\nUser {1} entered this query for /wiki:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_query))
        try:
#по умолчанию ставим поиск в английской версии
            wikipedia.set_lang("en")
#если в запросе имеется хоть один символ не с латинским ASCII, ищем в русской версии
            for s in your_query:
                if ord(s)>127:
                    wikipedia.set_lang("ru")
                    break
#извлекаем первые 7 предложений найденной статьи
            wiki_response = wikipedia.summary(your_query, sentences=7)
#извлекаем ссылку на саму статью
            wiki_url = wikipedia.page(your_query).url
#извлекаем название статьи
            wiki_title = wikipedia.page(your_query).title
            my_bot.reply_to(message, "<b>{0}.</b>\n{1}\n\n{2}".format(wiki_title, wiki_response, wiki_url), parse_mode="HTML")
#всё плохо, ничего не нашли
        except wikipedia.exceptions.PageError:
            my_bot.reply_to(message, "Запрос не найден.")
#нашли несколько статей, предлагаем пользователю список
        except wikipedia.exceptions.DisambiguationError as e:
            wiki_options = e.options
            my_bot.reply_to(message, "Пожалуйста, уточни запрос. Выбери, что из перечисленного имелось в виду, и вызови /wiki ещё раз.\n"+"\n".join(map(str, wiki_options)))
#берём рандомную статью на рандомном языке (перечисляем языки в data.py)
    else:
        wikipedia.set_lang(random.choice(data.wiki_langs))
        try:
            wikp = wikipedia.random(pages=1)
            wikpd = wikipedia.page(wikp)
            wikiFact = wikipedia.summary(wikp, sentences=3)
            my_bot.reply_to(message, "<b>{0}.</b>\n{1}".format(wikpd.title, wikiFact), parse_mode="HTML")
        except wikipedia.exceptions.DisambiguationError:
            wikp = wikipedia.random(pages=1)
            wikiVar = wikipedia.search(wikp, results=1)
            print("There are multiple possible pages for that article.\n")
            wikpd = wikipedia.page(str(wikiVar[0]))
            wikiFact = wikipedia.summary(wikiVar, sentences=4)
            my_bot.reply_to(message, "<b>{0}.</b>\n{1}".format(wikp, wikiFact), parse_mode="HTML")
        print("{0}\nUser {1} got Wikipedia article\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, str(wikp)))

#команда /meme (выпиливаем?)
@my_bot.message_handler(commands=['meme'])
#открывает соответствующую папку и кидает из не рандомную картинку или гифку
def myMemes(message):
    all_imgs = os.listdir(data.dir_location_meme)
    rand_file = random.choice(all_imgs)
    your_file = open(data.dir_location_meme+rand_file, "rb")
    if rand_file.endswith(".gif"):
        my_bot.send_document(message.chat.id, your_file, reply_to_message_id=message.message_id)
    else:
        my_bot.send_photo(message.chat.id, your_file, reply_to_message_id=message.message_id)
    print("{0}\nUser {1} got that meme:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
    your_file.close()

#команда /kek
@my_bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['/kek', '/kek@algebrach_bot'])
#открывает соответствующие файл и папку, кидает рандомную строчку из файла, или рандомную картинку или гифку из папки
def myKek(message):
    global weather_bold
    global kek_counter
    global kek_bang
    global kek_crunch
    kek_init = True

    if (kek_counter == 0):
        kek_bang = time.time()
        kek_crunch = kek_bang + 60*60
        kek_counter += 1
        kek_init = True
    elif (kek_counter >= data.limit_kek) and (time.time() <= kek_crunch) :
        kek_init = False
    elif (time.time() > kek_crunch) :
        kek_counter = -1
        kek_init = True
    print("KEK BANG : {0}\nKEK CRUNCH : {1}\nKEK COUNT : {2}\nTIME NOW : {3}".format(kek_bang, kek_crunch, kek_counter, time.time()))

    if kek_init :
        kek_counter += 1
        your_destiny = random.randint(1,60)
#если при вызове не повезло, то кикаем из чата
        if your_destiny == 13:
            my_bot.reply_to(message, "Предупреждал же, что кикну. Если не предупреждал, то ")
            your_img = open(data.dir_location_meme+"memeSurprise.gif", "rb")
            my_bot.send_document(message.chat.id, your_img, reply_to_message_id=message.message_id)
            your_img.close()
            try:
                if (int(message.from_user.id) in data.admin_ids):
                    my_bot.reply_to(message, "...Но против хозяев не восстану.")
                    print("{0}\nUser {1} can't be kicked out.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
                else:
#кикаем кекуна из чата (можно ещё добавить условие, что если один юзер прокекал больше числа n за время t, то тоже в бан)
                    my_bot.kick_chat_member(message.chat.id, message.from_user.id)
                    print("{0}\nUser {1} has been kicked out.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
                    my_bot.unban_chat_member(message.chat.id, message.from_iser.id)
#тут же снимаем бан, чтобы смог по ссылке к нам вернуться
                    print("{0}\nUser {1} has been unbanned.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            except Exception as e:
                logging.exception(e)
                pass
        else:
            type_of_KEK = random.randint(1,33)
#1/33 шанс на картинку или гифку
            if (type_of_KEK == 9):
                all_imgs = os.listdir(data.dir_location_kek)
                rand_file = random.choice(all_imgs)
                your_file = open(data.dir_location_kek+rand_file, "rb")
                if rand_file.endswith(".gif"):
                    my_bot.send_document(message.chat.id, your_file, reply_to_message_id=message.message_id)
                else:
                    my_bot.send_photo(message.chat.id, your_file, reply_to_message_id=message.message_id)
                your_file.close()
                print("{0}\nUser {1} got that kek:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
#иначе смотрим файл
            else:
                file_KEK = open(data.file_location_kek, 'r')
                your_KEK = random.choice(file_KEK.readlines())
                if (str(your_KEK) == str("Чекни /weather.\n")):
                    weather_bold = True
                else:
                    weather_bold = False
#если попалась строчка вида '<sticker>ID', то шлём стикер по ID
                if (str(your_KEK).startswith("<sticker>")):
                    if (not str(your_KEK).endswith("\n")):
                        sticker_id = str(your_KEK[9:])
                    else:
                        sticker_id = str(your_KEK[9:-1])
                    my_bot.send_sticker(message.chat.id, sticker_id, reply_to_message_id=message.message_id)
#иначе просто шлём обычный текст
                else:
                    my_bot.reply_to(message, str(your_KEK).replace("<br>", "\n"))
                file_KEK.close()
                print("{0}\nUser {1} got that kek:\n{2}".format(time.strftime(data.time, time.gmtime()), message.from_user.id, str(your_KEK).replace("<br>", "\n")))
    else :
        print("{0}\nLimit of keks has been expired.\nWait until {1} to kek again.\n".format(time.strftime(data.time, time.gmtime()), kek_crunch))


#для читерства

@my_bot.message_handler(commands=['prize'])
def showPrizes(message):
    if not len(message.text.split()) == 1 and int(message.from_user.id in data.admin_ids):
        s = message.text.split()[1]
        if (s == data.my_prize):
            all_imgs = os.listdir(data.dir_location_prize)
            rand_file = random.choice(all_imgs)
            your_file = open(data.dir_location_prize+rand_file, "rb")
            if rand_file.endswith(".gif"):
                my_bot.send_document(message.chat.id, your_file, reply_to_message_id=message.message_id)
            else:
                my_bot.send_photo(message.chat.id, your_file, reply_to_message_id=message.message_id)
            print("{0}\nUser {1} knows the secret and got that prize:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
            your_file.close()
    elif (not int(message.from_user.id in data.admin_ids)):
        print("{0}\nUser {1} tried to access the prizes, but he's not in Admin list.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))

@my_bot.message_handler(commands=['kill'])
def killBot(message):
    if not len(message.text.split()) == 1 and int(message.from_user.id in data.admin_ids):
        s = message.text.split()[1]
        if (s == data.my_killswitch):
            my_bot.reply_to(message, "Прощай, жестокий чат. ;~;")
#создаём отдельный алёрт для .sh скрипта -- перезапустим бот сами
            try:
                file_killed_write = open(data.bot_killed_filename, 'w')
                file_killed_write.close()
                print("{0}\nBot has been killed off remotely by user {1}.\nPlease, change the killswitch keyword in data.py before running the bot again.".format(time.strftime(data.time, time.gmtime()), message.from_user.first_name))
                sys.exit()
            except RuntimeError:
                sys.exit()
    elif (not int(message.from_user.id in data.admin_ids)):
        print("{0}\nUser {1} tried to kill the bot. Fortunately, he's not in Admin list.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))


#проверяет наличие новых постов ВК в паблике Мехмата и кидает их при наличии
def vkListener(interval):
    while True:
        try:
#коннектимся к API через requests. Берём первые два поста
            response = requests.get('https://api.vk.com/method/wall.get', params={'access_token': tokens.vk, 'owner_id': data.vkgroup_id, 'count': 2, 'offset': 0})
#создаём json-объект для работы
            posts = response.json()['response']
#инициализируем строку, чтобы он весь текст кидал одним сообщением
            vk_final_post = ''
            vk_initiate = False
            show_preview = False
#пытаемся открыть файл с датой последнего поста
            try:
                file_lastdate_read = open(data.vk_update_filename, 'r')
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
#смотрим, запиннен ли первый пост
            is_post_pinned = posts[-2]['is_pinned']
#если да, то смотрим, что свежее -- запинненный пост или следующий за ним
            if (is_post_pinned == 1):
                date_pinned = int(posts[-2]['date'])
                date_notpinned = int(posts[-1]['date'])
                if (date_pinned >= date_notpinned):
                    post = posts[-2]
                else :
                    post = posts[-1]
                post_date = max(date_pinned, date_notpinned)
#если нет, то берём первый пост
            else :
                post = posts[-2]
                post_date = int(posts[-2]['date'])
#наконец, сверяем дату свежего поста с датой, сохранённой в файле
            if (post_date > int(last_recorded_postdate)):
                vk_initiate = True
            else :
                vk_initiate = False
#если в итоге полученный пост -- новый, то начинаем операцию
            if (vk_initiate):
                post_recent_date = post_date
                print("{0}\nWe have new post in Mechmath's VK public.\n".format(time.strftime(data.time, time.gmtime())))
#если это репост, то сначала берём сообщение самого мехматовского поста
                if ('copy_text' in post) or ('copy_owner_id' in post):
                    if ('copy_text' in post):
                        post_text = post['copy_text']
                        vk_final_post += post_text.replace("<br>", "\n")
#пробуем сформулировать откуда репост
                    if ('copy_owner_id' in post):
                        original_poster_id = post['copy_owner_id']
#если значение ключа 'copy_owner_id' отрицательное, то перед нами репост из группы
                        if int(original_poster_id) < 0:
                            response_OP = requests.get('https://api.vk.com/method/groups.getById', params={'group_ids': -(int(original_poster_id))})
                            name_OP = response_OP.json()['response'][0]['name']
                            screenname_OP = response_OP.json()['response'][0]['screen_name']
#добавляем строку, что это репост из такой-то группы
                            vk_final_post += "\n\nРепост из группы <a href=\"https://vk.com/{0}\">{1}</a>:\n".format(screenname_OP, name_OP)
#если значение ключа 'copy_owner_id' положительное, то репост пользователя
                        else:
                            response_OP = requests.get('https://api.vk.com/method/users.get', params={'access_token': tokens.vk, 'user_id': int(original_poster_id)})
                            name_OP = "{0} {1}".format(response_OP.json()['response'][0]['first_name'], response_OP.json()['response'][0]['last_name'],)
                            screenname_OP = response_OP.json()['response'][0]['uid']
#добавляем строку, что это репост такого-то пользователя
                            vk_final_post += "\n\nРепост от пользователя <a href=\"https://vk.com/id{0}\">{1}</a>:\n".format(screenname_OP, name_OP)
                    else:
                        print("What.")
                try:
#добавляем сам текст репоста
                    post_text = post['text']
                    vk_final_post += post_text.replace("<br>", "\n")
                    vk_final_post += "\n"
                except KeyError:
                    pass
#смотрим на наличие ссылок, если есть -- добавляем
                try:
                    for i in range(0, len(post['attachments'])):
                        if ('link' in post['attachments'][i]):
                            post_link = post['attachments'][i]['link']['url']
                            vk_final_post += post_link
                            vk_final_post += "\n"
                            print("Successfully extracted link URL:\n{0}\n".format(post_link))
                except KeyError:
                    pass
#если есть вики-ссылки на профили пользователей ВК вида '[screenname|real name]', то превращаем ссылки в кликабельные
                try:
                    pattern = re.compile(r"\[([^\|]+)\|([^\|]+)\]", re.U)
                    results = pattern.findall(vk_final_post.decode('utf-8'), re.U)
                    for i in range(0, len(results)):
                        screen_name_user = results[i][0].encode('utf-8')
                        real_name_user = results[i][1].encode('utf-8')
                        link = "<a href=\"https://vk.com/{0}\">{1}</a>".format(screen_name_user, real_name_user)
                        unedited = "[{0}|{1}]".format(screen_name_user, real_name_user)
                        vk_final_post = vk_final_post.replace(unedited, link)
                except Exception as e:
                    logging.exception(e)
#смотрим на наличие картинок
                try:
                    img_src = []
                    for i in range(0, len(post['attachments'])):
#если есть, то смотрим на доступные размеры. Для каждой картинки пытаемся выудить ссылку на самое большое расширение, какое доступно
                        if ('photo' in post['attachments'][i]):
                            we_got_src = False
                            if ('src_xxbig' in post['attachments'][i]['photo']):
                                post_attach_src = post['attachments'][i]['photo']['src_xxbig']
                                we_got_src = True
                                request_img = requests.get(post_attach_src)
                                img_vkpost = io.BytesIO(request_img.content)
                                img_src.append(img_vkpost)
                                print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            elif ('src_xbig' in post['attachments'][i]['photo']) and (not we_got_src):
                                post_attach_src = post['attachments'][i]['photo']['src_big']
                                we_got_src = True
                                request_img = requests.get(post_attach_src)
                                img_vkpost = io.BytesIO(request_img.content)
                                img_src.append(img_vkpost)
                                print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            elif ('src_big' in post['attachments'][i]['photo']) and (not we_got_src):
                                post_attach_src = post['attachments'][i]['photo']['src_big']
                                we_got_src = True
                                request_img = requests.get(post_attach_src)
                                img_vkpost = io.BytesIO(request_img.content)
                                img_src.append(img_vkpost)
                                print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            elif not we_got_src:
                                post_attach_src = post['attachments'][i]['photo']['src']
                                we_got_src = True
                                request_img = requests.get(post_attach_src)
                                img_vkpost = io.BytesIO(request_img.content)
                                img_src.append(img_vkpost)
                                print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            else:
                                print("Couldn't extract photo URL from a VK post.\n")
                except KeyError:
                    pass
#отправляем нашу строчку текста
#если в тексте есть ссылка, а по ссылке есть какая-нибудь картинка, то прикрепляем ссылку к сообщению (делаем превью)
                try:
                    if ('image_src' in post['attachment']['link']):
                        show_preview = True
                except KeyError:
                    show_preview = False
                    pass
                if show_preview:
                    my_bot.send_message(data.my_chatID, vk_final_post.replace("<br>", "\n"), parse_mode="HTML")
#если нет -- отправляем без прикреплённой ссылки
                else:
                    my_bot.send_message(data.my_chatID, vk_final_post.replace("<br>", "\n"), parse_mode="HTML", disable_web_page_preview=True)
#отправляем все картинки, какие нашли
                for i in range(0, len(img_src)):
                    my_bot.send_photo(data.my_chatID, img_src[i])
#записываем дату поста в файл, чтобы потом сравнивать новые посты
                file_lastdate_write = open(data.vk_update_filename, 'w')
                file_lastdate_write.write(str(post_recent_date))
                file_lastdate_write.close()
                vk_initiate = False
#5 секунд нужно для инициализации файла
            time.sleep(5)
            time.sleep(interval)
#из-за Telegram API иногда какой-нибудь пакет не доходит
        except ReadTimeout as e:
#            logging.exception(e)
            print("{0}\nRead Timeout in vkListener() function. Because of Telegram API.\nWe are offline. Reconnecting in 5 seconds.\n".format(time.strftime(data.time, time.gmtime())))
            time.sleep(5)
#если пропало соединение, то пытаемся снова через минуту
        except ConnectionError as e:
#            logging.exception(e)
            print("{0}\nConnection Error in vkListener() function.\nWe are offline. Reconnecting in 60 seconds.\n".format(time.strftime(data.time, time.gmtime())))
            time.sleep(60)
#если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
        except RuntimeError as e:
#            logging.exception(e)
            print("{0}\nRuntime Error in vkListener() function.\nRetrying in 3 seconds.\n".format(time.strftime(data.time, time.gmtime())))
            time.sleep(3)
#если что-то неизвестное -- от греха вырубаем с корнем. Создаём алёрт файл для .sh скрипта
        except Exception as e:
            print("{0}\nUnknown Exception in vkListener() function:\n{1}\n{2}\n\nCreating the alert file.\n".format(time.strftime(data.time, time.gmtime()), e.message, e.args))
            file_down_write = open(data.bot_down_filename, 'w')
            file_down_write.close()
            print("{0}\nShutting down.".format(time.strftime(data.time, time.gmtime())))
            os._exit(-1)


while __name__ == '__main__':
    try:
#если бот запущен .sh скриптом после падения -- удаляем алёрт-файл
        try:
            os.remove(data.bot_down_filename)
        except OSError:
            pass
#если бот запущен после вырубания нами -- удаляем алёрт-файл
        try:
            os.remove(data.bot_killed_filename)
        except OSError:
            pass
        interval = data.vk_interval
#задаём новый поток для отслеживания постов в ВК, чтобы можно было одновременно работать с ботом
        t = threading.Thread(target=vkListener, args=(interval,))
        t.daemon = True
        t.start()
        bot_update=my_bot.get_updates()
        my_bot.polling(none_stop=True, interval=1)
        time.sleep(1)
#из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
#        logging.exception(e)
        print("{0}\nRead Timeout. Because of Telegram API.\nWe are offline. Reconnecting in 5 seconds.\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(5)
#если пропало соединение, то пытаемся снова через минуту
    except ConnectionError as e:
#        logging.exception(e)
        print("{0}\nConnection Error.\nWe are offline. Reconnecting in 60 seconds.\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(60)
#если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
#        logging.exception(e)
        print("{0}\nRuntime Error.\nRetrying in 3 seconds.\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(3)
#кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
#        logging.exception(e)
        print("{0}\nUnicode Encode Error. Someone typed in cyrillic.\nRetrying in 3 seconds.\n".format(time.strftime(data.time, time.gmtime())))
        time.sleep(3)
#завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
#        logging.exception(e)
        print("\n{0}\nKeyboard Interrupt. Good bye.\n".format(time.strftime(data.time, time.gmtime())))
        sys.exit()
#если что-то неизвестное -- от греха вырубаем с корнем. Создаём алёрт файл для .sh скрипта
    except Exception as e:
        print("{0}\nUnknown Exception:\n{1}\n{2}\n\nCreating the alert file.\n".format(time.strftime(data.time, time.gmtime()), e.message, e.args))
        file_down_write = open(data.bot_down_filename, 'w')
        file_down_write.close()
        print("{0}\nShutting down.".format(time.strftime(data.time, time.gmtime())))
        os._exit(-1)

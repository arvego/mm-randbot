#!/usr/bin/env python
#_*_ coding: utf-8 _*_
import io
import logging
import os
import random
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

global user_registr
global user_id
global user_correct_num
global user_status
global user_max
user_registr={}

global weather_bold
weather_bold = False

reload(sys)
sys.setdefaultencoding('utf-8')


#команда /start, /help, /links и /wifi
@my_bot.message_handler(commands=['start', 'help', 'links', 'wifi'])
#открывает локальный файл и посылает пользователю содержимое
def myData(message):
    for s in str(message.text).split():
        if s == "/start":
            required_file = open(data.file_location_start, 'r')
            print("{0}\nUser {1} started using the bot.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            break
        elif s == "/help":
            required_file = open(data.file_location_help, 'r')
            print("{0}\nUser {1} looked for help.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            break
        elif s == "/links":
            required_file = open(data.file_location_links, 'r')
            print("{0}\nUser {1} requested Mechmath links.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
        elif s == "/wifi":
            required_file = open(data.file_location_wifi, 'r')
            print("{0}\nUser {1} requested the Wi-Fi list.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    required_data = required_file.read()
    my_bot.reply_to(message, str(required_data), parse_mode="HTML", disable_web_page_preview=True)
    required_file.close()

#команды /task и /maths
@my_bot.message_handler(commands=['task', 'maths'])
#идёт в соответствующую папку и посылает рандомную картинку
def myRandImg(message):
    for s in str(message.text).split():
        if s == "/task":
            path = data.dir_location_challenge
            print("{0}\nUser {1} asked for a challenge.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            break
        elif s == "/maths":
            path = data.dir_location_maths
            print("{0}\nUser {1} asked for maths.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            break
    all_imgs = os.listdir(path)
    rand_img = random.choice(all_imgs)
    your_img = open(path+rand_img, "rb")
    my_bot.send_photo(message.from_user.id, your_img, reply_to_message_id=message.message_id)
    print("{0}\nUser {1} got that image:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_img.name))
    your_img.close()

#команда /d6
@my_bot.message_handler(commands=['d6'])
#рандомно выбирает элементы из списка значков
###желательно найти способ их увеличить или заменить на ASCII арт
def myD6(message):
    d6 = data.d6_symbols
    roll1 = random.choice(d6)
    roll2 = random.choice(d6)
    my_bot.reply_to(message, "{0}  {1}".format(roll1, roll2))
    print("{0}\nUser {1} got that D6 output: {2}  {3}.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, roll1, roll2))

#команда /number
@my_bot.message_handler(commands=['number'])
def guessNumber(message):
    global user_registr
    global user_id
    global user_correct_num
    global user_status
    global user_max
    user_id=str(message.from_user.id)
    your_num = -1
    is_max_zero = False
    is_num = True
    your_int = []
#пользователь в первый раз заходит в команду, генерируем плейсхолер в словаре
    if not user_id in user_registr:
        user_max = -3
        user_correct_num = -2
        user_status = -1
        user_registr[user_id] = {'maxNum': user_max, 'corrNum': user_correct_num, 'gameStatus': user_status}
        print("{0}\nUser {1} started /number game.\nDefault profile on the Registry has been created.\n".format(time.strftime(data.time, time.gmtime()), user_id))
        i = 0
        for s in str(message.text).split():
            i = i+1
#алёрт, если пользователь ввёл команду без параметра. Объясняем как надо и удаляем из словаря
        if i == 1:
            my_bot.reply_to(message, "Я не понял запрос.\nПожалуйста, вводи команду в виде \'/number [int]\'.")
            print("{0}\nUser {1} entered /number without int.\nUser {1} has been removed from the Registry.\n".format(time.strftime(data.time, time.gmtime()), user_id))
            del user_registr[user_id]
        else:
            for s in str(message.text).split():
                if (not s == "/number") and s.isdigit():
                    user_max = int(s)
                elif (not s == "/number") and (not s.isdigit()):
#если пользователю взбредёт в голову ввести отрицательное число в качестве max
                    if not s[0] == "-":
                        is_num = False
                        break
                    else:
                        for i in range(1, len(s)):
                            your_int.append(s[i])
                    try:
                        user_max = int(''.join(your_int))
#если всё плохо, берём максимальное число, заданное в data.py
                    except ValueError:
                        my_bot.reply_to(message, "Я не понял число.\nБеру стандартное максимальное целое.")
                        user_max = data.guessnum_maxnum
                        break
                elif (not s == "/number"):
                    my_bot.reply_to(message, "Я не понял число.\nБеру стандартное максимальное целое.")
                    user_max = data.guessnum_maxnum
            if not is_num:
                my_bot.reply_to(message, "Я не понял число.\nБеру стандартное максимальное целое.")
                user_max = data.guessnum_maxnum
#если пользователь хочет от 0 до 0, то нет
            elif user_max == 0:
                is_max_zero = True
                my_bot.reply_to(message, "Это скучно, ты же знаешь, что я смог загадать только 0.\nВызови /number ещё раз и дай мне любое другое целое для максимума.")
                del user_registr[user_id]
                print("{0}\nUser {1} entered '/number 0'.\nUser {1} has been removed from the Registry.\n".format(time.strftime(data.time, time.gmtime()), user_id))
#после получения числа создаём индивидуальный профиль на каждого пользователя и добавляем в словарь
        if user_id in user_registr:
            user_correct_num = random.randint(0, abs(user_max))
            user_status = data.guessnum_attempts
            user_registr[user_id] = {'maxNum': abs(user_max), 'corrNum': user_correct_num, 'gameStatus': user_status}
            my_bot.reply_to(message, "Окей, я загадал рандомное целое число от 0 до {0}.\nНапиши свою догадку в виде \'/number <число>\'.\nУ тебя есть {1} попыток.".format(abs(user_max), user_registr[user_id]['gameStatus']))
            print("{0}\nProfile in the Registry for user {1} has been updated:\n{2}\n".format(time.strftime(data.time, time.gmtime()), user_id, user_registr[user_id]))
    else:
#пользователь уже в игре
        i = 0
        for s in str(message.text).split():
            i = i+1
        if i == 1:
#выуживание числа
            is_num = False
            my_bot.reply_to(message, "Я не понял число.\nПожалуйста, вводи команду в виде \'/number [positive int]\'.\nКоличество попыток не изменилось.")
        else:
            for s in str(message.text).split():
                if (not s == "/number") and s.isdigit():
                    your_num = int(s)
                    is_num = True
                elif (not s == "/number"):
                    is_num = False
                    my_bot.reply_to(message, "Я не понял число.\nПожалуйста, вводи команду в виде \'/number [positive int]\'.\nКоличество попыток не изменилось.")
                    print("{0}\nUser {1} entered /number without a positive int.\nUser {1} has another chance.\n".format(time.strftime(data.time, time.gmtime()), user_id))
                    break
        if is_num:
#выудили, теперь сверяем с заданным в профиле из словаря пока попытки не кончатся
            if (data.guessnum_attempts>= user_registr[user_id]['gameStatus']>1):
                if your_num>user_registr[user_id]['corrNum']:
#если больше, и осталась одна попытка
                    if user_registr[user_id]['gameStatus'] == 2:
                        user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
                        my_bot.reply_to(message, "Твоё число оказалось больше загаданного.\nОсталась всего лишь {0} попытка.".format(user_registr[user_id]['gameStatus']))
#если больше
                    else:
                        user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
                        my_bot.reply_to(message, "Твоё число оказалось больше загаданного.\nОсталось {0} попытки.".format(user_registr[user_id]['gameStatus']))
                    print("{0}\nUser {1} guessed that number: {2}.\nThe correct number is {3}.\nUser {1} has got {4} attempts left.\n".format(time.strftime(data.time, time.gmtime()), user_id, your_num, user_registr[user_id]['corrNum'], user_registr[user_id]['gameStatus']))
                elif your_num<user_registr[user_id]['corrNum']:
#если меньше, и осталась одна попытка
                    if user_registr[user_id]['gameStatus'] == 2:
                        user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
                        my_bot.reply_to(message, "Твоё число оказалось меньше загаданного.\nОсталась всего лишь {0} попытка.".format(user_registr[user_id]['gameStatus']))
#если меньше
                    else:
                        user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
                        my_bot.reply_to(message, "Твоё число оказалось меньше загаданного.\nОсталось {0} попытки.".format(user_registr[user_id]['gameStatus']))
                    print("{0}\nUser {1} guessed that number: {2}.\nThe correct number is {3}.\nUser {1} has got {4} attempts left.\n".format(time.strftime(data.time, time.gmtime()), user_id, your_num, user_registr[user_id]['corrNum'], user_registr[user_id]['gameStatus']))
#если число угадано
                else:
                    user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
#если с первой попытки
                    if (user_registr[user_id]['gameStatus'] == data.guessnum_attempts-1):
                        my_bot.reply_to(message, "Красава! Прям сразу угадал. Как?!")
#если ещё и max>=100, то посылаем приз
                        if user_registr[user_id]['maxNum']>=100:
                            all_imgs = os.listdir(data.dir_location_prize)
                            rand_file = random.choice(all_imgs)
                            your_file = open(data.dir_location_prize+rand_file, "rb")
                            if rand_file.endswith(".gif"):
                                my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
                            else:
                                my_bot.send_photo(message.from_user.id, your_file, reply_to_message_id=message.message_id)
                            your_file.close()
#если не с первой и не с последней попытки
                    else:
                        my_bot.reply_to(message, "Поздравляю! Ты угадал моё загаданное число за {0} попытки.".format(data.guessnum_attempts-user_registr[user_id]['gameStatus']))
                        if user_registr[user_id]['maxNum']>=100:
                            all_imgs = os.listdir(data.dir_location_prize)
                            rand_file = random.choice(all_imgs)
                            your_file = open(data.dir_location_prize+rand_file, "rb")
                            if rand_file.endswith(".gif"):
                                my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
                            else:
                                my_bot.send_photo(message.from_user.id, your_file, reply_to_message_id=message.message_id)
                            your_file.close()
#ведётся лог. если пользователь выиграл, то его профиль удаляется из словаря
                    print("{0}\nUser {1} guessed that number: {2}.\nThe correct number is {3}.\nUser {1} has got {4} attempts left.\n".format(time.strftime(data.time, time.gmtime()), user_id, your_num, user_registr[user_id]['corrNum'], user_registr[user_id]['gameStatus']))
                    del user_registr[user_id]
                    print("{0}\nUser {1} has won the /number game.\nUser {1} has been removed from the Registry.\n".format(time.strftime(data.time, time.gmtime()), user_id))
#идёт последняя попытка
            elif user_registr[user_id]['gameStatus'] == 1:
                user_registr[user_id]['gameStatus'] = user_registr[user_id]['gameStatus']-1
#если число угадано
                if your_num == user_registr[user_id]['corrNum']:
#если число угадано, и max>=100
                    if user_registr[user_id]['maxNum']>=100:
                        my_bot.reply_to(message, "Хорош. Впритык успел отгадать моё число за {0} попыток.\nДля получения приза попробуй всё же отгадать не впритык. :) Удачи.".format(data.guessnum_attempts-user_registr[user_id]['gameStatus']))
#если max<100
                    else:
                        my_bot.reply_to(message, "Хорош. Впритык успел отгадать моё число за {0} попыток.".format(data.guessnum_attempts-user_registr[user_id]['gameStatus']))
#если пользователь не угадал за все попытки. Вылетает из словаря.
                else:
                    my_bot.reply_to(message, "Прости, ты не отгадал. Я загадал число {0}.\nДля новой игры введи команду \'/number <желаемое максимальное рандомное число>\'.".format(user_registr[user_id]['corrNum']))
                print("{0}\nUser {1} guessed that number: {2}.\nThe correct number is {3}.\n".format(time.strftime(data.time, time.gmtime()), user_id, your_num, user_registr[user_id]['corrNum']))
                del user_registr[user_id]
                print("{0}\nUser {1} has finised the /number game.\nUser {1} has been removed from the Registry.\n".format(time.strftime(data.time, time.gmtime()), user_id))

#команда /roll
@my_bot.message_handler(commands=['roll'])
#генерует случайное целое число, в засимости от него может кинуть картинку или гифку
def myRoll(message):
    your_destiny = random.randint(0,100)
    if your_destiny == 0:
        path_dir = data.my_core_dir
        your_img = open(path_dir+"00.jpg", "rb")
        my_bot.send_photo(message.from_user.id, your_img, reply_to_message_id=message.message_id)
        your_img.close()
        print("{0}\nUser {1} got ZERO.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif your_destiny == 13:
        my_bot.reply_to(message, "Прощай, зайчик!")
        your_img = open(data.dir_location_meme+"memeProblem.png", "rb")
        my_bot.send_photo(message.from_user.id, your_img, reply_to_message_id=message.message_id)
        your_img.close()
        my_bot.kick_chat_member(message.chat.id, message.from_user.id)
#кикаем неудачника из чата
        print("{0}\nUser {1} has been kicked out.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
        my_bot.unban_chat_member(message.chat.id, message.from_iser.id)
#тут же снимаем бан, чтобы он смог по ссылке к нам вернуться
        print("{0}\nUser {1} has been unbanned.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif your_destiny == 42:
        your_img = open(data.my_core_dir+"42.jpg", "rb")
        my_bot.send_photo(message.from_user.id, your_img, reply_to_message_id=message.message_id)
        your_img.close()
        print("{0}\nUser {1} recieved 42.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif your_destiny == 69:
        your_file = open(data.my_core_dir+"69HEYOO.gif", "rb")
        my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
        your_file.close()
        print("{0}\nUser {1} recieved 69. Lucky guy.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif your_destiny == 89:
        your_file = open(data.my_core_dir+"89RickRolled.gif", "rb")
        my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
        your_file.close()
        print("{0}\nUser {1} got RICK ROLL'D.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    elif your_destiny == 100:
        your_file = open(data.my_core_dir+"100KeepRollin.gif", "rb")
        my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
        your_file.close()
        print("{0}\nUser {1} should keep on rollin'.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    else:
        my_bot.reply_to(message, str(your_destiny))
        print("{0}\nUser {1} recieved {2}.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_destiny))

#команда /truth
@my_bot.message_handler(commands=['truth'])
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

#команда /wolfram
@my_bot.message_handler(commands=['wolfram'])
def wolframSolver(message):
#обрабатывает запрос и посылает пользователю картинку с результатом в случае удачи
    wolfram_query = []
#сканируем и передаём всё, что ввёл пользователь после '/wolfram '
    if not len(message.text.split()) == 1:
        your_query = message.text[9:]
        print("{0}\nUser {1} entered this query for \'/wolfram\':\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_query))
        response = requests.get("https://api.wolframalpha.com/v1/simple?appid="+tokens.wolfram, params={'i': your_query})
#если всё хорошо, и запрос найден
        if response.status_code == 200:
            img_wolfram = io.BytesIO(response.content)
            my_bot.send_photo(message.from_user.id, img_wolfram, reply_to_message_id=message.message_id)
            print("{0}\nUser {1} has received this Wolfram output:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, response.url))
#если всё плохо
        else:
            my_bot.reply_to(message, "Запрос не найдён.\nЕсли ты ввёл его на русском, то попробуй ввести его на английском.")
            print("{0}\nUser {1} didn't received any data.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
#если пользователь вызвал /wolfram без аргумента
    else:
        my_bot.reply_to(message, "Я не понял запрос.\nДля вызова Wolfram вводи команду в виде \'/wolfram <запрос>\'.")
        print("{0}\nUser {1} called /wolfram without any arguments.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))

#команда /weather
@my_bot.message_handler(commands=['weather'])
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
        my_bot.send_message(message.from_user.id, data.weather_HAARP, parse_mode="HTML")
        weather_bold = False
        print("{0}\nUser {1} got HAARP'd.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
#если всё нормально, то выводим результаты
    else:
        my_bot.reply_to(message, "The current temperature in Moscow is {2} C, and it is {3}.\n\nTomorrow it will be {4} C, {5}.\nIn 2 days it will be {6}, {7}.\nIn 3 days it will be {8} C, {9}.\n\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, temp_now['temp'], status, my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2], my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3]))
        print("{0}\nUser {1} got that weather forecast:\nThe current temperature in Moscow is {2} C, and it is {3}.\nTomorrow it will be {4} C, {5}.\nIn 2 days it will be {6}, {7}.\nIn 3 days it will be {8} C, {9}.\n\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, temp_now['temp'], status, my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2], my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3]))

#команда /wiki
@my_bot.message_handler(commands=['wiki'])
#обрабатывает запрос и пересылает результат, или выдаёт рандомный факт в случае отсутствия запроса
def myWiki(message):
    wiki_query = []
#обрабатываем всё, что пользователь ввёл после '/wiki '
    if not len(message.text.split()) == 1:
        your_query = message.text[6:]
        print("{0}\nUser {1} entered this query for \'/wiki\':\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_query))
        try:
#ищем только на русском (сразу на нескольких языках модуль нам не позволяет)
            wikipedia.set_lang("ru")
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
            my_bot.reply_to(message, "Пожалуйста, уточни запрос. Что из перечисленного имелось в виду?\n"+"\n".join(map(str, wiki_options)))
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

#команда /meme
@my_bot.message_handler(commands=['meme'])
#открывает соответствующую папку и кидает из не рандомную картинку или гифку
def myMemes(message):
    all_imgs = os.listdir(data.dir_location_meme)
    rand_file = random.choice(all_imgs)
    your_file = open(data.dir_location_meme+rand_file, "rb")
    if rand_file.endswith(".gif"):
        my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
    else:
        my_bot.send_photo(message.from_user.id, your_file, reply_to_message_id=message.message_id)
    print("{0}\nUser {1} got that meme:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
    your_file.close()

#команда /kek
@my_bot.message_handler(commands=['kek'])
#открывает соответствующие файл и папку, кидает рандомную строчку из файла, или рандомную картинку или гифку из папки
def myKek(message):
    global weather_bold
    your_destiny = random.randint(1,60)
#если при вызове не повезло, то кикаем из чата
    if your_destiny == 13:
        my_bot.reply_to(message, "Предупреждал же, что кикну. Если не предупреждал, то ")
        your_img = open(data.dir_location_meme+"memeSurprise.gif", "rb")
        my_bot.send_document(message.from_user.id, your_img, reply_to_message_id=message.message_id)
        your_img.close()
        my_bot.kick_chat_member(message.chat.id, message.from_user.id)
        print("{0}\nUser {1} has been kicked out.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
        my_bot.unban_chat_member(message.chat.id, message.from_iser.id)
#тут же снимаем бан, чтобы смог по ссылке к нам вернуться
        print("{0}\nUser {1} has been unbanned.\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
    else:
        type_of_KEK = random.randint(1,10)
#1/10 шанс на картинку или гифку
        if (type_of_KEK == 9):
            all_imgs = os.listdir(data.dir_location_kek)
            rand_file = random.choice(all_imgs)
            your_file = open(data.dir_location_kek+rand_file, "rb")
            if rand_file.endswith(".gif"):
                my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
            else:
                my_bot.send_photo(message.from_user.id, your_file, reply_to_message_id=message.message_id)
            your_file.close()
            print("{0}\nUser {1} got that kek:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
#иначе просто шлём обычный текст из файла
        else:
            file_KEK = open(data.file_location_kek, 'r')
            your_KEK = random.choice(file_KEK.readlines())
            if (str(your_KEK) == str("Чекни /weather.\n")):
                weather_bold = True
            my_bot.reply_to(message, str(your_KEK).replace("<br>", "\n"))
            file_KEK.close()
            print("{0}\nUser {1} got that kek:\n{2}".format(time.strftime(data.time, time.gmtime()), message.from_user.id, str(your_KEK).replace("<br>", "\n")))

#для читерства
@my_bot.message_handler(content_types={'text'})
def defaultHandler(message):
    your_msg = str(message.text)
#просмотр файла из папки с призами
    if your_msg == "Anime":
        all_imgs = os.listdir(data.dir_location_prize)
        rand_file = random.choice(all_imgs)
        your_file = open(data.dir_location_prize+rand_file, "rb")
        if rand_file.endswith(".gif"):
            my_bot.send_document(message.from_user.id, your_file, reply_to_message_id=message.message_id)
        else:
            my_bot.send_photo(message.from_user.id, your_file, reply_to_message_id=message.message_id)
        print("{0}\nUser {1} knows the secret and got that prize:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, your_file.name))
        your_file.close()
#если надо вырубить бот из чата
##КАЖДЫЙ РАЗ МЕНЯЙ КОДОВОЕ СЛОВО!
    elif your_msg == data.my_killswitch:
        my_bot.reply_to(message, "Прощай, жестокий чат. ;~;")
        try:
            print("{0}\nBot has been killed off remotely by user {1}.\nPlease, change the killswitch keyword in data.py before running the bot again.".format(time.strftime(data.time, time.gmtime()), message.from_user.id))
            sys.exit()
        except RuntimeError:
            sys.exit()
    else:
        my_bot.reply_to(message, "Не понял запрос.\nДля просмотра списка доступных команд вызови /help.")
        print("{0}\nUser {1} typed something I could not understand:\n{2}\n".format(time.strftime(data.time, time.gmtime()), message.from_user.id, message.text))


#проверяет наличие новых постов ВК в паблике Мехмата и кидает их при наличии 
def vkListener(interval):
    while True:
        try:
#коннектимся к API через requests
            response = requests.get('https://api.vk.com/method/wall.get', params={'access_token': tokens.vk, 'owner_id': data.vkgroup_id, 'count': 1, 'offset': 0})
#создаём json-объект для работы
            post = response.json()['response']
#инициализируем строку, чтобы он весь текст кидал одним сообщением
            vk_final_post = ''
            is_post_pinned = post[-1]['is_pinned']
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
#если первый пост, который мы получили, запиннен
            if (is_post_pinned == 1):
#смотрим на его дату
                pinned_date = post[-1]['date']
#переходим к следующему посту
                response_next = requests.get('https://api.vk.com/method/wall.get', params={'access_token': tokens.vk, 'owner_id': data.vkgroup_id, 'count': 1, 'offset': 1})
                post_next = response_next.json()['response']
                post_date = post_next[-1]['date']
#сравниваем даты двух постов. Если второй пост свежее запинненного и его дата свежее сохранённой, то начинаем извлекать из второго поста данные
                if (int(post_date) >= int(pinned_date)) and (int(post_date) > int(last_recorded_postdate)):
                    post_recent_date = post_date
                    print("{0}\nWe have new post in Mechmath's VK public.\n".format(time.strftime(data.time, time.gmtime())))
#если это репост, то сначала берём сообщение самого мехматовского поста
                    if ('copy_text' in post_next[-1]) or ('copy_owner_id' in post_next[-1]):
                        if ('copy_text' in post_next[-1]):
                            post_text = post_next[-1]['copy_text']
                            vk_final_post += post_text.replace("<br>", "\n")
#пробуем сформулировать откуда репост
                        if ('copy_owner_id' in post_next[-1]):
                            original_poster_id = post_next[-1]['copy_owner_id']
#abs() потому что в json-объекте у ключа 'copy_owner_id' отрицательное значение из-за особенности API
                            response_OP = requests.get('https://api.vk.com/method/groups.getById', params={'group_ids': abs(int(original_poster_id))})
                            name_OP = response_OP.json()['response'][0]['name']
                            screenname_OP = response_OP.json()['response'][0]['screen_name']
#добавляем строку, что это репост из такой-то группы
                            vk_final_post += "\n\nРепост из группы <a href=\"https://vk.com/{0}\">{1}</a>:\n".format(screenname_OP, name_OP)
                        else:
                            print("What.")
                    try:
#добавляем сам текст репоста
                        post_text = post_next[-1]['text']
                        vk_final_post += post_text.replace("<br>", "\n")
                        vk_final_post += "\n"
                    except KeyError:
                        pass
#смотрим на наличие ссылок, если есть -- добавляем
                    try:
                        for i in range(0, len(post_next[-1]['attachments'])):
                            if ('link' in post_next[-1]['attachments'][i]):
                                post_link = post_next[-1]['attachments'][i]['link']['url']
                                vk_final_post += post_link
                                vk_final_post += "\n"
                                print("Successfully extracted link URL:\n{0}\n".format(post_link))
                    except KeyError:
                        pass
#смотрим на наличие картинок
                    try:
                        img_src = []
                        for i in range(0, len(post_next[-1]['attachments'])):
#если есть, то смотрим на доступные размеры. Для каждой картинки пытаемся выудить ссылку на самое большое расширение, какое доступно
                            if ('photo' in post_next[-1]['attachments'][i]):
                                we_got_src = False
                                if ('src_xxbig' in post_next[-1]['attachments'][i]['photo']):
                                    post_attach_src = post_next[-1]['attachments'][i]['photo']['src_xxbig']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    img_src.append(img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_xbig' in post_next[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post_next[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    img_src.append(img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_big' in post_next[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post_next[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    img_src.append(img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif not we_got_src:
                                    post_attach_src = post_next[-1]['attachments'][i]['photo']['src']
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
                    my_bot.send_message(data.my_chatID, vk_final_post.replace("<br>", "\n"), parse_mode="HTML", disable_web_page_preview=True)
#отправляем все картинки, какие нашли
                    for i in range(0, len(img_src)):
                        my_bot.send_photo(data.my_chatID, img_src[i])
#записываем дату поста в файл, чтобы потом сравнивать новые посты
                    file_lastdate_write = open(data.vk_update_filename, 'w')
                    file_lastdate_write.write(str(post_recent_date))
                    file_lastdate_write.close()
#ВСЁ ТОЧНО ТАК ЖЕ. Разница, что запинненный пост -- самый свежий
                elif (int(pinned_date) > int(last_recorded_postdate)):
                    post_recent_date = pinned_date
                    if ('copy_text' in post[-1]) or ('copy_owner_id' in post[-1]):
                        if ('copy_text' in post[-1]):
                            post_text = post[-1]['copy_text']
                            vk_final_post += post_text.replace("<br>", "\n")
                        if ('copy_owner_id' in post[-1]):
                            original_poster_id = post[-1]['copy_owner_id']
                            response_OP = requests.get('https://api.vk.com/method/groups.getById', params={'group_ids': abs(int(original_poster_id))})
                            name_OP = response_OP.json()['response'][0]['name']
                            screenname_OP = response_OP.json()['response'][0]['screen_name']
                            vk_final_post += "\n\nРепост из группы <a href=\"https://vk.com/{0}\">{1}</a>:\n".format(screenname_OP, name_OP)
                        else:
                            print("What.")
                    try:
                        post_text = post[-1]['text']
                        vk_final_post += post_text.replace("<br>", "\n")
                        vk_final_post += "\n"
                    except KeyError:
                        pass
                    try:
                        for i in range(0, len(post[-1]['attachments'])):
                            if ('link' in post[-1]['attachments'][i]):
                                post_link = post[-1]['attachments'][i]['link']['url']
                                vk_final_post += post_link
                                vk_final_post += "\n"
                                print("Successfully extracted link URL:\n{0}\n".format(post_link))
                    except KeyError:
                        pass
                    try:
                        for i in range(0, len(post[-1]['attachments'])):
                            if ('photo' in post[-1]['attachments'][i]):
                                we_got_src = False
                                if ('src_xxbig' in post[-1]['attachments'][i]['photo']):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_xxbig']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_xbig' in post[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_big' in post[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif not we_got_src:
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            else:
                                print("Couldn't extract photo URL from a VK post.\n")
                    except KeyError:
                        pass
                    my_bot.send_message(data.my_chatID, vk_final_post.replace("<br>", "\n"), parse_mode="HTML", disable_web_page_preview=True)
                    for i in range(0, len(img_src)):
                        my_bot.send_photo(data.my_chatID, img_src[i])
                    file_lastdate_write = open(data.vk_update_filename, 'w')
                    file_lastdate_write.write(str(post_recent_date))
                    file_lastdate_write.close()
#ВСЁ ТОЧНО ТАК ЖЕ. Но с условием, что запинненного поста нет. Тогда просто берём самый первый полученный пост
            else:
                post_date = post[-1]['date']
                if (int(post_date) > int(last_recorded_postdate)):
                    post_recent_date = post_date
                    if ('copy_text' in post[-1]) or ('copy_owner_id' in post[-1]):
                        if ('copy_text' in post[-1]):
                            post_text = post[-1]['copy_text']
                            vk_final_post += post_text.replace("<br>", "\n")
                        if ('copy_owner_id' in post[-1]):
                            original_poster_id = post[-1]['copy_owner_id']
                            response_OP = requests.get('https://api.vk.com/method/groups.getById', params={'group_ids': abs(int(original_poster_id))})
                            name_OP = response_OP.json()['response'][0]['name']
                            screenname_OP = response_OP.json()['response'][0]['screen_name']
                            vk_final_post += "\n\nРепост из группы <a href=\"https://vk.com/{0}\">{1}</a>:\n".format(screenname_OP, name_OP)
                        else:
                            print("What.")
                    try:
                        vk_final_post += post_text.replace("<br>", "\n")
                        vk_final_post += "\n"
                    except KeyError:
                        pass
                    try:
                        for i in range(0, len(post[-1]['attachments'])):
                            if ('link' in post[-1]['attachments'][i]):
                                post_link = post[-1]['attachments'][i]['link']['url']
                                vk_final_post += post_link
                                vk_final_post += "\n"
                                print("Successfully extracted link URL:\n{0}\n".format(post_link))
                    except KeyError:
                        pass
                    try:
                        for i in range(0, len(post[-1]['attachments'])):
                            if ('photo' in post[-1]['attachments'][i]):
                                we_got_src = False
                                if ('src_xxbig' in post[-1]['attachments'][i]['photo']):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_xxbig']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_xbig' in post[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif ('src_big' in post[-1]['attachments'][i]['photo']) and (not we_got_src):
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src_big']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                                elif not we_got_src:
                                    post_attach_src = post[-1]['attachments'][i]['photo']['src']
                                    we_got_src = True
                                    request_img = requests.get(post_attach_src)
                                    img_vkpost = io.BytesIO(request_img.content)
                                    my_bot.send_photo(data.my_chatID, img_vkpost)
                                    print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                            else:
                                print("Couldn't extract photo URL from a VK post.\n")
                    except KeyError:
                        pass
                    my_bot.send_message(data.my_chatID, vk_final_post.replace("<br>", "\n"), parse_mode="HTML", disable_web_page_preview=True)
                    for i in range(0, len(img_src)):
                        my_bot.send_photo(data.my_chatID, img_src[i])
                    file_lastdate_write = open(data.vk_update_filename, 'w')
                    file_lastdate_write.write(str(post_recent_date))
                    file_lastdate_write.close()
#5 секунд нужно для инициализации файла
            time.sleep(5)
            time.sleep(interval)
        except ReadTimeout as e:
    #        logging.exception(e)
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


while __name__ == '__main__':
    try:
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
        exit()

#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import sys
import time

import pyowm

import config
import tokens
from utils import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def my_weather(message):
    '''
    Получает погоду в Москве на сегодня и на три ближайших дня, пересылает пользователю
    :param message:
    :return:
    '''
    try:
        my_owm = pyowm.OWM(tokens.owm)
        # где мы хотим узнать погоду
        my_obs = my_owm.weather_at_place('Moscow')
    except pyowm.exceptions.unauthorized_error.UnauthorizedError:
        print("Your API subscription level does not allow to check weather")
        return
    w = my_obs.get_weather()
    # статус погоды сейчас
    status = w.get_detailed_status()
    # температура сейчас
    temp_now = w.get_temperature('celsius')
    # limit=4, т.к. первый результат — текущая погода
    my_forecast = my_owm.daily_forecast('Moscow,RU', limit=4)
    my_fc = my_forecast.get_forecast()
    # температуры на следующие три дня
    my_fc_temps = []
    # статусы на следующие три дня
    my_fc_statuses = []
    for wth in my_fc:
        my_fc_temps.append(str(wth.get_temperature('celsius')['day']))
        my_fc_statuses.append(str(wth.get_status()))
    # если всё нормально, то выводим результаты
    else:
        forecast = "The current temperature in Moscow is {2} C, " \
                   "and it is {3}.\n\n" \
                   "Tomorrow it will be {4} C, {5}.\n" \
                   "In 2 days it will be {6}, {7}.\n" \
                   "In 3 days it will be {8} C, {9}.\n\n".format(time.strftime(config.time, time.gmtime()),
                                                                 message.from_user.id, temp_now['temp'], status,
                                                                 my_fc_temps[1], my_fc_statuses[1], my_fc_temps[2],
                                                                 my_fc_statuses[2], my_fc_temps[3], my_fc_statuses[3])
        my_bot.reply_to(message, forecast)
        user_action_log(message, "got that weather forecast:\n" + forecast)

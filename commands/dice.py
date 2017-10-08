#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import random
import sys

# модуль с настройками
import data.constants
# shared bot parts
from bot_shared import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def myD6(message):
    '''
    рандомно выбирает элементы из списка значков
    TODO: желательно найти способ их увеличить или заменить на ASCII арт
    :param message:
    :return:
    '''
    d6 = data.constants.d6_symbols
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


# для читерства
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

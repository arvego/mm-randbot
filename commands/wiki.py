#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import random
import sys
from urllib import parse

import wikipedia
from langdetect import detect

from utils import my_bot, user_action_log, action_log


def my_wiki(message):
    """
    Обрабатывает запрос и пересылает результат.
    Если запроса нет, выдаёт рандомный факт.
    :param message:
    :return:
    """
    # обрабатываем всё, что пользователь ввёл после '/wiki '
    if not len(message.text.split()) == 1:
        your_query = ' '.join(message.text.split()[1:])
        user_action_log(message,
                        "entered this query for /wiki:\n{0}".format(your_query))
        try:
            # определяем язык запроса. Эвристика для английского и русского
            if all(ord(x) < 127 or not x.isalpha() for x in your_query):
                wikipedia.set_lang('en')
            # TODO: a bit dirty condition
            elif all(ord(x) < 127 or (ord('Ё') <= ord(x) <= ord('ё')) or not x.isalpha() for x in your_query):
                wikipedia.set_lang('ru')
            else:
                wikipedia.set_lang(detect(your_query))
            wiki_response = wikipedia.summary(your_query, sentences=7)
            if '\n  \n' in str(wiki_response):
                wiki_response = "{}...\n\n" \
                                "<i>В данной статье " \
                                "имеется математическая вёрстка. " \
                                "Ссылка на статью:</i>".format(str(wiki_response).split('\n  \n', 1)[0])
            # print(wiki_response)
            # извлекаем ссылку на саму статью
            wiki_url = parse.unquote(wikipedia.page(your_query).url)
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
            # берём рандомную статью на рандомном языке (языки в config.py)
    else:
        wikipedia.set_lang(random.choice(['en', 'ru']))
        wikp = wikipedia.random(pages=1)
        try:
            print("Trying to get Wikipedia article\n{0}".format(str(wikp)))
            wikpd = wikipedia.page(wikp)
            wiki_fact = wikipedia.summary(wikp, sentences=3)
            my_bot.reply_to(message, "<b>{0}.</b>\n{1}".format(wikpd.title, wiki_fact), parse_mode="HTML")
            user_action_log(message, "got Wikipedia article\n{0}".format(str(wikp)))
        except wikipedia.exceptions.DisambiguationError:
            wikp = wikipedia.random(pages=1)
            try:
                print("Trying to get Wikipedia article\n{0}".format(str(wikp)))
                wiki_var = wikipedia.search(wikp, results=1)
                print("There are multiple possible pages for that article.\n")
                # wikpd = wikipedia.page(str(wiki_var[0]))
                wiki_fact = wikipedia.summary(wiki_var, sentences=4)
                my_bot.reply_to(message, "<b>{0}.</b>\n{1}".format(wikp, wiki_fact), parse_mode="HTML")
            except wikipedia.exceptions.PageError:
                print("Page error for Wikipedia article\n{0}".format(str(wikp)))
                my_bot.reply_to(message, "<b>{0}.</b>".format("You're even unluckier"), parse_mode="HTML")
            except Exception as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                action_log("Unknown Exception in Wikipedia: {}: {}\nat {} line {}".format(exc_type, ex,
                                                                                          fname, exc_tb.tb_lineno))
        except wikipedia.exceptions.PageError:
            print("Page error for Wikipedia article\n{0}".format(str(wikp)))
            my_bot.reply_to(message, "<b>{0}.</b>".format("You're very unlucky bastard"), parse_mode="HTML")

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            action_log("Unknown Exception in Wikipedia: {}: {}\nat {} line {}".format(exc_type, ex,
                                                                                      fname, exc_tb.tb_lineno))

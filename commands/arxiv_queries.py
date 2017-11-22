#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import datetime
import os
import random
import sys
from html import escape
from xml.etree import ElementTree

import arxiv
import pytz
import requests

from utils import my_bot, user_action_log, action_log


def arxiv_checker(message):
    my_bot.send_chat_action(message.chat.id, 'upload_document')
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
        user_action_log(message, "called arxiv search with query {}".format(query))
        my_bot.reply_to(message, query_answer, parse_mode="HTML")

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        action_log("Unknown Exception:\n{}: {}\nat {} line {}\n"
                   "Creating the alert file.".format(exc_type, ex, fname, exc_tb.tb_lineno))


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
        action_log("Random arxiv paper since {}".format(last_published_date))
        # если всё хорошо
        if response.status_code == 200:
            response_tree = ElementTree.fromstring(response.content)
            num_of_papers = len(response_tree[2])
            paper_index = random.randint(0, num_of_papers)
            paper_arxiv_id = response_tree[2][paper_index][0].text.split(':')[-1]  # hardcoded
            papep_obj = arxiv.query(id_list=[paper_arxiv_id])[0]
            paper_link = papep_obj['pdf_url'].replace('http://', 'https://') + '.pdf'
            paper_link_name = paper_link.split("/pdf/")[1]
            print(paper_link)
            print(paper_link_name)
            req_pdf_size = requests.head(paper_link)
            pdf_size = round(int(req_pdf_size.headers["Content-Length"]) / 1024 / 1024, 2)
            query_answer = '{}. <a href="{}">{}</a>. {}\n\n— <a href="{}">{}</a>, {} Мб\n'.format(
                papep_obj['author_detail']['name'],
                papep_obj['arxiv_url'],
                escape(papep_obj['title'].replace('\n', ' ')),
                escape(papep_obj['summary'].replace('\n', ' ')),
                paper_link,
                paper_link_name,
                pdf_size
            )
            my_bot.reply_to(message, query_answer, parse_mode="HTML", disable_web_page_preview=False)
            user_action_log(message,
                            "arxiv random query was successful: "
                            "got paper {}".format(papep_obj['arxiv_url']))
            # TODO(randl): doesn't send. Download and delete?
            # my_bot.send_document(message.chat.id, data=paper_link)
        elif response.status_code == 503:
            # слишком часто запрашиваем
            action_log("Too much queries. 10 minutes break should be enough")
            arxiv_checker.last_call = datetime.datetime.utcnow() - datetime.timedelta(seconds=610)
        else:
            # если всё плохо
            user_action_log(message, "arxiv random query failed: response {}".format(response.status_code))

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        action_log("Unknown Exception: {}: {}\nat {} line {}".format(exc_type, ex, fname, exc_tb.tb_lineno))

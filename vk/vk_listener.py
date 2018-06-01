#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import time

import apscheduler
import facebook
import requests

import config
import tokens
from utils import my_bot, action_log, scheduler
from vk.vk_utils import VkPost


def vk_listener():
    """
    Проверяет наличие новых постов в паблике мехмата и отправляет их при наличии
    :return: None
    """
    if tokens.vk == '':
        return

    try:
        vk_post = vk_get_last_post(config.mm_vk_group)

        if vk_post == 1:
            return
        if vk_post.not_posted():
            action_log("We have new post in mechmath public")

            vk_post.prepare_post()
            try:
                if config.mm_chat != '':
                    vk_post.send_post(config.mm_chat)
                if config.mm_channel != '':
                    vk_post.send_post(config.mm_channel)
                if tokens.fb != '' and config.mm_fb_album != '':
                    try:
                        vk_post.send_post_fb(tokens.fb, config.mm_fb_album)
                    except facebook.GraphAPIError as ex:
                        logging.exception(ex)
                        scheduler.pause_job('vk_listener')
                        my_bot.send_message(config.mm_chat_debug, 'Что-то не так с токеном у ФБ! Проверка новых постов приостановлена.\nФиксики приде, порядок наведе!')
                        action_log('Error reposting a VK post to FB. Most likely there\'s invalid FB token.\nJob "vk_listener" has been paused.')
            except Exception as ex:
                logging.exception(ex)
                my_bot.send_message(config.mm_chat_debug,
                                    "Последний пост вызвал ошибку при репостинге! @rm_bk, выезжай.")
            vk_post.set_as_posted()

        time.sleep(5)

    except requests.exceptions.ReadTimeout:
        action_log("Read Timeout in vkListener() function")
    except requests.exceptions.ConnectionError:
        action_log("Connection Error in vkListener() function")
    except RuntimeError:
        action_log("Runtime Error in vkListener() function")


def vk_get_last_post(vkgroup_id):
    try:
        # Берём первые два поста
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': tokens.vk, 'owner_id': vkgroup_id,
                                        'count': 2, 'offset': 0, 'v': config.vk_ver})
        # print(response.json())
        # Cоздаём json-объект для работы
        posts = response.json()['response']['items']
        # Cверяем два верхних поста на предмет свежести, т.к. верхний может быть запинен
        post = posts[0] if posts[0]['date'] >= posts[1]['date'] else posts[1]
        return VkPost(post)
    except KeyError as ex:
        logging.exception(ex)
        if response.json()['error']['error_code'] == 5:
            scheduler.pause_job('vk_listener')
            my_bot.send_message(config.mm_chat_debug, 'Что-то не так с токеном у ВК! Проверка новых постов приостановлена.\nФиксики приде, порядок наведе!')
            action_log('KeyError exception in vk_listener. Most likely there\'s invalid token.\nJob "vk_listener" has been paused.')
        return 1

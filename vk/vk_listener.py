#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import logging
import time

import requests

import config
import tokens
from utils import my_bot, action_log
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

        if vk_post.not_posted():
            action_log("We have new post in mechmath public")

            vk_post.prepare_post()
            try:
                if config.mm_chat != '':
                    vk_post.send_post(config.mm_chat)
                if config.mm_channel != '':
                    vk_post.send_post(config.mm_channel)
                if tokens.fb != '' and config.mm_fb_album != '':
                    vk_post.send_post_fb(tokens.fb, config.mm_fb_album)
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
    # Берём первые два поста
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': tokens.vk, 'owner_id': vkgroup_id,
                                    'count': 2, 'offset': 0, 'v': '5.68'})

    # Cоздаём json-объект для работы
    posts = response.json()['response']['items']

    # Cверяем два верхних поста на предмет свежести, т.к. верхний может быть запинен
    post = posts[0] if posts[0]['date'] >= posts[1]['date'] else posts[1]

    return VkPost(post)

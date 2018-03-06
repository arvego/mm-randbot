# !/usr/bin/env python
# _*_ coding: utf-8 _*_

import requests
import logging

import config
import tokens
from utils import my_bot, user_action_log
from vk import vk_utils


def vk_post(message):
    if len(message.text.split()) > 1:
        post_id = message.text.split('wall')[-1]
        user_action_log(message, "has requested vk post: {}".format(post_id))
        response = requests.get('https://api.vk.com/method/wall.getById',
                                params={'access_token': tokens.vk, 'posts': post_id,
                                        'extended': '1', 'v': config.vk_ver})
        response_list = response.json()['response']['items']
        if len(response_list) == 0:
            my_bot.reply_to(message, "Неудача! Использование: `/vk vk.com/wall-51776562_939`",
                            parse_mode="Markdown")
            return
        post = vk_utils.VkPost(response_list[0])
        post.prepare_post()
        post.send_post(message.chat.id)
    else:
        my_bot.reply_to(message, "Использование: `/vk vk.com/wall-51776562_939`", parse_mode="Markdown")


def vk_post_last(message):
    if len(message.text.split()) > 1:
        count = message.text.split()[1]
        if not count.isdigit():
            my_bot.reply_to(message, "Неудача! Использование: `/vk_post_last [N]`",
                            parse_mode="Markdown")
            return

        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': tokens.vk, 'owner_id': config.mm_vk_group,
                                        'count': count, 'offset': 0, 'v': config.vk_ver})

        posts = response.json()['response']['items']
        if len(posts) == 0:
            my_bot.reply_to(message, "Неудача! Использование: `/vk_post_last [N]`",
                            parse_mode="Markdown")
            return

        for post in reversed(posts):
            vk_post = vk_utils.VkPost(post)

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
    else:
        my_bot.reply_to(message, "Использование: `/vk_post_last [N]`", parse_mode="Markdown")

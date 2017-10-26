# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import requests
import sys

import tokens
import vk_listener
from utils import my_bot, user_action_log

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def vk_post(message):
    if len(message.text.split()) > 1:
        post_id = message.text.split('wall')[-1]
        user_action_log(message, "has requested vk post: {}\n".format(post_id))
        response = requests.get('https://api.vk.com/method/wall.getById',
                                params={'access_token': tokens.vk, 'posts': post_id, 'v': '5.68'})
        response_list = response.json()['response']
        if len(response_list) == 0:
            my_bot.reply_to(message, "Неудача! Использование: `/vk_post vk.com/wall-51776562_939`",
                            parse_mode="Markdown")
            return
        post = vk_listener.VkPost(response_list[0])
        post.prepare_post()
        post.send_post(message.chat.id)
    else:
        my_bot.reply_to(message, "Использование: `/vk_post vk.com/wall-51776562_939`", parse_mode="Markdown")

#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
import sys
import time

import requests

import config
import tokens
from utils import my_bot, cut_long_text, value_from_file, value_to_file

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def vk_listener():
    '''
    Проверяет наличие новых постов в паблике мехмата и отправляет их при наличии
    :return: None
    '''
    if tokens.vk == '':
        return
    try:
        vk_post = vk_find_last_post()

        if vk_post.not_posted():
            print("{0}\nWe have new post in mechmath public.\n".format(time.strftime(config.time, time.gmtime())))

            vk_post.prepare_post()
            vk_post.send_post(config.my_chatID)
            vk_post.send_post(config.my_channel)

        time.sleep(5)
    except requests.ReadTimeout:
        print("{0}\nRead Timeout in vkListener() function. Because of Telegram API.\n"
              "We are offline. Reconnecting in 5 seconds.\n".format(time.strftime(config.time, time.gmtime())))
    except requests.ConnectionError:
        print("{0}\nConnection Error in vkListener() function.\n"
              "We are offline. Reconnecting...\n".format(time.strftime(config.time, time.gmtime())))
    except RuntimeError:
        print("{0}\nRuntime Error in vkListener() function.\n"
              "Retrying in 3 seconds.\n".format(time.strftime(config.time, time.gmtime())))


def vk_find_last_post():
    # коннектимся к API через requests. Берём первые два поста
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': tokens.vk, 'owner_id': config.vkgroup_id,
                                    'count': 2, 'offset': 0})

    # создаём json-объект для работы
    posts = response.json()['response']

    # сверяем два верхних поста на предмет свежести, т.к. верхний может быть запинен
    post = posts[-2] if posts[-2]['date'] >= posts[-1]['date'] else posts[-1]

    return VkPost(post)


class VkPost:
    '''
    Описывает один пост из ВК.
    Имеет методы для подготовки постов к отправлению в Телеграм
    '''

    def __init__(self, post_in):
        self.post = post_in
        self.date = int(self.post['date'])
        self.owner_id = int(self.post['owner_id']) if 'owner_id' in self.post else 0
        self.final_text = 'VkPost need to prepare'
        self.header_text = ''
        self.footer_text = ''
        self.gif_links = []
        self.image_links = []
        self.audio_links = []
        self.video_links = []
        self.web_preview_url = ''

    def prepare_post(self):
        # Предварительная обработка
        self.attachments_handle()
        self.init_header()

        # Подготовка текстовой части
        post_text = self.header_text + '\n' + self.post['text'] + '\n' + self.footer_text
        post_text.replace("<br>", "\n")
        replace_wiki_links(post_text)

        self.final_text = post_text

    def send_post(self, destination):
        # Отправляем текст, нарезая при необходимости
        for text in cut_long_text(self.final_text):
            text = text.replace('<br>', '\n')
            my_bot.send_message(destination, text, parse_mode="HTML",
                                disable_web_page_preview=self.web_preview_url == '')

        # Отправляем отображаемые приложения к посту
        for url in self.video_links:
            my_bot.send_video(destination, url)
        for url in self.gif_links:
            my_bot.send_document(destination, url)
        for url in self.image_links:
            my_bot.send_photo(destination, url)
        for url in self.audio_links:
            my_bot.send_audio(destination, url)

    def not_posted(self):
        # TODO: refactor double file opening with single
        if self.date > value_from_file(config.vk_update_filename):
            value_to_file(config.vk_update_filename, self.date)  # TODO: write only if successful
            return True
        return False

    def is_repost(self):
        return 'copy_owner_id' in self.post or 'copy_text' in self.post

    def repost_header(self):
        # TODO: попробовать обойтись без дополнительного вызова API (extended = 1)
        original_poster_id = int(self.post['copy_owner_id'])
        web_preview = "<a href=\"{}\">📢</a>".format(self.web_preview_url) if self.web_preview_url != "" else "📢"
        # если значение ключа 'copy_owner_id' отрицательное, то репост из группы
        if original_poster_id < 0:
            response = requests.get('https://api.vk.com/method/groups.getById',
                                    params={'group_ids': -original_poster_id})
            op_name = response.json()['response'][0]['name']
            op_screenname = response.json()['response'][0]['screen_name']

            return web_preview + " <a href=\"https://vk.com/wall{}_{}\">Репост</a> " \
                                 "из группы <a href=\"https://vk.com/{}\">{}</a>:".format(self.owner_id,
                                                                                          self.post['id'],
                                                                                          op_screenname, op_name)
        # если значение ключа 'copy_owner_id' положительное, то репост пользователя
        else:
            response = requests.get('https://api.vk.com/method/users.get',
                                    params={'access_token': tokens.vk, 'user_id': original_poster_id})
            op_name = "{0} {1}".format(response.json()['response'][0]['first_name'],
                                       response.json()['response'][0]['last_name'], )
            op_screenname = response.json()['response'][0]['uid']

            return web_preview + (" <a href=\"https://vk.com/wall{}_{}\">Репост</a> "
                                  "пользователя <a href=\"https://vk.com/id{}\">{}</a>:").format(self.owner_id,
                                                                                                 self.post['id'],
                                                                                                 op_screenname, op_name)

    def post_header(self):
        # TODO: попробовать обойтись без дополнительного вызова API (extended = 1)
        web_preview = "<a href=\"{}\">📋</a>".format(self.web_preview_url) if self.web_preview_url != "" else "📋"
        response = requests.get('https://api.vk.com/method/groups.getById',
                                params={'group_ids': -(int(config.vkgroup_id))})
        op_name = response.json()['response'][0]['name']
        op_screenname = response.json()['response'][0]['screen_name']
        return web_preview + (" <a href=\"https://vk.com/wall{}_{}\">Пост</a> в группе "
                              "<a href=\"https://vk.com/{}\">{}</a>:").format(config.vkgroup_id, self.post['id'],
                                                                              op_screenname, op_name)

    def init_header(self):
        self.header_text = ''
        if self.is_repost():
            if 'copy_text' in self.post:
                self.header_text += self.post['copy_text'] + '\n\n'
            self.header_text += self.repost_header()
        else:
            self.header_text += self.post_header()

        return self.header_text

    def attachments_handle(self):
        first_doc = True
        text_link = ''
        text_docs = ''
        text_note = ''
        text_poll = ''
        text_page = ''
        text_album = ''

        def log_extraction(attach_type, url='no url'):
            print("  Successfully extracted {} URL: {}\n".format(attach_type, url))

        for attachment in self.post['attachments']:
            if attachment['type'] == 'photo':
                for size in ['src_xxbig', 'src_xbig', 'src_big', 'src']:
                    if size in attachment['photo']:
                        attach_url = attachment['photo'][size]
                        self.image_links.append(attach_url)
                        log_extraction(attachment['type'], attach_url)
                        break

            if attachment['type'] in ['posted_photo', 'graffiti', 'app']:
                attach_url = attachment[attachment['type']]['photo_604']
                self.image_links.append(attach_url)
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'video':
                # TODO: fix link for youtube and other (show: ['platform'])
                attach_owner = attachment['video']['owner_id']
                attach_vid = attachment['video']['vid']
                attach_url = "https://vk.com/video{}_{}".format(attach_owner, attach_vid)
                self.video_links.append(attach_url)
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'audio':
                attach_url = attachment['audio']['url']
                self.audio_links.append(attach_url)
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'doc':
                attach_url = attachment['doc']['url']
                if attachment['doc']['ext'] == 'gif':
                    self.gif_links.append(attach_url)
                else:
                    if first_doc:
                        text_docs += "\n— Приложения:\n"
                        first_doc = False
                    text_docs += "<a href=\"{}\">{}</a>, {} Мб\n".format(attach_url, attachment['doc']['title'],
                                                                         round(attachment['doc']['size'] / 1024 / 1024,
                                                                               2))
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'link':
                attach_url = attachment['link']['url']
                text_link += "\n— Ссылка:\n<a href=\"{}\">{}</a>\n".format(attach_url, attachment['link']['title'])
                self.web_preview_url = attachment['link']['preview_url'] if 'preview_url' in attachment[
                    'link'] else attach_url
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'note':
                attach_url = attachment['note']['view_url']
                text_note += "\n— Заметка:\n<a href=\"{}\">{}</a>\n".format(attach_url, attachment['note']['title'])
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'poll':
                text_poll += "\n— Опрос:\n{}, голосов: {}\n".format(attachment['poll']['question'],
                                                                    attachment['poll']['votes'])
                log_extraction(attachment['type'])

            if attachment['type'] == 'page':
                attach_url = attachment['page']['view_url']
                text_page += "\n— Вики-страница:\n<a href=\"{}\">{}</a>\n".format(attach_url,
                                                                                  attachment['page']['title'])
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'album':
                text_album += "\n— Альбом:\n{}, {} фото\n".format(attachment['album']['title'],
                                                                  attachment['album']['size'])
                log_extraction(attachment['type'])

        self.footer_text = text_poll + text_link + text_docs + text_note + text_page + text_album


def replace_wiki_links(text):
    '''
    Меняет вики-ссылки вида '[user_id|link_text]' на стандартные HTML
    :param text: Текст для обработки
    '''
    pattern = re.compile(r"\[([^|]+)\|([^|]+)\]", re.U)
    results = pattern.findall(text, re.U)
    for i in results:
        user_id = i[0]
        link_text = i[1]
        before = "[{0}|{1}]".format(user_id, link_text)
        after = "<a href=\"https://vk.com/{0}\">{1}</a>".format(user_id, link_text)
        text.replace(before, after)

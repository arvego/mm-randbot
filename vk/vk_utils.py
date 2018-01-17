#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import io
import re

import facebook
import requests
from PIL import Image
from first import first
from telebot.types import InputMediaPhoto, InputMediaVideo
from telebot import apihelper

import config
import tokens
from utils import my_bot, action_log, cut_long_text, value_from_file, value_to_file, char_escaping


class VkPost:
    """
    Описывает один пост из ВК.
    Имеет методы для подготовки постов к отправлению в Телеграм
    """

    def __init__(self, post_in):
        self.post = post_in

        self.date = int(self.post['date'])
        self.owner_id = int(self.post['owner_id'])
        self.is_repost = 'copy_history' in self.post
        # Получение приложений репоста и оригинального поста
        self.attachments = self.post.get('attachments', []) + self.post.get('copy_history', [{}])[-1].get('attachments',
                                                                                                          [])

        self.final_text = 'VkPost need to prepare'
        self.final_text_fb = 'VkPost need to prepare'
        self.body_text = ''
        self.header_text = ''
        self.footer_text = ''
        self.gif_links = []
        self.image_links = []
        self.audio_links = []
        self.video_links = []
        self.header_text_fb = ''
        self.repost_header_fb = ''
        self.footer_text_fb = ''
        self.links_fb = []
        self.gif_links_fb = []
        self.image_links_fb = []
        self.audio_links_fb = []
        self.video_links_fb = []
        self.web_preview_url = ''

    def prepare_post(self):
        # Предварительная обработка
        self.attachments_handle()

        # Подготовка текстовой части
        self.init_header()
        self.init_header_fb()
        self.body_text = self.post['text'] if not self.is_repost else self.post['copy_history'][-1]['text']
        self.body_text = char_escaping(self.body_text, mode="html")

        post_text = self.header_text + '\n' + self.body_text + '\n' + self.footer_text
        post_text = post_text.replace("<br>", "\n")
        post_text = replace_wiki_links(post_text)

        post_text_fb = self.header_text_fb + '\n' + self.body_text + '\n' + self.footer_text_fb
        post_text_fb = post_text_fb.replace("<br>", "\n")
        post_text_fb = replace_wiki_links(post_text_fb, raw_link=True)

        self.final_text = post_text
        self.final_text_fb = post_text_fb

    def send_post(self, destination):
        try:
            # Отправляем текст, нарезая при необходимости
            for text in cut_long_text(self.final_text):
                my_bot.send_message(destination, text, parse_mode="HTML",
                                    disable_web_page_preview=self.web_preview_url == '')

            # Отправляем отображаемые приложения к посту
            for url in self.gif_links:
                my_bot.send_document(destination, url)
            if len(self.image_links) > 0:
                my_bot.send_media_group(destination, [InputMediaPhoto(url) for url in self.image_links])
            if len(self.video_links) > 0:
                my_bot.send_media_group(destination, [InputMediaVideo(url) for url in self.video_links])
            for url in self.audio_links:
                my_bot.send_audio(destination, url)
        except apihelper.ApiException:
            action_log("VK Error: api exception")


    def send_post_fb(self, fb_page_token, fb_album):
        api = facebook.GraphAPI(fb_page_token)

        if len(self.image_links) > 1:
            response = requests.get(self.image_links[0])
            pic = Image.open(io.BytesIO(response.content))
            pic_byte = io.BytesIO()
            pic.save(pic_byte, format="png")
            pic_byte.seek(0)
            status = api.put_photo(image=pic_byte, message=self.final_text_fb)
            for url in self.image_links:
                response = requests.get(url)
                pic = Image.open(io.BytesIO(response.content))
                pic_byte = io.BytesIO()
                pic.save(pic_byte, format="png")
                pic_byte.seek(0)
                status = api.put_photo(image=pic_byte, album_path=fb_album + '/photos')
            return
        elif len(self.image_links) == 1:
            response = requests.get(self.image_links[0])
            pic = Image.open(io.BytesIO(response.content))
            pic_byte = io.BytesIO()
            pic.save(pic_byte, format="png")
            pic_byte.seek(0)
            status = api.put_photo(image=pic_byte, message=self.final_text_fb)
            return
        if len(self.links_fb) > 0:
            status = api.put_object(
                parent_object="me", connection_name="feed",
                message=self.final_text_fb,
                link=self.links_fb[0])
        elif len(self.gif_links) > 0 or len(self.audio_links) > 0 or len(self.video_links) > 0:
            my_media = first((self.gif_links, self.audio_links, self.video_links), key=lambda x: len(x) > 0)
            status = api.put_object(
                parent_object="me", connection_name="feed",
                message=self.final_text_fb,
                link=my_media)
        else:
            status = api.put_object(
                parent_object="me", connection_name="feed",
                message=self.final_text_fb,
                link="https://vk.com/wall{}_{}".format(self.owner_id, self.post['id']))
        # вариант Морозова
        '''
        my_link = "https://vk.com/wall{}_{}".format(self.owner_id, self.post['id'])
        status = api.put_object(
                 parent_object="me", connection_name="feed",
                 message="",
                 link=my_link)
        '''

    def not_posted(self):
        return self.date > value_from_file(config.file_location['vk_last_post'])

    def set_as_posted(self):
        value_to_file(config.file_location['vk_last_post'], self.date)

    def repost_header(self):
        # TODO: попробовать обойтись без дополнительного вызова API (extended = 1)
        original_poster_id = int(self.post['copy_history'][-1]['owner_id'])
        web_preview = "<a href=\"{}\">📢</a>".format(self.web_preview_url) if self.web_preview_url != "" else "📢"
        # если значение ключа 'copy_owner_id' отрицательное, то репост из группы
        if original_poster_id < 0:
            response = requests.get('https://api.vk.com/method/groups.getById',
                                    params={'group_ids': -original_poster_id})
            op_name = response.json()['response'][0]['name']
            op_screenname = response.json()['response'][0]['screen_name']
            self.repost_header_fb = "Репост из группы {} (https://vk.com/{}):".format(op_name,
                                                                                      op_screenname)

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
            self.repost_header_fb = "Репост пользователя {} (https://vk.com/id{}):".format(op_name,
                                                                                           op_screenname)

            return web_preview + (" <a href=\"https://vk.com/wall{}_{}\">Репост</a> "
                                  "пользователя <a href=\"https://vk.com/id{}\">{}</a>:").format(self.owner_id,
                                                                                                 self.post['id'],
                                                                                                 op_screenname, op_name)

    def post_header(self):
        # TODO: попробовать обойтись без дополнительного вызова API (extended = 1)
        web_preview = "<a href=\"{}\">📋</a>".format(self.web_preview_url) if self.web_preview_url != "" else "📋"
        response = requests.get('https://api.vk.com/method/groups.getById',
                                params={'group_ids': -(int(self.owner_id))})
        op_name = response.json()['response'][0]['name']
        op_screenname = response.json()['response'][0]['screen_name']
        return web_preview + (" <a href=\"https://vk.com/wall{}_{}\">Пост</a> в группе "
                              "<a href=\"https://vk.com/{}\">{}</a>:").format(self.owner_id, self.post['id'],
                                                                              op_screenname, op_name)

    def init_header(self):
        self.header_text = ''
        if self.is_repost:
            if self.post['text'] != "":
                self.header_text += self.post['text'] + '\n\n'
            self.header_text += self.repost_header()
        else:
            self.header_text += self.post_header()

        return self.header_text

    def init_header_fb(self):
        self.header_text_fb = ''
        if self.is_repost:
            if self.post['text'] != "":
                self.header_text_fb += self.post['text'] + '\n\n'
            self.header_text_fb += self.repost_header_fb

        return self.header_text_fb

    def attachments_handle(self):
        first_doc = True
        text_link = ''
        text_docs = ''
        text_note = ''
        text_poll = ''
        text_page = ''
        text_album = ''
        text_audio = ''
        text_video = ''
        text_link_fb = ''
        text_docs_fb = ''
        text_note_fb = ''
        text_poll_fb = ''
        text_page_fb = ''
        text_album_fb = ''
        text_audio_fb = ''
        text_video_fb = ''

        def log_extraction(attach_type, url='no url'):
            print("  Successfully extracted {} URL: {}\n".format(attach_type, url))

        for attachment in self.attachments:
            if attachment['type'] == 'photo':
                for size in ['photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75']:
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
                if 'player' in attachment['video']:
                    attach_url = attachment['video']['player']
                    # self.video_links.append(attach_url)
                    self.web_preview_url = attach_url
                    log_extraction(attachment['type'], attach_url)
                elif 'platform' in attachment['video']:
                    text_video += "\n— Видео:\n{}\n".format(attachment['video']['title'])
                    text_video_fb += "\n— Видео:\n{}\n".format(attachment['video']['title'])
                else:
                    attach_owner = attachment['video']['owner_id']
                    attach_id = attachment['video']['id']
                    attach_url = "https://vk.com/video{}_{}".format(attach_owner, attach_id)
                    text_video += "\n— Видео:\n<a href=\"{}\">{}</a>\n".format(attach_url, attachment['video']['title'])
                    text_video_fb += "\n— Видео:\n{}\n".format(attachment['video']['title'])
                    # self.video_links.append(attach_url) # Временно отключено до разбирательств (@rm_bk)
                    log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'audio':
                if attachment['audio']['content_restricted']:
                    text_audio += "\n— Аудио:\n{} — {}.\n".format(attachment['audio']['artist'],
                                                                  attachment['audio']['title'])
                    text_audio_fb += "\n— Аудио:\n{} — {}.\n".format(attachment['audio']['artist'],
                                                                     attachment['audio']['title'])
                else:
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
                        text_docs_fb += "\n— Приложения:\n"
                        first_doc = False
                    text_docs += "<a href=\"{}\">{}</a>" \
                                 ", {} Мб\n".format(attach_url, attachment['doc']['title'],
                                                    round(attachment['doc']['size'] / 1024 / 1024, 2))
                    text_docs_fb += "{1}:\n{0}  ({2} Мб)\n".format(attach_url, attachment['doc']['title'],
                                                                   round(attachment['doc']['size'] / 1024 / 1024, 2))
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'link':
                attach_url = attachment['link']['url']
                text_link += "\n— Ссылка:\n<a href=\"{}\">{}</a>\n".format(attach_url, attachment['link']['title'])
                text_link_fb += "\n— Ссылка ({1}):\n{0}\n".format(attach_url, attachment['link']['title'])
                self.links_fb.append(attach_url)
                self.web_preview_url = attachment['link']['preview_url'] if 'preview_url' in attachment[
                    'link'] else attach_url
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'note':
                attach_url = attachment['note']['view_url']
                text_note += "\n— Заметка:\n<a href=\"{}\">{}</a>\n".format(attach_url, attachment['note']['title'])
                text_note_fb += "\n— Заметка ({1}):\n{0}\n".format(attach_url, attachment['note']['title'])
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'poll':
                text_poll += "\n— Опрос:\n«{}», голосов: {}\n".format(attachment['poll']['question'],
                                                                      attachment['poll']['votes'])
                text_poll_fb += "\n— Опрос:\n«{}», голосов: {}\n".format(attachment['poll']['question'],
                                                                         attachment['poll']['votes'])
                for answer in attachment['poll']['answers']:
                    text_poll += "  → {}, голосов: {}\n".format(answer['text'], answer['votes'])
                    text_poll_fb += "  → {}, голосов: {}\n".format(answer['text'], answer['votes'])

                log_extraction(attachment['type'])

            if attachment['type'] == 'page':
                attach_url = attachment['page']['view_url']
                text_page += "\n— Вики-страница:\n<a href=\"{}\">{}</a>\n".format(attach_url,
                                                                                  attachment['page']['title'])
                text_page += "\n— Вики-страница ({1}):\n{0}\n".format(attach_url,
                                                                      attachment['page']['title'])
                log_extraction(attachment['type'], attach_url)

            if attachment['type'] == 'album':
                text_album += "\n— Альбом:\n{}, {} фото\n".format(attachment['album']['title'],
                                                                  attachment['album']['size'])
                text_album_fb += "\n— Альбом:\n{}, {} фото\n".format(attachment['album']['title'],
                                                                     attachment['album']['size'])
                log_extraction(attachment['type'])

        self.footer_text = text_poll + text_link + text_docs + text_video + text_audio + text_note + text_page + text_album
        self.footer_text_fb = text_poll_fb + text_link_fb + text_docs_fb + text_video_fb + text_audio_fb + text_note_fb + text_page_fb + text_album_fb


def replace_wiki_links(text, raw_link=False):
    """
    Меняет вики-ссылки вида '[user_id|link_text]' на стандартные HTML
    :param text: Текст для обработки
    :param raw_link: Меняет способ замены вики-ссылки
    """
    link_format = "{1} (vk.com/{0})" if raw_link else "<a href=\"https://vk.com/{0}\">{1}</a>"
    pattern = re.compile(r"\[([^|]+)\|([^|]+)\]", re.U)
    results = pattern.findall(text, re.U)
    for i in results:
        user_id = i[0]
        link_text = i[1]
        before = "[{0}|{1}]".format(user_id, link_text)
        after = link_format.format(user_id, link_text)
        text = text.replace(before, after)
    return text

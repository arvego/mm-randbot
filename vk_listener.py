#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import io
import logging
import re
import sys
import time

# сторонние модули
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

# модуль с настройками
import data
# модуль с токенами
import tokens
from bot_shared import my_bot

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def vk_find_last_post():
    # коннектимся к API через requests. Берём первые два поста
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': tokens.vk, 'owner_id': data.vkgroup_id, 'count': 2,
                                    'offset': 0})
    try:
        # создаём json-объект для работы
        posts = response.json()['response']
    except Exception as ex:
        time.sleep(3)
        raise ex

    # пытаемся открыть файл с датой последнего поста
    try:
        file_lastdate_read = open(data.vk_update_filename, 'r', encoding='utf-8')
        last_recorded_postdate = file_lastdate_read.read()
        file_lastdate_read.close()
    except IOError:
        last_recorded_postdate = -1
        pass
    try:
        int(last_recorded_postdate)
    except ValueError:
        last_recorded_postdate = -1
        pass
    # сверяем два верхних поста на предмет свежести, т.к. верхний может быть запинен
    post = posts[-2] if posts[-2]['date'] >= posts[-1]['date'] else posts[-1]
    post_date = post['date']

    # наконец, сверяем дату свежего поста с датой, сохранённой в файле
    vk_initiate = False
    if post_date > int(last_recorded_postdate):
        vk_initiate = True
        # записываем дату поста в файл, чтобы потом сравнивать новые посты
        file_lastdate_write = open(data.vk_update_filename, 'w', encoding='utf-8')
        file_lastdate_write.write(str(post_date))
        file_lastdate_write.close()

    return post, vk_initiate


def vk_get_repost_text(post):
    original_poster_id = int(post['copy_owner_id'])
    # если значение ключа 'copy_owner_id' отрицательное, то перед нами репост из группы
    if original_poster_id < 0:
        response_OP = requests.get('https://api.vk.com/method/groups.getById',
                                   params={'group_ids': -original_poster_id})
        name_OP = response_OP.json()['response'][0]['name']
        screenname_OP = response_OP.json()['response'][0]['screen_name']
        # добавляем строку, что это репост из такой-то группы
        return "\n\n<a href=\"<web_preview>\">📢</a> <a href=\"https://vk.com/wall{}_{}\">Репост</a> " \
               "из группы <a href=\"https://vk.com/{}\">{}</a>:\n".format(data.vkgroup_id, post['id'], screenname_OP,
                                                                          name_OP)
    # если значение ключа 'copy_owner_id' положительное, то репост пользователя
    else:
        response_OP = requests.get('https://api.vk.com/method/users.get',
                                   params={'access_token': tokens.vk,
                                           'user_id': original_poster_id})
        name_OP = "{0} {1}".format(response_OP.json()['response'][0]['first_name'],
                                   response_OP.json()['response'][0]['last_name'], )
        screenname_OP = response_OP.json()['response'][0]['uid']
        # добавляем строку, что это репост такого-то пользователя
        return ("\n\n<a href=\"<web_preview>\">📢</a> <a href=\"https://vk.com/wall{}_{}\">Репост</a> "
                "пользователя <a href=\"https://vk.com/id{}\">{}</a>:\n").format(data.vkgroup_id, post['id'],
                                                                                 screenname_OP, name_OP)


def vk_post_get_links(post):
    links = ''
    web_preview_links = []
    vk_annot_link = False
    vk_annot_doc = False
    vk_annot_video = False
    try:
        for attachment in post['attachments']:
            # проверяем есть ли ссылки в посте
            if 'link' in attachment:
                post_url_raw = attachment['link']['url']
                post_url = "<a href=\"{}\">{}</a>\n".format(post_url_raw, attachment['link']['title'])
                if not vk_annot_link:
                    links += '\n— Ссылка:\n'
                    vk_annot_link = True
                links += post_url
                web_preview_links.append(post_url_raw)
                print("Successfully extracted a link:\n{0}\n".format(post_url_raw))

            # проверяем есть ли документы в посте. GIF отрабатываются отдельно
            # в vkListener
            if 'doc' in attachment and attachment['doc']['ext'] != 'gif':
                post_url_raw = attachment['doc']['url']
                doc_name = attachment['doc']['title']
                doc_size = round(attachment['doc']['size'] / 1024 / 1024, 2)
                post_url = "<a href=\"{}\">{}</a>, размер {} Мб\n".format(post_url_raw, doc_name, doc_size)
                if not vk_annot_doc:
                    links += '\n— Приложения:\n'
                    vk_annot_doc = True
                links += post_url
                print("Successfully extracted a document's link:\n{0}\n".format(post_url_raw))

            # проверяем есть ли видео в посте
            if 'video' in attachment:
                post_video_owner = attachment['video']['owner_id']
                post_video_vid = attachment['video']['vid']
                # TODO: fix link for youtube and other
                post_url_raw = "https://vk.com/video{}_{}".format(post_video_owner, post_video_vid)
                post_url = "<a href=\"{}\">{}</a>\n".format(post_url_raw, attachment['video']['title'])
                if not vk_annot_video:
                    links += '\n— Видео:\n'
                    vk_annot_video = True
                links += post_url
                web_preview_links.insert(0, post_url_raw)
                print("Successfully extracted a video's link:\n{0}\n".format(post_url_raw))

    except KeyError:
        pass
    return links, web_preview_links


def vk_send_new_post(destination, vk_final_post, img_src, show_preview):
    # Отправляем текст, нарезая при необходимости
    for text in text_cuts(vk_final_post):
        my_bot.send_message(destination,
                            text,
                            parse_mode="HTML",
                            disable_web_page_preview=not show_preview)

    # Отправляем все изображения
    for img in img_src:
        if img['type'] == 'img':
            my_bot.send_photo(destination, copy(img['data']))
        if img['type'] == 'gif':
            my_bot.send_document(destination, img['data'])


# Вспомогательная функция для нарезки постов ВК
def text_cuts(text):
    max_cut = 3000
    last_cut = 0
    dot_anchor = 0
    nl_anchor = 0

    # я не очень могу в генераторы, так вообще можно писать?
    if len(text) < max_cut:
        yield text[last_cut:]
        return

    for i in range(len(text)):
        if text[i] == '\n':
            nl_anchor = i + 1
        if text[i] == '.' and text[i + 1] == ' ':
            dot_anchor = i + 2

        if i - last_cut > max_cut:
            if nl_anchor > last_cut:
                yield text[last_cut:nl_anchor]
                last_cut = nl_anchor
            elif dot_anchor > last_cut:
                yield text[last_cut:dot_anchor]
                last_cut = dot_anchor
            else:
                yield text[last_cut:i]
                last_cut = i

            if len(text) - last_cut < max_cut:
                yield text[last_cut:]
                return

    yield text[last_cut:]


# проверяет наличие новых постов ВК в паблике Мехмата и кидает их при наличии
def vkListener():
    try:
        # ищем последний пост
        try:
            post, vk_initiate = vk_find_last_post()
        except:
            return

        # инициализируем строку, чтобы он весь текст кидал одним сообщением
        vk_final_post = ''
        show_preview = False
        # если в итоге полученный пост — новый, то начинаем операцию
        if vk_initiate:
            print("{0}\nWe have new post in Mechmath's VK public.\n".format(time.strftime(data.time, time.gmtime())))
            # если это репост, то сначала берём сообщение самого мехматовского поста
            if 'copy_owner_id' in post or 'copy_text' in post:
                if 'copy_text' in post:
                    post_text = post['copy_text']
                    vk_final_post += post_text.replace("<br>", "\n")
                # пробуем сформулировать откуда репост
                if 'copy_owner_id' in post:
                    vk_final_post += vk_get_repost_text(post)

            else:
                response_OP = requests.get('https://api.vk.com/method/groups.getById',
                                           params={'group_ids': -(int(data.vkgroup_id))})
                name_OP = response_OP.json()['response'][0]['name']
                screenname_OP = response_OP.json()['response'][0]['screen_name']
                vk_final_post += (
                    "\n\n<a href=\"<web_preview>\">📃</a> <a href=\"https://vk.com/wall{}_{}\">Пост</a> в группе "
                    "<a href=\"https://vk.com/{}\">{}</a>:\n").format(data.vkgroup_id, post['id'],
                                                                      screenname_OP, name_OP)
            try:
                # добавляем сам текст репоста
                post_text = post['text']
                vk_final_post += post_text.replace("<br>", "\n") + "\n"
            except KeyError:
                pass
            # смотрим на наличие ссылок, если есть — добавляем
            links, web_preview_links = vk_post_get_links(post)
            vk_final_post += links
            # если есть вики-ссылки на профили пользователей ВК вида '[screenname|real name]',
            # то превращаем ссылки в кликабельные
            try:
                pattern = re.compile(r"\[([^|]+)\|([^|]+)\]", re.U)
                results = pattern.findall(vk_final_post, re.U)
                for i in results:
                    screen_name_user = i[0]
                    real_name_user = i[1]
                    link = "<a href=\"https://vk.com/{0}\">{1}</a>".format(screen_name_user, real_name_user)
                    unedited = "[{0}|{1}]".format(screen_name_user, real_name_user)
                    vk_final_post = vk_final_post.replace(unedited, link)
            except Exception as ex:
                logging.exception(ex)

            # смотрим на наличие картинок и GIF
            img_src = []
            try:
                for attachment in post['attachments']:
                    # если есть, то смотрим на доступные размеры.
                    # Для каждой картинки пытаемся выудить ссылку на самое большое расширение, какое доступно
                    if 'photo' in attachment:
                        wegot = False
                        for size in ['src_xxbig', 'src_xbig', 'src_big', 'src']:
                            if size in attachment['photo']:
                                post_attach_src = attachment['photo'][size]
                                wegot = True
                                break

                        if wegot:
                            request_img = requests.get(post_attach_src)
                            img_vkpost = io.BytesIO(request_img.content)
                            img_src.append({'data': img_vkpost,
                                            'type': 'img'})
                            print("Successfully extracted photo URL:\n{0}\n".format(post_attach_src))
                        else:
                            print("Couldn't extract photo URL from a VK post.\n")
                    elif ('doc' in attachment
                          and ('type' in attachment['doc']
                               and attachment['doc']['type'] == 3)
                          or ('ext' in attachment['doc']
                              and attachment['doc']['ext'] == 'gif')):
                        post_attach_src = gif_vkpost = attachment['doc']['url']
                        img_src.append({'data': gif_vkpost,
                                        'type': 'gif'})
                        print("Successfully extracted GIF URL:\n{0}\n".format(post_attach_src))

            except KeyError:
                pass

            for link in web_preview_links:
                show_preview = True
                vk_final_post = vk_final_post.replace("<web_preview>", link)
                break

            vk_final_post = vk_final_post.replace("<br>", "\n")

            vk_send_new_post(data.my_chatID, vk_final_post, img_src, show_preview)
            vk_send_new_post(data.my_channel, vk_final_post, img_src, show_preview)

        time.sleep(5)
    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout:
        # logging.exception(e)
        print(
            "{0}\nRead Timeout in vkListener() function. Because of Telegram API.\n"
            "We are offline. Reconnecting in 5 seconds.\n".format(
                time.strftime(data.time, time.gmtime())))
    # если пропало соединение, то пытаемся снова
    except ConnectionError:
        # logging.exception(e)
        print("{0}\nConnection Error in vkListener() function.\nWe are offline. Reconnecting...\n".format(
            time.strftime(data.time, time.gmtime())))
    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError:
        # logging.exception(e)
        print("{0}\nRuntime Error in vkListener() function.\nRetrying in 3 seconds.\n".format(
            time.strftime(data.time, time.gmtime())))

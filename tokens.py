# _*_ coding: utf-8 _*_

import os

# Set your api tokens and keys manually or through environmental variables
# (add lines to your .bashrc and restart terminal):
# export MM_BOT_TELEGRAM_TOKEN="XXXXX:XXXXXXXXXXX"

default_bot = ""
bot = os.getenv('MM_BOT_TELEGRAM_TOKEN', default_bot)

default_owm = ""
owm = os.getenv('MM_BOT_OWM_TOKEN', default_owm)

default_wolfram = ""
wolfram = os.getenv('MM_BOT_WOLFRAM_TOKEN', default_wolfram)

default_vk = ""
vk = os.getenv('MM_BOT_VK_TOKEN', default_vk)

default_prize = ""
my_prize = os.getenv('MM_BOT_PRIZE_CODEWORD', default_prize)

default_login = ""
default_password = ""
vk_disa_login = os.getenv('MM_BOT_DISA_VK_LOGIN', default_login)
vk_disa_password = os.getenv('MM_BOT_DISA_VK_PASSWORD', default_password)

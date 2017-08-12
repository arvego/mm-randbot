#_*_ coding: utf-8 _*_

import os

# Set your api tokens and keys manually or through enviromental variables (add lines to your .bashrc and restart terminal):
# export MM_BOT_TELEGRAM_TOKEN="XXXXX:XXXXXXXXXXX"

default_bot = ""
bot = os.getenv('MM_BOT_TELEGRAM_TOKEN', default_bot)

default_owm = ""
owm = os.getenv('MM_BOT_OWM_TOKEN', default_owm)

default_wolfram = ""
wolfram = os.getenv('MM_BOT_WOLFRAM_TOKEN', default_wolfram)

default_vk = ""
vk = os.getenv('MM_BOT_VK_TOKEN', default_vk)

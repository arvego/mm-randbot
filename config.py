# _*_ coding: utf-8 _*_

# Чат мехмата
mm_chat = '-1001091546301'

# Тестовый чат
mm_chat_debug = '-1001129974163'

# Канал мехмата
mm_channel = '-1001143764222'

# Группа мехмата вк
mm_vk_group = '-1441'
vk_ver = '5.68'

# Альбом паблика мехмата в ФБ
mm_fb_album = '1690168107688487'

# Mеняет ресурсы на тестовые и включает доступ у админов бота ко всем командам
debug_mode = False
if debug_mode:
    mm_chat = mm_chat_debug
    mm_channel = ''
    mm_vk_group = '-152881225'
    mm_fb_album = ''

# Пути к папкам
data_dir = 'data/'
kek_dir = data_dir + 'kek/'
text_dir = data_dir + 'text/'
task_dir = data_dir + 'task/'
math_dir = data_dir + 'maths/'
prize_dir = data_dir + 'anime/'

gen_dir = 'gen/'
dump_dir = gen_dir + 'dump/'

# Пути к файлам
file_location = {
    '/kek': text_dir + 'DataKek.txt',
    '/help': text_dir + 'DataHelp.txt',
    '/wifi': text_dir + 'DataWifi.txt',
    '/chats': text_dir + 'DataChats.txt',
    '/links': text_dir + 'DataLinks.txt',
    '/rules': text_dir + 'DataRules.txt',
    '/start': text_dir + 'DataStart.txt',
    '/gender': text_dir + 'DataGender.txt',
    '/channels': text_dir + 'DataChannels.txt',
    'chromo': gen_dir + 'chromo_count.txt',
    'bot_logs': gen_dir + 'bot_logs.txt',
    'last_post': gen_dir + 'last_post.txt',
    'vk_config': gen_dir + 'vk_config.json',
    'bot_killed': gen_dir + 'they_killed_me.txt',
    'vk_last_post': gen_dir + 'vk_last_post.txt',
    'kek_file_ids': text_dir + 'DataKek_IDs.txt',
}

# Боремся с тупостью Дисы
disa_vk_group = '-152881225'
disa_id = 208237356
length_of_stupid_message = 16
too_many_messages = 4
stop_disa = [
    'Денис, остановись! Хватит.',
    'Косов, харэ спамить этот несчастный чат.',
    'Как же ты задолбал...'
]
stupid_channels = [-1001366318764, -1001137986351]

gif_links = [
    'https://t.me/mechmath/127603',
    'https://t.me/mechmath/257601',
    'https://t.me/mechmath/257606'
]

welcome_list = [
    'Приветствую',
    'Добро пожаловать',
    'Здарова',
    'Hello',
    'Салют',
    'Aloha',
    'Здрасти-мордасти',
    'Бонжур',
    'Рады видеть',
    'Сколько лет, сколько зим',
    'Здравия желаю',
    'Бал’а даш, маланорэ',
    'Hola',
    'Привіт',
    'Привет',
    'Превед',
    'Ave',
    'Konnichi wa',
    'Вечер в хату'
]

# Лимит сообщений для /compress
compress_num_max = 25

# лимит вызова /kek в час
limit_kek = 60

# ID администраторов бота
admin_ids = [28006241, 207275675, 217917985, 126442350, 221439208, 147100358, 258145124]

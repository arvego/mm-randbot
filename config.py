# _*_ coding: utf-8 _*_

# Чат мехмата
my_chatID = '-1001091546301'

# Канал мехмата
my_channel = '-1001143764222'

# Группа мехмата вк
vkgroup_id = '-1441'

# Mеняет ресурсы на тестовые и включает доступ у админов бота ко всем командам
debug_mode = False
# debug_mode = True
if debug_mode:
    my_chatID = '-1001129974163'
    my_channel = ''
    vkgroup_id = '-152881225'

# вставь полный путь к папке со всеми данными
my_core_dir = 'data/'

# индекс всех необходимых папок с картинками
dir_location_prize = my_core_dir + 'anime/'
dir_location_task = my_core_dir + 'task/'
dir_location_maths = my_core_dir + 'maths/'
dir_location_kek = my_core_dir + 'kek/'

file_location = {
    '/chats': 'data/text/DataChats.txt',
    '/gender': 'data/text/DataGender.txt',
    '/help': 'data/text/DataHelp.txt',
    '/kek': 'data/text/DataKek.txt',
    '/links': 'data/text/DataLinks.txt',
    '/rules': 'data/text/DataRules.txt',
    '/start': 'data/text/DataStart.txt',
    '/wifi': 'data/text/DataWifi.txt'
}

my_gen_dir = 'gen/'
file_location_disa = my_gen_dir + 'DataDisa.txt'
file_location_lastbotpost = my_gen_dir + 'DataLastPostID.txt'
vk_update_filename = my_gen_dir + 'vk_update_time.txt'

# Боремся с тупостью Дисы
vk_disa_groupID = '-152881225'
disa_id = 208237356
length_of_stupid_message = 17
too_many_messages = 4
stop_disa = [
    'Денис, остановись! Хватит.',
    'Косов, харэ спамить этот несчастный чат.',
    'Как же ты задолбал...'
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

# лимит вызова /kek в час
limit_kek = 60

# ID администраторов бота
admin_ids = [28006241, 207275675, 217917985, 126442350, 221439208, 147100358, 258145124]

# индикатор для .sh скрипта, что нужно перезапустить бот
bot_down_filename = 'iamdown.txt'
# индикатор для .sh скрипта, что бота убили мы -- перезапускать не нужно
bot_killed_filename = 'theykilledme.txt'
bot_update_filename = 'runningupdate.txt'

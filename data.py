#_*_ coding: utf-8 _*_
import os

#вставь chatID чата Мехмата
my_chatID = "-1001129974163"

#вставь полный путь к папке со всеми данными
my_core_dir = "data/"

#индекс всех необходимых папок с картинками
dir_location_prize = my_core_dir+"anime/"
dir_location_task  = my_core_dir+"task/"
dir_location_maths = my_core_dir+"maths/"
dir_location_meme  = my_core_dir+"memes/"
dir_location_kek   = my_core_dir+"kek/"
dir_location_other = my_core_dir+"other/"

#индекс всех необходимых текстовых файлов
my_text_dir = my_core_dir+"text/"
file_location_start = my_text_dir+"DataStart.txt"
file_location_help  = my_text_dir+"DataHelp.txt"
file_location_links = my_text_dir+"DataLinks.txt"
file_location_truth = my_text_dir+"DataTruth.txt"
file_location_wifi  = my_text_dir+"DataWifi.txt"
file_location_kek   = my_text_dir+"DataKek.txt"

difficulty = ["1", "2", "3"]
subjects = ["algebra", "calculus", "funcan"]

d6_symbols = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

#языки, статьи на которых кидает /wiki без аргумента
wiki_langs = ["en", "ru"]

##базовая настройка игры /number
#guessnum_attempts = 5
#guessnum_maxnum = 100

#ID паблика Мехмата в ВК
vkgroup_id = '-1441'
#интервал в секундах, с которым vkListener() запрашивает обновления
vk_interval = 30
#путь к файлу с датой последнего поста
vk_update_filename = "vk_update_time.txt"


#бред для угара
weather_HAARP = """\r<b>HAARP может быть использован так, чтобы в выбранном районе была полностью нарушена морская и воздушная навигация, блокированы радиосвязь и радиолокация, выведена из строя бортовая электронная аппаратура космических аппаратов, ракет, самолётов и наземных систем. В произвольно очерченном районе может быть прекращено использование всех видов вооружения и техники. Интегральные системы геофизического оружия могут вызвать масштабные аварии в любых электрических сетях, на нефте- и газопроводах. Энергия излучения HAARP может быть использована для манипулирования погодой в глобальном масштабе, для нанесения ущерба экосистеме или её полного разрушения.</b>"""
the_TRUTH = """\r<b>Через 1.1 миллиарда лет, начиная с сегодняшнего дня, Солнце начнет меняться. Как водородный двигатель, в котором заканчивается топливо, и горение начинает происходить не внутрь, а наружу. Солнце станет ярче. Радиация увеличится и разрушит к чертям нашу планету. А будет это так… \nСредняя температура поверхности Земли увеличится с 20С до 75С. Океаны, само собой, испарятся, и планета станет безжизненной пустыней. \nЧерез 1.2 миллиарда лет Солнце начнет «сдуваться», и его масса уменьшиться более, чем на четверть. Само собой, из-за того, что изменится масса нашей звезды, изменится и притяжение, и планеты поменяют свои орбиты. Венера удалиться от Солнца приблизительно на то же расстояние, на котором сейчас находится Земля, а Земля «отъедет» еще дальше. Но это ненадолго, совсем в скором времени Солнце вновь начнет неумолимо увеличиваться и, в итоге, превратится в красного гиганта – его размер будет в 166 раз больше, чем был (это почти как орбита, по которой сейчас двигается Земля). Меркурий и Венера просто сгорят в пламени гиганта. Горы на Земле будут таять и течь раскаленными лавовыми потоками. А раздувшееся красное Солнце занимать половину неба. Но этого не увидят даже тараканы. \nБез топлива, Солнце, наконец, начнет умирать по-настоящему. Последние остатки гелия и водорода при «схлопывании» увеличат размер Солнца в 180 раз и сделают его в тысячу раз ярче. Это будет последний «вздох» нашей звезды. После чего она резко уменьшится вдвое. Потеря массы отбросит Венеру и Землю – точнее головешки, которые от них остались, еще дальше в космос. \nТонкая оболочка гелия, окружающая углеродно-кислородное ядро Солнца станет нестабильной. Солнце начнет сильно пульсировать, как, скажем, полицейская мигалка. И каждая такая «пульсация» будет грозить Солнцу потерей его массы. Последний импульс в буквальном смысле «сдует» остатки внешней поверхности звезды. Все что останется – голое ядро, размером приблизительно с Землю, какой мы ее знаем сегодня. Оно будет очень горячим, но это будет остаточное тепло – его уже ничто не будет подпитывать. И как уголек в остывающем костре, оно постепенно будет остывать, пока не превратиться просто в кусок холодного космического камня.\nТогда с останков нашей планеты, сгоревшей дотла, можно будет увидеть белого карлика, в которого превратилось Солнце. Но, конечно, никто не увидит, никто не оценит. К тому моменту наша система будет уже безвозвратно мертва.</b>"""


#формат времени для логов в консоли
time = "%d/%m/%Y %H:%M:%S"

#ID администраторов бота
admin_ids = [28006241, 207275675]

#индикатор для .sh скрипта, что нужно перезапустить бот
bot_down_filename = "iamdown.txt"
#индикатор для .sh скрипта, что бота убили мы -- перезапускать не нужно
bot_killed_filename = "theykilledme.txt"


default_prize = ""
default_kill = ""
my_prize = os.getenv('MM_BOT_PRIZE_CODEWORD', default_prize)
my_killswitch = os.getenv('MM_BOT_KILL_CODEWORD', default_kill)

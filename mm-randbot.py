#!/usr/bin/env python
#_*_ coding: utf-8 _*_
import telebot
import random
import os
import time
import logging
import requests
import pyowm
import wikipedia
import data

myBot = telebot.TeleBot(data.myToken)
#myBot.send_message(message.chat.id, "Hi.")
global changeRandNum
global randNumAttempts
global youWin
global maxNum
global isMaxZero
global weatherBold
changeRandNum=1
randNumAttempts=data.guessNum_Attempts
youWin=False
maxNum=data.guessNum_maxNum
isMaxZero=False
weatherBold=False

@myBot.message_handler(commands=['start', 'help'])
def myGreeter(message):
	myBot.reply_to(message, 
		"\tПривет. Это рандомный бот для рандомного чата Мехмата. Написан forthelolz на Python.\n \n На данный момент бот умеет следующую фигню:\n\tЕсли после вызова бота написать в произвольном регистре предмет \'Algebra\', \'Calculus\', \'FuncAn\', то он выдаст картинку с рандомным определением или теоремой, связанной с этим предметом.\n\tЕсли ввести \'Maths\', то он выдаст рандомную картинку рандомного предмета.\n\tЕсли ввести \'Challenge\', то он скинет картинку с задачей из банка www.problems.ru.\n\tЕсли ввести \'Fact\', то он скинет первые три предложения рандомной статьи из Википедии либо на английском, либо на русском.\nЕсли ввести \'Roulette\', то он проверит, насколько вы везучие.\n\n\tКоманда \'/number [int]\' начинает игру с угадыванием целого числа от 0 до [int], загаданного ботом. Если получится отгадать не с последней попытки для [int]>99, то получишь приз.\n\tКоманда \'/weather\' даёт отчёт о нынешней погоде в МСК, а также прогноз на три ближайших дня. Только на английском, ибо у меня нету денег на premium API токен, но вы держитесь там.\n\n\tВведите \'MEMES\' для мемчиков.\n Ну и куда же без 'kek'-а в мехматянском чате.\n\nЭто первый release, и это мой самый первой бот. Так что всё фигово пока.")
	print("User "+str(message.from_user.id)+" started using mm-randbot or looked for help.\n")

@myBot.message_handler(commands=['number'])
def guessNumber(message):
	global yourNum
	global randNum
	global randNumAttempts
	global numExtractor
	global changeRandNum
	global youWin
	global maxNum
	global isMaxZero
	global understandableNum
	yourNum=-1
	isMaxZero=False
	isNegative=False
	understandableNum=True
	yourInt=[]
	if changeRandNum==1 :
		for s in str(message.text).split():
			if s.isdigit():
				maxNum = int(s)
				print maxNum
				understandableNum=True
			elif (not s=="/number") and (not s.isdigit()):
				for j in range(len(s)):
					if s[0]=="-":
						isNegative=True
						understandableNum=True
						break
					else:
						understandableNum=False
						break
				for i in range(j, len(s)):
#					print(s[i])
#					if type(s[i])==int:
					yourInt.append(s[i])
				try:
					maxNum=int(''.join(yourInt))
				except ValueError:
					myBot.reply_to(message, "Я не понял число.\nБеру стандартное максимальное целое.")
					changeRandNum=0
					maxNum=data.guessNum_maxNum
					break
#			print(s)
#		randNum=random.randint(0, data.guessNum_maxNum)
		if maxNum==0 :
			isMaxZero=True
			randNum=random.randint(0, abs(maxNum))
			myBot.reply_to(message, "Это скучно, ты же знаешь, что я смог загадать только 0.\n Вызови \'/number\' ещё раз и дай мне любое другое целое для максимума.")
			changeRandNum=1
			numExtractor=0
		else:
			randNum=random.randint(0, abs(maxNum))
			randNumAttempts=data.guessNum_Attempts
			youWin=False
			changeRandNum=0
			myBot.reply_to(message, "Окей, я загадал рандомное целое число от 0 до "+str(abs(maxNum))+". Напиши свою догадку в виде \'/number <число>\'.\nУ тебя есть "+str(randNumAttempts)+" попыток.")
#		randNumAttempts=randNumAttempts+1
			numExtractor=abs(maxNum)+1

#	youWin=False
	for s in str(message.text).split():
		if s.isdigit():
			numExtractor = int(s)
#			print(numExtractor)
		yourNum=numExtractor
#	print(changeRandNum)
#	print(randNum)
	if (randNumAttempts>=1) and (not youWin) and (changeRandNum==0) and (not isMaxZero):
		if yourNum>randNum:
			if randNumAttempts==data.guessNum_Attempts:
				crap=-1
				randNumAttempts=randNumAttempts-1
			elif randNumAttempts==1:
				myBot.reply_to(message, "Твоё число оказалось больше загаданного.\nОсталась всего лишь "+str(randNumAttempts)+" попытка.")
				changeRandNum=0
				randNumAttempts=0
			else:
				myBot.reply_to(message, "Твоё число оказалось больше загаданного.\nОсталось "+str(randNumAttempts)+" попытки.")
				changeRandNum=0
				randNumAttempts=randNumAttempts-1
		elif yourNum<randNum:
			if randNumAttempts==1:
				myBot.reply_to(message, "Твоё число оказалось меньше загаданного.\nОсталась всего лишь "+str(randNumAttempts)+" попытка.")
				changeRandNum=0
				randNumAttempts=0
			else:
				myBot.reply_to(message, "Твоё число оказалось меньше загаданного.\nОсталось "+str(randNumAttempts)+" попытки.")
				changeRandNum=0
				randNumAttempts=randNumAttempts-1
		else:
			if randNumAttempts==data.guessNum_Attempts:
				crap=-1
				randNumAttempts=randNumAttempts-1
			youWin=True
			if (data.guessNum_Attempts-randNumAttempts==1):
				myBot.reply_to(message, "Красава! Прям сразу угадал. Как?!")
				if abs(maxNum)>=100:
					pathDir = data.myDir+"/anime"
					allImgs = os.listdir(pathDir)
					randFile = random.choice(allImgs)
					yourFile = open(pathDir+"/"+randFile, "rb")
					if randFile.endswith(".gif"):
						myBot.send_chat_action(message.from_user.id, 'upload_photo')
						myBot.send_document(message.from_user.id, yourFile)
					else:
						myBot.send_chat_action(message.from_user.id, 'upload_photo')
						myBot.send_photo(message.from_user.id, yourFile)
					yourFile.close()		
				changeRandNum=1
			else:
				myBot.reply_to(message, "Поздравляю! Ты угадал моё загаданное число за "+str(data.guessNum_Attempts-randNumAttempts)+" попытки.")
				if abs(maxNum)>=100:
					pathDir = data.myDir+"/anime"
					allImgs = os.listdir(pathDir)
					randFile = random.choice(allImgs)
					yourFile = open(pathDir+"/"+randFile, "rb")
					if randFile.endswith(".gif"):
						myBot.send_chat_action(message.from_user.id, 'upload_photo')
						myBot.send_document(message.from_user.id, yourFile)
					else:
						myBot.send_chat_action(message.from_user.id, 'upload_photo')
						myBot.send_photo(message.from_user.id, yourFile)
					yourFile.close()
#			randNumAttempts=4
			changeRandNum=1
	elif randNumAttempts==0:
		if yourNum==randNum:
			youWin=True
			if abs(maxNum)>=100:
				myBot.reply_to(message, "Хорош. Впритык успел отгадать моё число за "+str(data.guessNum_Attempts-randNumAttempts)+" попыток.\nДля получения приза попробуй всё же отгадать не впритык. :) Удачи.")
			else:
				myBot.reply_to(message, "Хорош. Впритык успел отгадать моё число за "+str(data.guessNum_Attempts-randNumAttempts)+" попыток.")
#			randNumAttempts=4
			changeRandNum=1
		else:
			myBot.reply_to(message, "Прости, ты не отгадал. Я загадал число "+str(randNum)+".\nДля новой игры введи команду \'/number <желаемое максимальное рандомное число>\'.")
			changeRandNum=1

	print("User "+str(message.from_user.id)+" guessed that number: "+str(yourNum)+".\nThe correct number is "+str(randNum)+".\n")
#	elif randNumAttempts==4:
#		crap=0
#		randNumAttempts=randNumAttempts-1
#	triggerMaxRandNum=False
#	else: 
#		changeRandNum=1
#		youWin=True
#		break
#		numHandler(numExtractor, randNumAttempts)
#		randNumAttempts=randNumAttempts-1

@myBot.message_handler(commands=['weather'])
def myWeather(message):
	global weatherBold
	myOWM=pyowm.OWM(data.owmToken)
#	myRusOWM=pyowm.OWM(language='ru') Нужен про аккаунт. Вы держитесь там.
	myObs=myOWM.weather_at_place('Moscow')
	w=myObs.get_weather()
	status=w.get_detailed_status()
	tempNow=w.get_temperature('celsius')
#	print(str(tempNow['temp']), status)
	myForecast=myOWM.daily_forecast('Moscow,RU', limit=3)
	myFc=myForecast.get_forecast()
	myFcTemps=[]
	myFcStatuses=[]
	for wth in myFc:
#		print(str(wth.get_temperature('celsius')['day']), str(wth.get_status()))
		myFcTemps.append(str(wth.get_temperature('celsius')['day']))
		myFcStatuses.append(str(wth.get_status()))
	if weatherBold:
		myBot.send_message(message.from_user.id, """\r
	<b>HAARP может быть использован так, чтобы в выбранном районе была полностью нарушена морская и воздушная навигация, блокированы радиосвязь и радиолокация, выведена из строя бортовая электронная аппаратура космических аппаратов, ракет, самолётов и наземных систем. В произвольно очерченном районе может быть прекращено использование всех видов вооружения и техники. Интегральные системы геофизического оружия могут вызвать масштабные аварии в любых электрических сетях, на нефте- и газопроводах. Энергия излучения HAARP может быть использована для манипулирования погодой в глобальном масштабе, для нанесения ущерба экосистеме или её полного разрушения.</b>""", parse_mode="HTML")
		weatherBold=False
		print("User "+str(message.from_user.id)+" got HAARP'd.\n")
	else:
		myBot.reply_to(message, "The current temperature in Moscow is "+str(tempNow['temp'])+" C, and it is "+str(status)+".\n\n Tomorrow it will be "+str(myFcTemps[0])+" C. "
	+str(myFcStatuses[0])+".\n In 2 days it will be "+str(myFcTemps[1])+" C. "
	+str(myFcStatuses[1])+".\n In 3 days it will be "+str(myFcTemps[2])+" C. "
	+str(myFcStatuses[2])+".")
		print("User "+str(message.from_user.id)+" got that forecast:\n"+"The current temperature in Moscow is "+str(tempNow['temp'])+" C, and it is "+str(status)+".\n\n Tomorrow it will be "+str(myFcTemps[0])+" C. "
	+str(myFcStatuses[0])+".\n In 2 days it will be "+str(myFcTemps[1])+" C. "
	+str(myFcStatuses[1])+".\n In 3 days it will be "+str(myFcTemps[2])+" C. "
	+str(myFcStatuses[2])+".\n")

@myBot.message_handler(content_types={'text'})
def defaultHandler(message):
	global weatherBold
	print("User "+str(message.from_user.id)+" typed in: "+str(message.text))
	yourMsg=str.lower(str(message.text))
	if yourMsg == "maths":
		allImgs = []
		for root, directories, filenames in os.walk(data.myDir):
			for filename in filenames:
				if (not (filename.startswith("meme"))) and (not (filename.startswith("challenge")))	and (not (filename.startswith("anime"))) and (not (filename.startswith("42"))) and (not (filename.startswith("69"))):
					allImgs.append(str(os.path.join(root,filename)))
#		print(allImgs)
		randImg = random.choice(allImgs)
		yourImg = open(randImg, "rb")
		myBot.send_chat_action(message.from_user.id, 'upload_photo')
		myBot.send_photo(message.from_user.id, yourImg)
		print("User "+str(message.from_user.id)+" got that image:\n"+str(randImg)+"\n")
		yourImg.close()
	elif yourMsg in data.myListOfSubjects:
		pathDir = data.myDir+"/"+yourMsg
		allImgs = os.listdir(pathDir)
		randImg = random.choice(allImgs)
		yourImg = open(pathDir+"/"+randImg, "rb")
#		myBot.send_chat_action(message.from_user.id, 'upload_photo')
#		myBot.send_photo(message.from_user.id, yourImg)
		if randImg.endswith(".gif"):
			myBot.send_chat_action(message.from_user.id, 'upload_photo')
			myBot.send_document(message.from_user.id, yourImg)
		else:
			myBot.send_chat_action(message.from_user.id, 'upload_photo')
			myBot.send_photo(message.from_user.id, yourImg)

		print("User "+str(message.from_user.id)+" got that file:\n"+str(pathDir+"/"+randImg)+"\n")
		yourImg.close()
	elif yourMsg in data.myListOfOther:
#		if yourMsg == "number":
#			playNumGame=True
		if yourMsg == "fact":
			wikipedia.set_lang(random.choice(data.wikiLangs))
			wikp=wikipedia.random(pages=1)
			wikpd=wikipedia.page(wikp)
#			print(wikp)
			try:
				wikiFact=wikipedia.summary(wikp, sentences=3)
				myBot.reply_to(message, wikpd.title+".\n"+wikiFact)
			except wikipedia.exceptions.DisambiguationError as e:
				myBot.reply_to(message, "Что-то пошло не так. :( Я такой рандомный. Попробуй снова.")
			print("User "+str(message.from_user.id)+" got Wikipedia article\n"+wikp+"\n")
		if yourMsg == "roulette":
			yourDestiny=random.randint(1,72)
			if yourDestiny==42:
				pathDir = data.myDir
				yourImg = open(pathDir+"/42.jpg", "rb")
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_photo(message.from_user.id, yourImg)
				yourImg.close()

				print("User "+str(message.from_user.id)+" recieved 42.\n")
			elif yourDestiny==13:
#				myBot.send_message(message.chat.id, "You died!")
				myBot.reply_to(message, "Прощай, зайчик!")
				pathDir = data.myDir+"/MEMES"
				yourImg = open(pathDir+"/memeProblem.png", "rb")
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_photo(message.from_user.id, yourImg)
				yourImg.close()
				myBot.kick_chat_member(message.chat.id, message.from_user.id)

				print("User "+str(message.from_user.id)+" has been kicked out.\n")
			elif yourDestiny==69:
				yourFile = open(data.myDir+"/69HEYOO.gif", "rb")
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_document(message.from_user.id, yourFile)
				yourFile.close()

				print("User "+str(message.from_user.id)+" recieved 69. Lucky guy.\n")
#				myBot.send_message(message.chat.id, "HEYO.")
#				myBot.reply_to(message, "HEYO.")
			else:
				myBot.reply_to(message, str(yourDestiny))
				print("User "+str(message.from_user.id)+" recieved "+str(yourDestiny)+".\n")
		elif yourMsg == "memes":
			pathDir = data.myDir+"/MEMES"
			allImgs = os.listdir(pathDir)
			randFile = random.choice(allImgs)
			yourFile = open(pathDir+"/"+randFile, "rb")
			if randFile.endswith(".gif"):
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_document(message.from_user.id, yourFile)
			else:
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_photo(message.from_user.id, yourFile)
			
			print("User "+str(message.from_user.id)+" got that meme:\n"+str(pathDir+"/"+randFile)+"\n")
			yourFile.close()
		elif yourMsg == "kek":
			yourDestiny=random.randint(1,60)
			if yourDestiny==13:
				myBot.reply_to(message, "Предупреждал же, что кикну. Если не предупреждал, то ")
				pathDir = data.myDir+"/MEMES"
				yourImg = open(pathDir+"/memeSurprise.gif", "rb")
				myBot.send_chat_action(message.from_user.id, 'upload_photo')
				myBot.send_document(message.from_user.id, yourImg)
				yourImg.close()
				myBot.kick_chat_member(message.chat.id, message.from_user.id)

				print("User "+str(message.from_user.id)+" has been kicked out.\n")
			else:
				fKek=random.choice(data.myListOfHate4Kek)
				if (str(fKek)==str("Чекни /weather.")):
					weatherBold=True
#				myBot.send_message(message.chat.id, str(fKek))
				myBot.reply_to(message, str(fKek))

				print("User "+str(message.from_user.id)+" got that kek:\n"+str(fKek)+"\n")
	elif yourMsg == data.myKillswitch:
		myBot.reply_to(message, "Прощай, жестокий мир.\n;~;")
		try:
			print("Bot has been killed off remotely by user "+str(message.from_user.id)+".")
			exit()
		except RuntimeError:
			exit()
	else:
#		myBot.send_message(message.chat.id, "Lolwat.")
		myBot.reply_to(message, "Не понимаю. Обратись к команде \'/help\' чтобы посмотреть доступные опции.")
		print("User "+str(message.from_user.id)+" typed something I could not understand.\n")

while __name__ == '__main__':
	try:
		botUpdate=myBot.get_updates()
#		lastUpdate=botUpdate
#		print(botUpdate)
#		print(lastUpdate)
		myBot.polling(none_stop=True, interval=1)
		time.sleep(1)
	except requests.exceptions.Timeout:
		logging.exception("Can't keep up. Timeout because of API.")
		time.sleep(3)
	except RuntimeError:
		logging.exception("Can't keep up.")
		time.sleep(10)
	except UnicodeEncodeError:
		logging.exception("Can't keep up. Someone typed in cyrillic.")
		time.sleep(5)
	except KeyboardInterrupt:
		exit()

#!/bin/bash

STATUS=0                            `#переменная для бесконечного цикла`
FILENAME="iamdown.txt"              `#переменная для упавшего бота (из data.py)`
FILENAME_KILL="theykilledme.txt"    `#переменная для убитого бота (из data.py)`
NOTIFIED=0                          `#переменные чтобы не флудить консоль`
NOTIFIED_KILL=0

`#инициализация вечного цикла`
while [ $STATUS -eq "0" ]; do
`#если бот лежит и не убит нами, или если не запущен вовсе, то воскрешаем его`
    if [ -e $FILENAME ] && [ ! -e $FILENAME_KILL ] || [ $(ps -ef | grep "python ./mm-randbot.py" | grep -v "grep" | wc -l) -eq "0" ] && [ ! -e $FILENAME_KILL ]; then
        printf "Bot is down. Ressurecting it.\n-----------------------------\n\n"
        NOTIFIED=0
        NOTIFIED_KILL=0
        python mm-randbot.py
`#что-то снова упало, уже после воскрешения бота`
        printf "\n---------------------------\nBot has been stopped again.\n\n"
        sleep 3s;
`#если бота убили мы`
    elif [ -e $FILENAME_KILL ]; then
        if [ $NOTIFIED_KILL -eq "0" ]; then
`#исправляем наши проблемы, меняем кодовое слово и удаляем алёрт файл`
            printf "Bot has been killed off.\nPlease restart it manually once you fixed everything or remove $FILENAME_KILL.\n\n"
            NOTIFIED=0
            NOTIFIED_KILL=1;
        else
            sleep 10s;
        fi
`#если всё хорошо, и бот уже запущен`
    else
        if [ $NOTIFIED -eq "0" ]; then
            printf "Bot is running successfully.\n\n"
            NOTIFIED=1;
        else
            sleep 10s;
        fi
    fi
done

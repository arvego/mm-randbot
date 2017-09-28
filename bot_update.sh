#!/bin/bash

FILENAME="runningupdate.txt"

if [ -e $FILENAME ]; then
    # Stop all bot processes
    kill -9 $(ps aux | grep 'mm-randbot.py' | awk '{print $2}')
    kill -9 $(ps aux | grep 'bot_status.sh' | awk '{print $2}')

    cd ..
    rm -rf mm-randbot/
    git clone -b "disa_branch" https://github.com/arvego/mm-randbot.git
    cd mm-randbot/
    bash bot_status.sh
fi

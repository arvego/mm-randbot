#!/bin/bash

FILENAME="runningupdate.txt"

if [ -e $FILENAME ]; then
    kill $(ps aux | grep '[p]ython2 mm-randbot.py' | awk '{print $2}')
    kill $(ps aux | grep '[b]ash bot_status.sh' | awk '{print $2}')
    cd ..
    rm -rf mm-randbot/
    git clone -b "disa_branch" https://github.com/arvego/mm-randbot.git
    cd mm-randbot/
    bash bot_status.sh
fi

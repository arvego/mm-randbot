#!/bin/bash

FILENAME="runningupdate.txt"

if [ -e $FILENAME ]; then
    # Stop all bot processes
    kill -9 $(ps aux | grep 'mm-randbot.py' | awk '{print $2}')
    kill -9 $(ps aux | grep 'bot_status.sh' | awk '{print $2}')
    # Stage all changes
    git add -A
    git commit -m "bot_update: unpushed changes"
    # Update repo
    git pull --rebase
    rm $FILENAME
    # Run bot
    bash bot_status.sh
fi

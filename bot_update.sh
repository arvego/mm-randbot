#!/bin/bash

FILENAME="runningupdate.txt"

if [ -e $FILENAME ]; then
    # Stop all bot processes
    kill $(ps aux | grep '[p]ython2 mm-randbot.py' | awk '{print $2}')
    kill $(ps aux | grep '[b]ash bot_status.sh' | awk '{print $2}')
    # Stage all changes
    git add -A
    git commit -m "bot_update: unpushed changes"
    # Update repo
    git pull --rebase
    rm $FILENAME
    # Run bot
    bash bot_status.sh
fi

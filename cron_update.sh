#!/bin/bash

###
### Script need to be used with cron for bot reruning.
###
### For every 5 minute script running add line to crontab:
### */5 * * * * /path/to/dir/cron_update.sh
### Or add with command:
### $ (crontab -l ; echo "*/5 * * * * /path/to/dir/cron_update.sh") | crontab -
###

### Main cfg parameters

SCRIPT_NAME=$(basename $0)
SCRIPT_DIR=$(readlink -f $(dirname $0))

cd $SCRIPT_DIR

### Restart bot if died

if [ $(pgrep -cf mm-randbot) -eq "0" ]
then
  echo "Bot is dead. Resurrecting it."
  python2 ./mm-randbot.py
else
  echo "Bot is still alive."
fi

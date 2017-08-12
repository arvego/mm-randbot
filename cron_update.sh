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

if [ "$(pgrep -cf mm-randbot)" == "0" ]
then
  echo "Bot is down, need a resurrection"
  python ./mm-randbot.py
else
  echo "Bot still alive"  
fi

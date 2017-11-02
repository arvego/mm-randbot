#!/bin/bash

echo "=== UPDATING THE BOT ==="
git stash save -u -m 'Autostash before update'
git pull < /dev/null &&
echo "=== UPDATE COMPLETE ===" &&
exec ./mm-randbot.py

# if anything went wrong...
echo "!!! UPDATE FAILED !!!"
git reset --hard

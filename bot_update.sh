#!/bin/bash

echo "=== UPDATING THE BOT ==="
git reset --hard
git pull < /dev/null &&
echo "=== UPDATE COMPLETE ===" &&
exec ./mm-randbot.py

# if anything went wrong...
echo "!!! UPDATE FAILED !!!"
git reset --hard

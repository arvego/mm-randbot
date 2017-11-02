#!/bin/bash

echo "=== UPDATING THE BOT ==="
git pull < /dev/null &&
echo "=== UPDATE COMPLETE ===" &&
exec ./mm-randbot.py

echo "!!! UPDATE FAILED !!!"

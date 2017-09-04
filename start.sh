#!/bin/bash

# Set the chatscript host address.
sed -i -e 's/^$host = "1.22.08.4"/$host = "localhost"/g' \
  ChatScript-engine/WEBINTERFACE/SPEECH/ui.php

# Start the server.
nohup caddy > /dev/null 2>&1 > caddy.logs &

# Start the chatscript engine.
cd ChatScript-engine && ./run.sh --users ../users --logs ../logs --topic ../topic --tmp ../tmp -p 1024

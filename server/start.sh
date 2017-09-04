#!/bin/bash
#
# NOTE: The paths are paths in the container.

MOUNT_POINT="/host"

# Set the chatscript host address.
sed -i -e 's/^$host = "1.22.08.4"/$host = "localhost"/g' \
  "$MOUNT_POINT/ChatScript-engine/WEBINTERFACE/SPEECH/ui.php"

# Start the server.
nohup caddy -conf "$MOUNT_POINT/server/Caddyfile" > /dev/null 2>&1 \
  > "$MOUNT_POINT/server/caddy.log" &

# Start the chatscript engine.
cd "$MOUNT_POINT/ChatScript-engine" && ./run.sh --users ../users \
  --logs ../logs --topic ../topic --tmp ../tmp -p 1024

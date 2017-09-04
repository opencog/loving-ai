#!/bin/bash

IMAGE_NAME="chatscript"
CONTAINER_NAME="chatscript"
MOUNT_POINT="/host"

help() {
  printf "Pass either 'b' for build, 'r' for run, or 's' for stop.\n"
  exit 1
}

if [ $# -eq 0 ]; then help; fi

case $1 in
  b) docker build -t "$IMAGE_NAME" . ;;
  r) docker stop "$CONTAINER_NAME"
    docker rm -v "$CONTAINER_NAME"
    docker run -d --name "$CONTAINER_NAME" -p 55555:80 \
      -v "$PWD/..":"$MOUNT_POINT" -w "$MOUNT_POINT" -it "$IMAGE_NAME" \
      bash /host/web-server/start.sh
    ;;
  s) docker stop "$CONTAINER_NAME" ;;
  *) help ;;
esac

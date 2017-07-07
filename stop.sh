#!/usr/bin/env bash

if [[ $(tmux ls 2>/dev/null) ]]; then
    tmux kill-session
fi

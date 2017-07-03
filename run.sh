#!/usr/bin/env bash

export LOVING_AI_WORKSPACE=~/loving_ai
export HR_CHARACTER_PATH=$LOVING_AI_WORKSPACE/chatbot-server/characters.yaml
export CHATBOT_SERVER_PORT=8002
export CS_DIR=$LOVING_AI_WORKSPACE/ChatScript-engine
export CS_PORT=1025
export SLACK_BOTNAME=sarah
export SLACKBOT_API_TOKEN=$LOVING_AI_SLACKBOT_API_TOKEN
export SLACKTEST_TOKEN=$LOVING_AI_SLACKTEST_TOKEN

tmux new-session -d -n "Loving AI" "cd $LOVING_AI_WORKSPACE/chatbot-server && python run_server.py -p $CHATBOT_SERVER_PORT -v; $SHELL"
tmux new-window -n "CS" "cd $CS_DIR && ../build.exp rose && ./run.sh -p $CS_PORT; $SHELL"
tmux new-window -n "Slack" "cd $LOVING_AI_WORKSPACE/chatbot-server && python slack_client.py $SLACK_BOTNAME; $SHELL"
tmux attach                                                                     

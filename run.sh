#!/usr/bin/env bash

BASEDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
export BOTNAME=sarah
export SLACK_BOTNAME=sarah
export LOVING_AI_WORKSPACE=$BASEDIR
export HR_CHARACTER_PATH=$LOVING_AI_WORKSPACE/chatbot-server/${BOTNAME}.yaml
export CHATBOT_SERVER_PORT=8002
export CS_DIR=$LOVING_AI_WORKSPACE/ChatScript-engine
export CS_PORT=1025
export SLACKBOT_API_TOKEN=$LOVING_AI_SLACKBOT_API_TOKEN
export SLACKTEST_TOKEN=$LOVING_AI_SLACKTEST_TOKEN
export CHATBOT_LOG_DIR=$HOME/.loving_ai

if [[ ! -d $CS_DIR ]]; then
    git clone git@github.com:hansonrobotics/ChatScript-engine.git $CS_DIR
fi

tmux new-session -d -n "Loving AI" "echo $HR_CHARACTER_PATH && cd $LOVING_AI_WORKSPACE/chatbot-server && python run_server.py -p $CHATBOT_SERVER_PORT -v; $SHELL"
tmux new-window -n "CS" "cd $CS_DIR && ../build.exp Sarah && ./run.sh --users ../users --logs ../logs --topic ../topic --tmp ../tmp -p $CS_PORT; $SHELL"
tmux new-window -n "Slack" "cd $LOVING_AI_WORKSPACE/chatbot-server && python slack_client.py $SLACK_BOTNAME; $SHELL"
tmux attach

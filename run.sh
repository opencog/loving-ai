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
export CHATBOT_LOG_DIR=$HOME/.loving-ai

check_ports() {
    local ports=$@
    local process
    local ret
    for port in ${ports[@]}; do
        process=$(netstat -tuple 2>/dev/null|awk '{print $4 " " $9}'|grep ":$port"|cut -d' ' -f2|cut -d/ -f1|sort -u)
        if [[ ! -z $process ]]; then
            printf "Process $process is using port $port" >&2
            ret=1
        fi
    done
    return $ret
}

check_ports 8002 1025

if [[ ! -d $CS_DIR ]]; then
    git clone git@github.com:hansonrobotics/ChatScript-engine.git $CS_DIR
fi

if [[ $# -eq 1 ]] && [[ "$1" == "expt" ]]; then
  # NOTE: This only works with hansonrobotics robots or their simulations.
  export CS_PORT=1024
  tmux new-window -n "Loving-AI CS" "cd $CS_DIR && ../build.exp Sarah && ./run.sh --users ../users --logs ../logs --topic ../topic --tmp ../tmp -p $CS_PORT; $SHELL"
  tmux new-window -n "Client" "cd $LOVING_AI_WORKSPACE/chatbot-server && python client.py $SLACK_BOTNAME localhost; $SHELL"
else
  tmux new-session -d -n "Loving AI" "echo $HR_CHARACTER_PATH && cd $LOVING_AI_WORKSPACE/chatbot-server && python run_server.py -p $CHATBOT_SERVER_PORT -v; $SHELL"
  tmux new-window -n "CS" "cd $CS_DIR && ../build.exp Sarah && ./run.sh --users ../users --logs ../logs --topic ../topic --tmp ../tmp -p $CS_PORT; $SHELL"
  tmux new-window -n "Slack" "cd $LOVING_AI_WORKSPACE/chatbot-server && python slack_client.py $SLACK_BOTNAME; $SHELL"
  tmux new-window -n "Client" "cd $LOVING_AI_WORKSPACE/chatbot-server && python client.py $SLACK_BOTNAME localhost; $SHELL"
  tmux attach
fi

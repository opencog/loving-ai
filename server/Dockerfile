from ubuntu:14.04

ENV DEBIAN_FRONTEND=noninteractive

run apt-get update && apt-get -y upgrade
run apt-get install -y vim curl tmux php5-fpm
run curl https://getcaddy.com | bash

EXPOSE 2015

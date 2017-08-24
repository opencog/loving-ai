#!/usr/bin/env python

import os
import sys
import logging
import argparse
CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(CWD, 'src'))

from chatbot.client import Client

HR_CHATBOT_AUTHKEY = os.environ.get('HR_CHATBOT_AUTHKEY', 'AAAAB3NzaD')

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARN)

    parser = argparse.ArgumentParser(
        description='Run the chatbot client')
    parser.add_argument(
        'botname', help='Name of the bot')
    parser.add_argument(
        'host', help='Host of the chatbot server')
    args = parser.parse_args()

    client = Client(HR_CHATBOT_AUTHKEY, botname=args.botname, host=args.host)
    client.cmdloop()

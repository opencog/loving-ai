# -*- coding: utf-8 -*-
import socket
import logging
import threading
import re
import subprocess
import os
import shutil
import datetime as dt

from chatbot.server.character import Character, TYPE_CS
from chatbot.client import get_default_username
from chatbot.utils import shorten
from chatbot.server.session import Locker

LOVING_AI_WORKSPACE = os.environ.get('LOVING_AI_WORKSPACE', os.path.expanduser('~/loving_ai'))
CS_DIR = os.path.join(LOVING_AI_WORKSPACE, 'ChatScript-engine')
CS_USERS_DIR = os.environ.get('CS_USERS_DIR', os.path.join(CS_DIR, 'USERS'))
CS_STATE_DIR = os.environ.get('CS_STATE_DIR',
            os.path.expanduser('~/.loving_ai/chatbot/cs_states'))
variable_pattern = re.compile(""".* variable: .*\$(?P<name>\S+) = (?P<value>.*)""")

class CSCharacter(Character):
    def __init__(self, id, name, level, weight, cs_host, cs_port, cs_botname):
        super(CSCharacter, self).__init__(id, name)
        self.languages = ['en']
        self.level = level
        self.weight = weight
        self.host = cs_host
        self.port = cs_port
        self.cs_botname = cs_botname
        self.dynamic_level = True
        self.non_repeat = True
        self.response_limit = 512
        self.type = TYPE_CS
        self._locker = Locker()

    def _threadsafe(f):
        def wrap(self, *args, **kwargs):
            self._locker.lock()
            try:
                return f(self, *args, **kwargs)
            finally:
                self._locker.unlock()
        return wrap

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    @_threadsafe
    def say(self, username, question):
        to_say = "{username}\0{botname}\0{question}\0".format(
            username=username, botname='', question=question)
        response =  ""
        connection = None
        try:
            connection = socket.create_connection((self.host, self.port), timeout=2)
            self.logger.info("Say {}".format(to_say))
            ret = connection.sendall(to_say)
            try:
                while True:
                    chunk = connection.recv(4096)
                    if chunk:
                        response += chunk
                    else:
                        break
            except socket.timeout as e:
                self.logger.error("Timeout {}".format(e))
                self.kill_server()
                raise e
        except Exception as ex:
            self.logger.error("Connection error {}".format(ex))
        finally:
            if connection is not None:
                connection.close()

        if 'No such bot' in response:
            self.logger.error(response)
            response = ''
        return response

    def is_command(self, question):
        return question.startswith(':')

    def get_csuser(self, session):
        if session is None:
            user = '.'
        else:
            if session.test:
                user = 'test'
            else:
                user = session.sid
        return user

    def respond(self, question, lang, session, query, request_id, *args, **kwargs):
        ret = {}
        ret['botid'] = self.id
        ret['botname'] = self.name
        sid = self.get_csuser(session)
        if lang not in self.languages:
            ret['text'] = ''
        else:
            state_snapshot = os.path.join(CS_STATE_DIR, '{}/{}.txt'.format(
                sid, request_id))
            if not session.test:
                self.save_state(session, state_snapshot)
            answer = self.say(sid, question)
            if not answer:
                ret['trace'] = 'Not responsive'

            answer, res = shorten(answer, self.response_limit)
            trace = self.say(sid, ':why')

            if self.non_repeat and session and answer:
                if not session.check(question, answer):
                    ret['repeat'] = answer
                    ret['trace'] = trace
                    answer = ''
                    self.logger.warn("Repeat answer")

            if session and res:
                self.set_context(session, {'continue': res})
                self.logger.info("Set continue={}".format(res))

            if self.is_command(question):
                if question == ':reset':
                    ret['text'] = 'Hi there'
                else:
                    ret['text'] = ''
            else:
                ret['text'] = answer

            if answer:
                ret['trace'] = trace
                ret['quibble'] = 'xquibble_' in trace or 'keywordlessquibbles' in trace
                ret['gambit'] = 'gambit' in trace
                ret['repeat_input'] = 'repeatinput' in trace
                if not ret['quibble'] and not ret['repeat_input']:
                    ret['ok_match'] = True
                if ret['repeat_input']:
                    ret['bad'] = 'repeatinput' in trace

        return ret

    def refresh(self, session):
        sid = self.get_csuser(session)
        self.say(sid, ':reset')
        self.logger.info("Character is refreshed")

    def rebuild(self):
        response = self.say('.', ':build {}'.format(self.cs_botname))
        self.logger.info("Character is rebuilt")
        return response

    def kill_server(self):
        out = subprocess.check_output(['ps', '-ef'])
        for l in out.splitlines():
            if 'ChatScript' in l:
                pid = int(l.split()[1])
                os.kill(pid, 9)
                self.logger.info("Killed ChatScript server pid {}".format(pid))

    def get_context(self, session):
        sid = self.get_csuser(session)
        response = self.say(sid, ':variables')
        context = {}
        names = ['firstname', 'fullname']
        for line in response.splitlines():
            matchobj = variable_pattern.match(line)
            if matchobj:
                name, value =  matchobj.groups()
                if name in names:
                    context[name] = value.replace('_', ' ')
        if 'firstname' in context or 'fullname' in context:
            context['name'] = context.get('firstname') or context.get('fullname')
        return context

    def set_context(self, session, context):
        assert isinstance(context, dict), "Context must be dict"
        sid = self.get_csuser(session)
        c = {}
        names = ['firstname', 'fullname', 'name']
        for name in names:
            if name in context:
                c[name] = context[name]
        if 'location' in context:
            c['here'] = context['location']
        if 'name' in context:
            c['firstname'] = context['name']
            c['fullname'] = context['name']
            c['name'] = context['name']
        for k, v in c.iteritems():
            v = ' '.join(v.split()).replace(' ', '_') # variables in CS use _ instead of space
            response = self.say(sid, ':do ${}={}'.format(k, v))
            self.logger.info("Set {}={}".format(k, v))

    def get_state_filename(self, session):
        if session is None:
            self.logger.error("Session is not set")
            return
        sid = self.get_csuser(session)
        fname = 'topic_{}_{}.txt'.format(sid, self.cs_botname)
        fname = os.path.join(CS_USERS_DIR, fname)
        return fname

    def save_state(self, session, state_fname):
        topic_fname = self.get_state_filename(session)
        if os.path.isfile(topic_fname):
            state_dir = os.path.dirname(state_fname)
            if state_dir and not os.path.isdir(state_dir):
                os.makedirs(state_dir)
            shutil.copy(topic_fname, state_fname)
            self.logger.info("State is saved to {}".format(state_fname))
            return True
        else:
            self.logger.warn("No state to save")
            return False

    def load_state(self, session, state_fname):
        topic_fname = self.get_state_filename(session)
        if os.path.isfile(state_fname):
            if os.path.isfile(topic_fname):
                shutil.copy(topic_fname, '{}.bak'.format(os.path.splitext(topic_fname)[0]))
            shutil.copy(state_fname, topic_fname)
            self.logger.info("State is recovered by {}".format(state_fname))
            return True
        else:
            self.logger.error("No state to load")
            return False

if __name__ == '__main__':
    from chatbot.server.session import Session
    s = Session('id')
    c = CSCharacter('id', 'name', 1, 1, 'localhost', '2048', 'Sarah')
    answer = c.respond('make sense', 'en', s, False, '1')
    print answer

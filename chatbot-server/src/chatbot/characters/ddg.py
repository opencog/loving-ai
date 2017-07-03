# -*- coding: utf-8 -*-
import requests
import logging
import re
from chatbot.server.character import DefaultCharacter
from chatbot.utils import shorten, check_online
import datetime as dt

class DDG(DefaultCharacter):
    def __init__(self, id, name, level, weight):
        super(DDG, self).__init__(id, name)
        self.level = level
        self.weight = weight
        self.languages = ['en']
        self.non_repeat = True
        self.response_limit = 512
        self.keywords = "what is,what's,what are,what're,who is,who's,who are,who're,where is,where's,where are,where're".split(',')
        self.online = True
        self.last_check_time = None

    def ask(self, question):
        try:
            response = requests.get('http://api.duckduckgo.com', params={'q': question, 'format': 'json'}, timeout=1)
        except:
            self.online = check_online('duckduckgo.com')
            return ''
        json = response.json()
        if json['AnswerType'] not in ['calc']:
            return json['Abstract'] or json['Answer']
        else:
            return ''

    def is_favorite(self, question):
        question = question.strip()
        return all(question != k.strip() for k in self.keywords) and \
            any(question.startswith(k.strip()) for k in self.keywords) and \
            all(word not in question.split() for word in 'I,i,me,my,mine,we,us,our,ours,you,your,yours,he,him,his,she,her,hers,it,its,they,them,their,theirs,time,date,weather,day,this,that,those,these'.split(','))

    def respond(self, question, lang, session=None, *args, **kwargs):
        ret = {}
        ret['botid'] = self.id
        ret['botname'] = self.name
        ret['text'] = ''
        if lang not in self.languages:
            return ret
        elif re.search(r'\[.*\]', question):
            return ret

        if self.last_check_time is None or (dt.datetime.now()-self.last_check_time).total_seconds() > 60:
            self.last_check_time = dt.datetime.now()
            self.online = check_online('duckduckgo.com')

        if self.online:
            if self.is_favorite(question.lower()):
                answer = self.ask(question)
                answer, res = shorten(answer, self.response_limit)

                if self.non_repeat and session and answer:
                    if not session.check(question, answer):
                        ret['repeat'] = answer
                        answer = ''
                        self.logger.warn("Repeat answer")

                if res and session is not None:
                    self.set_context(session, {'continue': res})
                    self.logger.info("Set continue={}".format(res))

                ret['text'] = answer
            else:
                ret['trace'] = "Can't answer"
        else:
            ret['trace'] = "Offline"
        return ret

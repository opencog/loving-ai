import socket
import unittest
import subprocess
import os
import atexit
import time
import shutil

CWD = os.path.dirname(os.path.abspath(__file__))

username='test'
host='localhost'
port=2049
users='/tmp/cs_users'
tmp='/tmp/cs_tmp'
logs='/tmp/cs_logs'
topic='/tmp/cs_topic'

for d in [users, tmp, logs, topic]:
    if not os.path.isdir(d):
        os.makedirs(d)

CS_DIR=os.environ.get('CS_DIR', '')
proc = subprocess.Popen(
    ['./LinuxChatScript64',
        'port={}'.format(port),
        'users={}'.format(users),
        'logs={}'.format(logs),
        'tmp={}'.format(tmp),
        'topic={}'.format(topic)
    ], cwd=os.path.join(CS_DIR, 'BINARIES'),
    preexec_fn=os.setsid)
time.sleep(4)

def shutdown():
    if proc:
        os.killpg(proc.pid, 2)
    for d in [users, tmp, logs, topic]:
        if os.path.isdir(d):
            shutil.rmtree(d)
atexit.register(shutdown)

def say(message):
    to_say = "{username}\0{botname}\0{message}\0".format(
        username=username, botname='', message=message)
    try:
        connection = socket.create_connection((host, port))
    except Exception as ex:
        return ''
    connection.send(to_say)
    response =  ""
    while True:
        chunk = connection.recv(100)
        if chunk:
            response += chunk
        else:
            break
    return response


class ChatScriptTest(unittest.TestCase):

    def test(self):
        response = say(':build 0')
        self.assertTrue('Finished compile' in response)
        response = say(':build rose')
        self.assertTrue('Finished compile' in response)
        if 'ERROR' in response:
            self.assertTrue(
                False, response[response.index('ERROR'):
                                response.index('Finished compile')])

        response = say('what is your name')
        self.assertTrue('Sarah' in response)

if __name__ == '__main__':
    unittest.main()

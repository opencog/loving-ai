import socket
import unittest
import subprocess
import os
import atexit
import time

CWD = os.path.dirname(os.path.abspath(__file__))

username='test'
host='localhost'
port=2049

CS_DIR=os.environ.get('CS_DIR', '')
proc = subprocess.Popen(
    ['./LinuxChatScript64', 'port={}'.format(port)], cwd=os.path.join(CS_DIR, 'BINARIES'),
    preexec_fn=os.setsid)
time.sleep(4)

def shutdown():
    if proc:
        os.killpg(proc.pid, 2)
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

    def test_sophia(self):
        response = say(':build rose')
        self.assertTrue('Finished compile' in response)
        if 'ERROR' in response:
            self.assertTrue(
                False, response[response.index('ERROR'):
                                response.index('Finished compile')])

        response = say('what is your name')
        self.assertTrue('Sophia' in response)

if __name__ == '__main__':
    unittest.main()

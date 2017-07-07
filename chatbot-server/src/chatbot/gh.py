import threading
from flask import request
from chatbot.server.chatbot_agent import rebuild_cs_character
import logging
from pprint import pformat
import os
import subprocess
logger = logging.getLogger('hr.chatbot.ext.gh')

revision = None

BOTNAME = os.environ.get('BOTNAME', None)

def update_repo(name, branch, workspace=None):
    if workspace is None:
        workspace = os.environ.get('LOVING_AI_WORKSPACE', None)
    global revision
    if workspace:
        cwd = workspace
        cmd = ['git', 'pull', 'origin', branch]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        logger.info('Updating {} repository'.format(name))
        proc.wait()
        try:
            revision = subprocess.check_output('git log -1 --format="%h"', shell=True, cwd=cwd).strip()
        except Exception as ex:
            logger.error(ex)
        return True
    else:
        logger.error("Can't find workspace, skipping repo updating")
        return False

def test_repo(repo, branch):
    if repo == 'loving-ai':
        workspace=os.path.expanduser('~/.loving-ai/test_ws')
        if not os.path.isdir(workspace):
            logger.error("Workspace {} doesn't exist".format(workspace))
            return False
        try:
            update_repo(repo, branch, workspace=workspace)
            cmd = ['python', 'test.py']
            cwd = os.path.join(workspace, 'test')
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            stdout, stderr = proc.communicate()
            if 'OK' not in stderr:
                logger.error("Test failed: {}".format(stderr))
                return False
            return True
        except Exception as ex:
            logger.error(ex)
    return False

def check_trigger_rebuild(json):
    should_rebuild = False
    branch = 'master'
    if 'ref' in json and json['ref'] == 'refs/heads/{}'.format(branch):
        if 'commits' in json:
            commits = json['commits']
            for commit in commits:
                added = commit['added']
                removed = commit['removed']
                modified = commit['modified']
                for f in added + removed + modified:
                    prefix, suffix = os.path.splitext(f)
                    if suffix == '.top':
                        should_rebuild = True
        if json['forced']:
            should_rebuild = True

    if should_rebuild and test_repo('loving-ai', branch) and update_repo('loving-ai', branch):
        threading.Thread(target=rebuild_cs_character, kwargs={'revision': revision, 'botname': BOTNAME}).start()
        return True
    return False

def _postreceive():
    if request.json['repository']['full_name'] == 'opencog/loving-ai':
        logger.info('Request {}'.format(pformat(request.json, indent=4)))
        if check_trigger_rebuild(request.json):
            return ('Trigger rebuilding', 202)
        else:
            return ('Echo', 202)

def load(app, root):
    logger.info('Loading postreceive rule')
    app.add_url_rule(root + '/postreceive', None, _postreceive, methods=['POST'])

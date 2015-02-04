GITHUB_API = 'https://api.github.com'

import json
import getpass
from urlparse import urljoin

import requests


class Authenticate:
    def __init__(self):
        pass

    def doAuthenticate(self):
        username = raw_input('Github username: ')
        #print username
        password = getpass.getpass("Github password: ")
        note = raw_input('Note (optional): ')
        url = urljoin(GITHUB_API, 'user')
        #print url
        payload = {}
        if note:
            payload['note']=note
        res = requests.post(url, auth = (username, password), data=json.dumps(payload))
        #print res
        #print res.text
        #print res.status_code
        j = json.loads(res.text)
        if res.status_code >= 400:
            msg = j.get('message', ' UNDEFINED ERROR (no error description from server)')
            print 'ERROR: %s' % msg
            return
        return(username,password)

    def check_authentication(self, username, password, note):
        # url = urljoin(GITHUB_API, 'user')
        # payload = {}
        # if note:
        #     payload['note']=note
        # res = requests.post(url, auth = (username, password), data=json.dumps(payload))
        # j = json.loads(res.text)
        # if res.status_code >= 400:
        #     msg = j.get('message', ' UNDEFINED ERROR (no error description from server)')
        #     print 'ERROR: %s' % msg
        #     return False
        # return True
        #
        # Compose Request
        #
        url = urljoin(GITHUB_API, 'user')
        payload = {}
        if note:
            payload['note'] = note
        res = requests.post(
            url,
            auth = (username, password),
            data = json.dumps(payload),
            )
        #
        # Parse Response
        #
        j = json.loads(res.text)
        print j
        if res.status_code >= 400:
            msg = j.get('message', 'UNDEFINED ERROR (no error description from server)')
            print 'ERRORs: %s' % msg
            return False
        else:
            print "test"
            token = j['token']
            print 'New token: %s' % token
            return token
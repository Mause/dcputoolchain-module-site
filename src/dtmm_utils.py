#!/usr/bin/env python
#
# Copyright 2012 Dominic May
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
contains some functions
required by both main.py and humans.py
"""
# this could be dangerous D:
from __future__ import division

# generic imports
import re
import os
import json
import urllib
import base64
import hashlib
import logging

# lua interpreter functions
from slpp import slpp as lua

# google appengine imports
import webapp2
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

# for debugging exceptions
import traceback
import sys

# authentication data
client_auth_data = memcache.get('client_auth_data')
if not client_auth_data:
    with open('auth_data.json', 'r') as fh:
        auth_data = json.loads(fh.read())
        client_auth_data = auth_data["client_auth_data"]


def get_hardware_data(handler, fragment):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    module = get_url_content(handler, fragment['url'])
    assert 'content' in module
    file_data = base64.b64decode(
        module['content'])
    hardware_data = (
        re.search('HARDWARE\s*=\s*(?P<data>\{[^}]*\})',
                  file_data))
    if hardware_data:
        hardware_data = lua.decode(hardware_data.groupdict()['data'])
        return hardware_data
    else:
        return {}


def get_module_data(handler, fragment):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    module = get_url_content(handler, fragment['url'])
    assert 'content' in module, 'The key "content" was not found in %s' % module
    file_data = base64.b64decode(module['content'])
    module_data = (
        re.search('MODULE\s*=\s*(?P<data>\{[^}]*\})',
                  file_data))
    if module_data:
        module_data = lua.decode(module_data.groupdict()['data'])
        return module_data
    else:
        return {}


def get_tree(handler=None):
    """this is a hard coded version of the get_url_content function
    but with extra features"""
    result = memcache.get('tree')
    if result != None:
        logging.info('Memcache get successful; got the repo tree')
    else:
        logging.info('Getting the result from the GitHub API')
        try:
            url_data = authed_fetch(url='https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').content
        except urlfetch.DownloadError:
            logging.info('Fetching the github api tree failed. Try try again')
            handler.error(408)
            return None
        else:
            result = json.loads(url_data)
            memcache.set('tree', result)
    # check if the api limit has been reached
    assert result
    assert not result.get('message', '').startswith('API Rate Limit Exceeded for'), 'API Limit reached'
    assert 'tree' in result
    assert result['tree']
    return result['tree']


def get_url_content(handler, url):
    "this is a caching function, to help keep wait time short"
    url_hash = hashlib.md5(str(url)).hexdigest()
    result = memcache.get(str(url_hash))
    if result != None:
        logging.info('Memcache get successful; %.40s' % result)
    else:
        logging.info('Getting the result from the GitHub API')
        try:
            r = authed_fetch(url)
            url_data = r.content
        except urlfetch.DownloadError:
            logging.info('Fetching "%s" failed with a download error' % url)
            handler.error(408)
            return
        else:
            result = json.loads(url_data)
            memcache.set(str(url_hash), result)
    # check if the api limit has been reached
    assert not result.get('message', '').startswith('API Rate Limit Exceeded for'), 'API Limit reached'
    return result


def dorender(handler, tname='base.html', values=None, write=True):
    """automates some stuff so we dont have to type
    it in everytime we want to use a template"""
    handler.response.headers['content-type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if write:
        handler.response.out.write(template.render(path, values or {}))
    else:
        return template.render(path, values or {})


def authed_fetch(url, headers={}):
    headers.update({'X-Admin-Contact': 'admin@lysdev.com'})
    url += '?' + urllib.urlencode(client_auth_data)
    r = urlfetch.fetch(url=url, headers=headers)
    if 'x-ratelimit-remaining' in r.headers.keys():
        logging.info('%s requests remaining for this hour.' % (r.headers['x-ratelimit-remaining']))
    else:
        logging.info('Could not determine how many requests are remaining for this hour')
        logging.info(r.content)
    return r


# this function is no longer used, as it is no longer required
# def get_oauth_token(all_data=False):
#     token = memcache.get('oauth_token')
#     if token:
#         return token
#     else:
#         if not os.path.exists('auth_frag.txt'):
#             raise Exception('No authentication fragment found. Run the gen_auth file to generate it')
#         with open('auth_frag.txt', 'r') as fh:
#             auth_frag = fh.read()
#         # use the next line to configure to a new github account
#         r = None
#         count = 0
#         while not r and count != 15:
#             try:
#                 r = urlfetch.fetch(
#                     url='https://api.github.com/authorizations',
#                     payload=json.dumps({
#                         'scopes': ["repo"],
#                         'note': 'DCPUToolchain'}),
#                     method=urlfetch.POST,
#                     headers={
#                         'Content-Type': 'application/json',
#                         "Authorization": "Basic " + auth_frag}
#                     )
#             except apiproxy_errors.ApplicationError:
#                 count += 1
#                 logging.info('Try try again for the oauth token. %s tries' % count)
#         if count > 14:
#             logging.info('More than fifteen tries. Aborting')
#             return
#         else:
#             if 200 <= r.status_code < 300:
#                 token = json.loads(r.content)['token']
#                 memcache.set('oauth_token', token)
#                 return token


class FourOhFourErrorLog(db.Model):
    module = db.StringProperty(required=True)
    address = db.StringProperty(required=True)
    datetimer = db.DateTimeProperty(auto_now=True)


class BaseRequestHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        if not development():
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error(lines)
            template_values = {}
            template_values['traceback'] = lines.replace('\n', '<br/>')
            mail.send_mail(
                sender='debugging@dcputoolchain-module-site.appspotmail.com',
                to="jack.thatch@gmail.com",
                subject='Caught Exception',
                body=lines,
                html=dorender(self, 'error.html', template_values, write=False))
            if users.is_current_user_admin():
                raise exception
            else:
                self.error(500)
                if isinstance(exception, AssertionError):
                    dorender(self, 'unexpected_result.html', {})
        else:
            super(BaseRequestHandler, self).handle_exception(exception, debug_mode)


def development():
    # return not False
    # return False
    if os.environ['SERVER_SOFTWARE'].find('Development') == 0:
        return True
    else:
        return False

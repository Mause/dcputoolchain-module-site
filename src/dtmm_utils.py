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
from __future__ import (
    division,
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement
)

import os
import json
import urllib
import base64
import hashlib
import logging
from operator import itemgetter

# google appengine imports
import webapp2
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

# for debugging exceptions
import sys
import traceback

# application specific
from module_utils import get_hardware_data, get_module_data

# authentication data
client_auth_data = memcache.get('client_auth_data')
if not client_auth_data:
    with open('auth_data.json', 'r') as fh:
        auth_data = json.load(fh)
        client_auth_data = auth_data["client_auth_data"]


def _get_live_data(handler, fragment):
    """
    get_url_content's fragment['url'], b64decode's module['content']
    """
    module = get_url_content(handler, fragment['url'])
    assert 'content' in module

    return base64.b64decode(module['content'])


def get_live_hardware_data(handler, fragment):
    """
    Given a get_tree fragment,
    returns hardware data in a python dict
    """
    return get_hardware_data(_get_live_data(handler, fragment))


def get_live_module_data(handler, fragment):
    """
    Given a get_tree fragment,
    returns module data in a python dict
    """
    return get_module_data(_get_live_data(handler, fragment))


def get_tree(handler=None):
    """
    Returns the file hierarchy/tree
    """

    result = get_url_content(handler, 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')

    assert result['tree'], result
    return result['tree']


def get_modules(handler=None):
    """
    Returns the file hierarchy/tree, filtered by a .lua extension
    """
    tree = get_tree(handler)

    return [
        fragment
        for fragment in tree
        if fragment['path'].endswith('.lua')
    ]


def get_module_names(handler):
    """
    Returns list containing the path attributes of all modules
    """

    modules = get_modules(handler)
    modules = map(itemgetter('path'), modules)
    return map(rpart, modules)


def get_url_content(handler, url):
    """
    A wrapper around authed_fetch_json, caches results to help keep wait time short
    """

    url_hash = hashlib.md5(url).hexdigest()
    result = memcache.get(url_hash)

    if result is None:
        logging.info('Getting the result from the GitHub API')

        try:
            result = authed_fetch_json(url)
        except urlfetch.DownloadError as e:
            logging.info('Fetching "{}" failed with a {}'.format(url, e))
            handler.error(408)
            return
        else:
            memcache.set(url_hash, result)

    else:
        logging.info('Memcache get successful; %.40s' % result)
    # check if the api limit has been reached
    assert not result.get('message', '').startswith(
        'API Rate Limit Exceeded for'), 'API Limit reached'
    return result


def authed_fetch(url, headers=None):
    # add admin contact, auth_data
    headers = headers or {}
    headers.update({'X-Admin-Contact': 'admin@lysdev.com'})

    # build the url
    url += '&' if '?' in url else '?'
    url += urllib.urlencode(client_auth_data)

    r = urlfetch.fetch(url=url, headers=headers)

    remaining = r.headers.get('x-ratelimit-remaining')
    if remaining:
        logging.info('{} requests remaining for this hour.'.format(remaining))
    else:
        logging.info(
            'Could not determine number of requests remaining for this hour')
        logging.info(r.content)

    return r


def authed_fetch_json(*args, **kwargs):
    """
    parse json output from proxied authed_fetch
    """
    return json.load(authed_fetch(*args, **kwargs).raw)


class BaseRequestHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        if development():
            return super(BaseRequestHandler, self).handle_exception(exception, debug_mode)

        lines = ''.join(traceback.format_exception(*sys.exc_info()))
        logging.error(lines)
        template_values = {
            'traceback': lines.replace('\n', '<br/>')
        }
        html = self.dorender('error.html', template_values, write=False)
        mail.send_mail(
            sender='debugging@dcputoolchain-module-site.appspotmail.com',
            to="jack.thatch@gmail.com",
            subject='Caught Exception',
            body=lines,
            html=html)
        if users.is_current_user_admin():
            raise exception
        else:
            self.error(500)
            if isinstance(exception, AssertionError):
                self.dorender('unexpected_result.html', {})

    def dorender(self, tname='base.html', values=None, write=True):
        """
        automates some stuff so we dont have to type
        it in everytime we want to use a template
        """

        self.response.headers['content-type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates/' + tname)

        data = template.render(path, values or {})

        if write:
            self.response.out.write(data)


def development():
    return os.environ['SERVER_SOFTWARE'].find('Development') == 0


def rpart(path):
    return path.rpartition('/')[-1]

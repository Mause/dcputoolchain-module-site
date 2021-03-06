# The MIT License (MIT)

# Copyright (c) 2013 Dominic May

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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


def _get_tree(handler=None):
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
    tree = _get_tree(handler)

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

    url_hash = md5_hash(url)
    result = memcache.get(url_hash)

    if result is None:
        logging.info('Getting the result from the GitHub API')

        try:
            result = authed_fetch_json(url)
        except urlfetch.DownloadError as e:
            logging.error(e)
            handler.error(408)
            return []
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
        memcache.set('requests_remaining', int(remaining))
    else:
        logging.info(
            'Could not determine number of requests remaining for this hour')
        logging.info(r.content)

    return r


def authed_fetch_json(*args, **kwargs):
    """
    parse json output from proxied authed_fetch
    """
    return json.loads(authed_fetch(*args, **kwargs).content)


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

        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates/' + tname)

        data = template.render(path, values or {})

        if write:
            self.response.out.write(data)
        else:
            return data


def development():
    return os.environ['SERVER_SOFTWARE'].find('Development') == 0


def rpart(path):
    return path.rpartition('/')[-1]


def md5_hash(string):
    return hashlib.md5(string).hexdigest()

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import base64
import hashlib
import urllib2
# import requests
import logging

# lua interpreter functions
from slpp import slpp as lua

# google appengine imports
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template


# timeout for urlopen functions
TIMEOUT = 10


def get_hardware_data(handler, fragment):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    file_data = base64.b64decode(
        get_url_content(handler,
            fragment['url'])['content'])
    hardware_data = (
        re.search('HARDWARE\s*=\s*\{([^}]*)\}',
                  file_data))
    try:
        hardware_data = hardware_data.group(0)
        hardware_data = hardware_data.strip('HARDWARE=')
        hardware_data = hardware_data.strip('HARDWARE =')
        hardware_data = lua.decode(hardware_data)
    except AttributeError:
        logging.info('hardware_data: ' + str(hardware_data))
    new_output = {}
    new_output['Version'] = '0' + str(hardware_data[1])
    new_output['ID'] = '0' + str(hardware_data[3])
    new_output['Manufacturer'] = '0' + str(hardware_data[5])
    return new_output


def get_module_data(handler, fragment):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    file_data = base64.b64decode(
        get_url_content(handler,
            fragment['url'])['content'])
    module_data = (
        re.search('MODULE\s*=\s*(\{([^}]*)\})',
                  file_data))
    try:
        module_data = module_data.group(0)
        module_data = module_data.strip('MODULE=')
        module_data = module_data.strip('MODULE =')
        module_data = lua.decode(module_data)
    except AttributeError:
        logging.info('module_data: ' + str(module_data))
    return module_data


def get_tree(handler=None):
    def path_frag(x):
        return str(x).split('/')[-1]
    """this is a hard coded version of the get_url_content function
    but with extra features"""
    url = 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master'
    result = None
    result = memcache.get('tree')
    if result != None:
        logging.info('Memcache get successful; got the repo tree')
    else:
        logging.info('Getting the result from the GitHub API')

        try:
            r = urlfetch.fetch(url=url, headers={'Authorization': 'token %s' % (get_oauth_token())})
            if 'x-ratelimit-remaining' in r.headers.keys():
                logging.info('%s requests remaining for this hour.' % (r.headers['x-ratelimit-remaining']))
            else:
                logging.info('Could not determine how many requests are remaining for this hour')
            url_data = r.content
            # url_data = urllib2.urlopen(url, timeout=TIMEOUT).read()
        except urllib2.URLError:
            handler.error(408)
            return
        result = json.loads(url_data)
        memcache.set('tree', result)
    logging.info('Okay, done the main part of the get_tree function')
    # okay, the tree is special,
    # so we have to do some special stuff to it :P
    # like, caching individual blobs :D
    items = []
    for item in items:
        cur_item = memcache.get(path_frag(item['path']))
        if cur_item == None or cur_item != item['url']:
            if type(cur_item) == list:
                cur_item.append(item['url'])
                memcache.set(path_frag(item['path']),
                             item['url'])
            else:
                memcache.set(path_frag(item['path']),
                             item['url'])
    return result['tree']


def get_url_content(handler, url):
    "this is a caching function, to help keep wait time short"
    result = None
    url_hash = hashlib.md5(str(url)).hexdigest()
    result = memcache.get(str(url_hash))
    if result != None:
        logging.debug('Memcache get successful')
        return result
    else:
        logging.info('Getting the result from the GitHub API')
        try:
            url_data = urllib2.urlopen(url, timeout=TIMEOUT).read()
        except urllib2.URLError:
            handler.error(408)
            return
        else:
            result = json.loads(url_data)
            memcache.set(str(url_hash), result)
            return result


def dorender(handler, tname='base.html', values=None):
    """automates some stuff so we dont have to type
    it in everytime we want to use a template"""
    handler.response.headers['content-type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(path):
        return False
    if values != None:
        handler.response.out.write(template.render(path, values))
    else:
        handler.response.out.write(template.render(path, {}))
    return True


def get_oauth_token(all_data=False):
    token = memcache.get('oauth_token')
    if token:
        return token
    else:
        with open('auth_frag.txt', 'r') as fh:
            auth_frag = fh.read()
        # use the next line to configure to a new github account
        # auth_frag = base64.urlsafe_b64encode("%s:%s" % ('user', 'pass'))

        header = {
            'content-type': 'application/json',
            "Authorization": "Basic " + auth_frag
        }

        r = urlfetch.fetch(
            url='https://api.github.com/authorizations',
            payload=json.dumps({
                'scopes': ["repo"],
                'note': 'DCPUToolchain'}),
            method=urlfetch.POST,
            headers=header)

        # r = requests.post(
        #     'https://api.github.com/authorizations',
        #     data=json.dumps({
        #         'scopes': ["repo"],
        #         'note': 'DCPUToolchain'
        #     }),
        #     headers=header)
        if 200 <= r.status_code < 300:
            token = json.loads(r.content)['token']
            memcache.set('oauth_token', token)
            return token


class FourOhFourErrorLog(db.Model):
    address = db.StringProperty(required=True)
    requested_module = db.StringProperty(required=True)
    datetimer = db.DateTimeProperty(auto_now=True)

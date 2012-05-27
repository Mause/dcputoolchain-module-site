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
import webapp2
#import sqlite3
import datetime
import hashlib
import urllib
import base64
import json
import logging
from mailer import sendmail
from google.appengine.api import memcache

# this is a caching function, to help keep wait time short
def get_url_content(url):
    result = None   
    url_hash = hashlib.md5(str(url)).hexdigest()
    try:
        result = memcache.get(str(url_hash))
        if result != None:
            logging.debug('Memcache get successful')
    except:
        logging.debug('"content" memcache get excepted')
    if result == None:
        x=None
        result = json.loads(urllib.urlopen(url).read())
        memcache.add(str(url_hash), result, 3600)
        return result
    else:
        return result



class HomeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('''
<h3>Search the available modules</h3>
<form action="/modules/search">
<input name="q"/>
<input type="submit"/>
</form>''')


class SearchModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
#        data = json.loads(urllib.urlopen('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').read())
        data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        tree = [str(x['path'].split('/')[-1])+'\n' for x in data['tree'] if x['path'].endswith('.lua') and self.request.get('q') in x['path'].split('/')[-1]]
        logging.info('tree:' + str(tree))
        for filename in tree:
            self.response.out.write(filename)


class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
#        data = json.loads(urllib.urlopen('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').read())
        data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        for x in data['tree']:
            if x['path'].split('/')[-1] == self.request.get('name'):
                #self.response.out.write(base64.b64decode(json.loads(urllib.urlopen(x['url']).read())['content']))
                self.response.out.write(base64.b64decode(
                    get_url_content(x['url'])['content']))


class ListModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        #data = json.loads(urllib.urlopen('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').read())
        data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        tree = [str(x['path'].split('/')[-1])+'\n' for x in data['tree'] if x['path'].endswith('.lua')]
        for filename in tree:
            self.response.out.write(filename)


def flusher(handler):
    try:
        memcache.flush_all()
        handler.response.out.write('<strong>Memcache should have just been flushed</strong>')
    except:
        handler.response.out.write('<strong>Memcache could not be flushed. Contact the <a href="mailto:jack.thatch@gmail.com">administrator</a></strong>')


class SmartFlushHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('The Smart Flusher Handler can be reached at this address')
    def post(self):
#        flusher(self)
        




class FlushHandler(webapp2.RequestHandler):
    def get(self):
        flusher(self)
    def post(self):
        flusher(self)


app = webapp2.WSGIApplication([
    ('/modules/search*', SearchModulesHandler),
    ('/modules/download*', DownloadModulesHandler),
    ('/modules/list', ListModulesHandler),
   # ('/flush', FlushHandler),
    ('/flush', SmartFlushHandler),
   # ('/smart_flush', SmartFlushHandler),
    ('/', HomeHandler)
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8010')

if __name__ == '__main__':
    main()


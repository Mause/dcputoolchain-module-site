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
        memcache.set(str(url_hash), result, 3600)
        return result
    else:
        return result





def get_tree():
    url = 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master'
    result = None
    key = 'tree'
    try:
        result = memcache.get(str(key))
        if result != None:
            logging.debug('Memcache get successful; got the repo tree')
    except: #10
        logging.debug('tree memcache get excepted')
    if result == None:
        x=None
        result = json.loads(urllib.urlopen(url).read())
        memcache.set(str(key), result, 86400)
    # okay, the tree is special,
    # so we have to do some special stuff to it :P
    tree = result['tree']
    items = [item for item in tree if item['type'] == 'blob']
    tobesent = {}
    for item in items:
        #cur_item = item['url']
        cur_item = memcache.get(str(item['path']).split('/')[-1])
        #if cur_item == None:
         #   for item in 
        logging.info('Trying to get this: '+str(str(item['path']).split('/')[-1]))
        if cur_item == None or cur_item != item['url']:
            if type(cur_item) == list:
                cur_item.append(item['url'])
                memcache.set(str(item['path']).split('/')[-1], item['url'], 86400)
            else:
                memcache.set(str(item['path']).split('/')[-1], item['url'], 86400)
            tobesent[str(item['path']).split('/')[-1]] = item['url']
    #if tobesent != {}: sendmail('Dict of values \n\n'+str(tobesent))
    return result['tree']




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
        self.response.headers['Cache-Control'] = 'no-Cache'
#        data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        data = get_tree()
        tree = []
        for x in data:
            if x['path'].endswith('.lua') and self.request.get('q') in x['path'].split('/')[-1]:
                tree.append(str(x['path'].split('/')[-1])+'\n')
        for filename in tree:
            self.response.out.write(filename)


class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        #data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        data = get_tree()
        for x in data:
            if x['path'].split('/')[-1] == self.request.get('name'):
                #self.response.out.write(base64.b64decode(json.loads(urllib.urlopen(x['url']).read())['content']))
                self.response.out.write(base64.b64decode(
                    get_url_content(x['url'])['content']))


class ListModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        #data = get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')
        data = get_tree()
        tree = [str(x['path'].split('/')[-1])+'\n' for x in data if x['path'].endswith('.lua')]
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
        #sendmail('STFU i can hear you!')
    def post(self):
        #logging.info('#############################################################################')
        #logging.info('Okay, the hook seems to have worked :D')
        #logging.info('#############################################################################')
        payload = self.request.get('payload')
        #logging.info('This:'+str(payload))
        payload = json.loads(payload)
        files_changed=False
        changed_files = []
        info_dict = {}
        for commit in payload['commits']:
            changed_files += commit['modified']
            try:
                changed_files += commit['removed']
            except:
                pass
        for file in changed_files:
            info_dict[str(file)] = False
        if len(changed_files) != 0 and changed_files != []:
            files_changed=True
            for file in changed_files:
                logging.info('type: '+str(file))
                if file != None and file != '':
                    assert file != None
                    assert file != ''
                    assert file != {}
                    assert file != []
                    assert file != ()
                    logging.info(file+':'+str(memcache.get(file)))
                    if memcache.get(file) != None: memcache.delete(memcache.get(file))####################################################################################################################################
                    memcache.delete(file)
                    try:
                        info_dict[str(file)] = True
                    except:
                        pass
            sendmail('Here is a list \n\n'+str(changed_files)+'\n\n\n\n\n\n\n'+str(info_dict))

        removed_files = []        
        for commit in payload['commits']:
            removed_files += commit['removed']
        if len(removed_files) != 0 and removed_files != []:
            files_changed=True
            for file in removed_files:
                if file != None and file != '':
                    if memcache.get(file) != None: memcache.delete(memcache.get(file))
                    memcache.delete(file)

        added_files = []
        for commit in payload['commits']:
            added_files += commit['added']
        if len(added_files) != 0 and added_files != []:
            files_changed=True
            get_tree()
#            for file in removed_files:
 #               if file != None and file != '':
  #                  if memcache.get(file) != None: memcache.delete(memcache.get(file))
   #                 memcache.delete(file)
        if files_changed: sendmail('Odd. No files were changed in this commit')
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


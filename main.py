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
import datetime
import hashlib
import urllib
import base64
import json
import logging
import time
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
        result = json.loads(urllib.urlopen(url).read())
        memcache.set(str(url_hash), result, 3600)
        return result
    else:
        return result


def get_tree():
    logging.info('Lets go cut down a tree!')
    url = 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master'
    result = None
    key = 'tree'
    try:
        result = memcache.get(str(key))
        if result != None:
            #pass
            logging.info('Memcache get successful; got the repo tree\nlength: '+str(len(str(result))))
    except:
       # pass
        logging.info('tree memcache get excepted')
    if result == None:
        logging.info('Getting the result from the GitHub API')
        result = json.loads(urllib.urlopen(url).read())
        memcache.set(str(key), result, 86400)
        logging.info('length: '+str(len(str(result))))
    logging.info([commit['path'] for commit in result['tree']])
    logging.info('Okay, done the main part of the get_tree function')
    # okay, the tree is special,
    # so we have to do some special stuff to it :P
    data = result['tree']
    logging.info([commit['path'] for commit in result['tree']])
    logging.info('gotten the tree out of the result')
    items = []
    tree = []
    logging.info(
        '''Created the items variable,
        this is how many items are in the root level of the the tree '''+str(len(tree)))
    #logging.info(str(tree))
    for item in range(len(data)):
        logging.info(str(data[item]['path']))
     #   time.sleep(2)
        if data[item]['type'] == 'blob':
            tree.append(data[item])
    
    logging.info(
        '''Okay, worked out what needs to be cached.
        now, how many items to be cached:'''+str(len(items)))
    #time.sleep(5)
    tobesent = {}
    logging.info('tobesent')
    logging.info([commit['path'] for commit in result['tree']])
    for item in items:
     #   logging.info(str(item['path']))
        cur_item = memcache.get(str(item['path']).split('/')[-1])
        #if cur_item == None:
         #   for item in
        logging.info('Trying to get this: ' +
                     str(str(item['path']).split('/')[-1]))
        if cur_item == None or cur_item != item['url']:
            if type(cur_item) == list:
                cur_item.append(item['url'])
                memcache.set(str(item['path']).split('/')[-1],
                             item['url'], 86400)
            else:
                memcache.set(str(item['path']).split('/')[-1],
                             item['url'], 86400)
            tobesent[str(item['path']).split('/')[-1]] = item['url']
    #if tobesent != {}: sendmail('Dict of values \n\n'+str(tobesent))
    logging.info([commit['path'] for commit in result['tree']])
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
        data = get_tree()
        logging.info(str(data))
        tree = []
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                if self.request.get('q') in fragment['path'].split('/')[-1]:
                    self.response.out.write(str(fragment['path'].split('/')[-1]) + '\n')


class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        module_found = False
        data = get_tree()
        for x in data:
            if x['path'].split('/')[-1] == self.request.get('name'):
                module_found = True
                self.response.out.write(base64.b64decode(
                    get_url_content(x['url'])['content']))
        if not module_found:
            self.error(404)


class ListModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        data = get_tree()
        tree = []
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                self.response.out.write(str(fragment['path'].split('/')[-1]) + '\n')


def flusher(handler):
    try:
        memcache.flush_all()
    except:
        handler.response.out.write('An error occured')


class SmartFlushHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
            'The Smart Flusher Handler can be reached at this address')

    def post(self):
        payload = self.request.get('payload')
        payload = json.loads(payload)
        files_changed = False
        changed_files = []
        info_dict = {}
        for commit in payload['commits']:
            changed_files += commit['modified']
            try:
                changed_files += commit['removed']
            except:
                pass
        for changed_file in changed_files:
            info_dict[str(changed_file)] = False
        if len(changed_files) != 0 and changed_files != []:
            files_changed = True
            for changed_file in changed_files:
                logging.info('type: ' + str(changed_file))
                if changed_file != None and changed_file != '':
                    logging.info(
                        changed_file + ':' + str(memcache.get(changed_file)))
                    if memcache.get(changed_file) != None:
                        memcache.delete(memcache.get(changed_file))
                    memcache.delete(changed_file)
                    try:
                        info_dict[str(changed_file)] = True
                    except:
                        pass
            sendmail(
                'Here is a list \n\n' +
                str(changed_files) + '\n\n\n\n\n\n\n' + str(info_dict))

        removed_files = []
        for commit in payload['commits']:
            removed_files += commit['removed']
        if len(removed_files) != 0 and removed_files != []:
            files_changed = True
            for file in removed_files:
                if file != None and file != '':
                    if memcache.get(file) != None:
                        memcache.delete(memcache.get(file))
                    memcache.delete(file)

        added_files = []
        for commit in payload['commits']:
            added_files += commit['added']
        if len(added_files) != 0 and added_files != []:
            files_changed = True
            get_tree()
        if not files_changed:
            sendmail('Odd. No files were changed in this commit')

class TreeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello!')
    #    self.response.write(str(get_url_content('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master')))
        self.response.out.write(str(get_tree()))

app = webapp2.WSGIApplication([
    ('/modules/search*', SearchModulesHandler),
    ('/modules/download*', DownloadModulesHandler),
    ('/modules/list', ListModulesHandler),
    ('/flush', SmartFlushHandler),
    ('/tree', TreeHandler),
    ('/', HomeHandler)
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8010')

if __name__ == '__main__':
    main()

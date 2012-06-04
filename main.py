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
This is a simple webapp2 based application for the Google App Engine PaaS;
it uses the GitHub API v3 to request one of the numerous available files
within the [DCPUModules](http://github.com/DCPUTeam/DCPUModules) repository.
It decodes the json returned by the API and the thence linked to base64 encoded
files and provides said files in their original formats, ready to be served to
the DCPUToolchain executables that make use of them.
"""


import hashlib
import urllib
import base64
import json
import logging
import re
from colorsys import hsv_to_rgb
import random
import math

import webapp2
from slpp import slpp as lua
from mailer import sendmail
from google.appengine.api import memcache


def get_url_content(url):
    "this is a caching function, to help keep wait time short"
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
    """this is a hard coded version of the get_url_content function
    but with extra features"""
    url = 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master'
    result = None
    result = memcache.get(str('tree'))
    if result != None:
        logging.info(
            'Memcache get successful; got the repo tree\nlength: ' +
            str(len(str(result))))
    else:
        logging.info('Getting the result from the GitHub API')
        result = json.loads(urllib.urlopen(url).read())
        memcache.set(str('tree'), result, 86400)
    logging.info('Okay, done the main part of the get_tree function')
    # okay, the tree is special,
    # so we have to do some special stuff to it :P
    data = result['tree']
    items = []
    tree = []
    for item in range(len(data)):
        if data[item]['type'] == 'blob':
            tree.append(data[item])
    tobesent = {}
    for item in items:
        cur_item = memcache.get(str(item['path']).split('/')[-1])
        #if cur_item == None:
         #   for item in
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
    return result['tree']


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        "handles get requests"
        output = ''
        output += '<ul>'
        pages = ['search', 'tree', 'tree/pretty']
        for page in pages:
            output += '<li><a href="/human/%s">%s</a></li>' % (page, page)
        self.response.write(output)


class HumanSearch(webapp2.RequestHandler):
    "Handler searching of the repo"
    def get(self):
        "provides search interface"
        self.response.write('''
<h3>Search the available modules</h3>
<form method="POST" action="/human/search">
<input name="q"/>
<select name="type">
  <option value="">All results</option>
  <option value="hardware">Hardware</option>
  <option value="debugger">Debugger</option>
  <option value="preprocessor">Preprocessor</option>
</select>
<input type="submit"/>
</form>''')

    def post(self):
        "Handles get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        query = self.request.get('q')
        type = self.request.get('type')
        module_types = ['preprocessor', 'debugger', 'hardware']
        if type.lower() not in module_types:
            type = None
        else:
            type = type.lower()
        data = get_tree()
        if type != None:
            logging.info('Type was specified: '+str(type))
            for fragment in data:
                if fragment['path'].endswith('.lua'):
                    logging.info(str(type) + ':' +
                        str(get_module_data(fragment)))
                    logging.info('fragment: '+str(fragment))
                    if (query in fragment['path'].split('/')[-1] and
                        type == get_module_data(fragment)['Type'].lower()):
                                self.response.out.write(
                                  str(fragment['path'].split('/')[-1]) + '\n')
        else:
            logging.info('Type was not specified')
            for fragment in data:
                if (fragment['path'].endswith('.lua') and
                    query in fragment['path'].split('/')[-1]):
                            self.response.out.write(
                                str(fragment['path'].split('/')[-1]) + '\n')




class SearchModulesHandler(webapp2.RequestHandler):
    "Handler searching of the repo"
    def get(self):
        "Handles get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        query = self.request.get('q')
        data = get_tree()
        for fragment in data:
            if (fragment['path'].endswith('.lua') and
                query in fragment['path'].split('/')[-1]):
                        self.response.out.write(
                            str(fragment['path'].split('/')[-1]) + '\n')


class DownloadModulesHandler(webapp2.RequestHandler):
    "Handles download requests"
    def get(self):
        "Handlers get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        module_found = False
        data = get_tree()
        for fragment in data:
            if fragment['path'].split('/')[-1] == self.request.get('name'):
                module_found = True
                self.response.out.write(base64.b64decode(
                    get_url_content(fragment['url'])['content']))
        if not module_found:
            self.error(404)

    def post(self):
        "Handlers post requests"
        self.response.write('This uri does not handle post requests')


class ListModulesHandler(webapp2.RequestHandler):
    "returns a list of accessable modules"
    def get(self):
        "Handlers get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        data = get_tree()
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                self.response.out.write(
                    str(fragment['path'].split('/')[-1]) + '\n')


def flusher(handler):
    "Performs a memcache flush"
    try:
        memcache.flush_all()
    except:
        handler.response.out.write('An error occured')


class SmartFlushHandler(webapp2.RequestHandler):
    "Tries to efficiently flush the memcache"
    def get(self):
        "Handles get requests to this uri"
        self.response.out.write(
            'The Smart Flusher Handler can be reached at this address')

    def post(self):
        "Handles post requests to this uri"
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
                        changed_file + ':' +
                        str(memcache.get(changed_file)) + ':' +
                        hashlib.md5(
                            str(memcache.get(changed_file))).hexdigest())
                    if memcache.get(changed_file) != None:
                        memcache.delete(
                            hashlib.md5(
                                memcache.get(changed_file)).hexdigest())
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
            for removed_file in removed_files:
                if removed_file != None and removed_file != '':
                    if memcache.get(removed_file) != None:
                        memcache.delete(
                            hashlib.md5(
                                memcache.get(removed_file)).hexdigest())
                    memcache.delete(removed_file)

        added_files = []
        for commit in payload['commits']:
            added_files += commit['added']
        if len(added_files) != 0 and added_files != []:
            files_changed = True
            get_tree()
        if not files_changed:
            sendmail('Odd. No files were changed in this commit')

# MODULE = {
#  Type = "Preprocessor",
#  Name = ".ASSERT directive",
#  Version = "1.0"
#};


def get_module_data(fragment):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    file_data = base64.b64decode(
        get_url_content(
            fragment['url'])['content'])
    module_data = (
        re.search('MODULE\s*=\s*\{([^}]*)\}',
                  file_data))
    try:
        module_data = module_data.group(0)
        module_data = module_data.strip('MODULE=')
        module_data = module_data.strip('MODULE =')
        module_data = lua.decode(module_data)
    except AttributeError:
        logging.info('module_data: ' + str(module_data))
    return module_data


def mine(hue, saturation, value):
    "a dumb hsv-rgb converter"
    hue = hue/1*256
    saturation = saturation/1*256
    value = value/1*256
    return [hue, saturation, value]


def pretty_colours(how_many):
    """uses golden ratio to create pleasant/pretty colours
    returns in rgb form"""
    golden_ratio_conjugate = (1+math.sqrt(5))/2
    logging.info('golden_ratio_conjugate: ' + str(golden_ratio_conjugate))
    #h = random.random()#1,5000) # use random start value
    colours = []
    hue = 0
    blocks = 1001
    for tmp in range(blocks):
        hue += golden_ratio_conjugate#*(tmp/5)
        hue = hue % 1
        colours.append(hsv_to_rgb(hue, 0.5, 0.95))

    logging.info('colours: '+str(colours))
    final_colours = []
    for colour in colours:
        temp_c = mine(colour[0], colour[1], colour[2])
        temp_c = (int(round(temp_c[0])),
            int(round(temp_c[1])),
            int(round(temp_c[2])))
        final_colours.append('rgb('+(str(temp_c[0])+', '+
            str(temp_c[1])+', '+
            str(temp_c[2])+')'))
    return final_colours


class PrettyTreeHandler(webapp2.RequestHandler):
    "Basically the same as /tree, but pretty <3"
    def get(self):
        "handlers get requests"
        colours = pretty_colours(50)
        logging.info(('length: ' + str(len(colours))))
        module_data = pretty_data_tree(get_tree())
        output = ''
        #output += '<div style="center">'
        logging.info(str(module_data))
        output += (
            '''<table border=0 style="
                    border-collapse: collapse;
                    width: 800px;
                    height: 500px;
                    margin-left: -250px;
                    margin-top: -400px;
                    top: 50%;
                    left: 50%;
                ">''')
        output += '<tr>'
        for fragment in module_data:
            output += '<td style="width: 50px; height: 50px; '
            output += ('background-color: %s;">%s</td>' %
                (random.choice(colours), fragment))
        output += '</table>'
        self.response.write(output)



class TreeHandler(webapp2.RequestHandler):
    """A simple debugging interface"""
    def get(self):
        "Handles get requests"
        output = ''
        output = ('<h2>Basic overview</h2>')
        data = get_tree()
        output += data_tree(data)
        self.response.write(output)

    def post(self):
        "Handlers POST requests"
        self.response.write('POST not handled at this URI')


def pretty_data_tree(data):
    "given a data tree, will return a dict version"
    output = {}
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_path = str(fragment['path'].split('/')[-1])
            module_data = get_module_data(fragment)
            output[cur_path] = {}
            output[cur_path]['filename'] = cur_path
            output[cur_path]['type'] = module_data['Type']
            output[cur_path]['name'] = module_data['Name']
            output[cur_path]['Version'] = module_data['Version']
    return output


def data_tree(data):
    "given a data tree, will return a html-based representation"
    output = ''
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_path = str(fragment['path'].split('/')[-1])
            logging.info('Path: '+str(cur_path))
            module_data = get_module_data(fragment)
            output += '<h4>MODULE</h4>'
            output += '<ul>'     # start the list
            output += '<li>Filename: %s</li>' % cur_path
            output += '<li>Type: %s</li>' % module_data['Type']
            output += '<li>Name: %s</li>' % module_data['Name']
            output += '<li>Version: %s</li>' % module_data['Version']
            output += '</ul>'    # end the list
    return output


class RedirectToHumanHandler(webapp2.RequestHandler):
    "redirects the user to /human"
    def get(self):
        "hnadles get requests"
        self.redirect('/human')


app = webapp2.WSGIApplication([
    (r'/human/tree/pretty', PrettyTreeHandler),
    (r'/human/tree*', TreeHandler),
    (r'/human/search*', HumanSearch),
    (r'/human/*', HomeHandler),
    (r'/human*', HomeHandler),
    (r'/modules/search*', SearchModulesHandler),
    (r'/modules/download*', DownloadModulesHandler),
    (r'/modules/list', ListModulesHandler),
    (r'/flush', SmartFlushHandler),
    (r'/', RedirectToHumanHandler)
    ], debug=True)


def main():
    "Runs the paste httpserver"
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8010')

if __name__ == '__main__':
    main()

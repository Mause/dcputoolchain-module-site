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
Contains code that allows the user
to interact with the dtmm server
in a variety of ways :)
"""

import webapp2
import math
from utils import get_module_data
from utils import get_tree
from colorsys import hsv_to_rgb
import random
import logging



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



class HomeHandler(webapp2.RequestHandler):
    def get(self):
        "handles get requests"
        output = ''
        output += '<ul>'
        pages = ['search', 'tree', 'tree/pretty']
        for page in pages:
            output += '<li><a href="/human/%s">%s</a></li>' % (page, page)
        self.response.write(output)



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

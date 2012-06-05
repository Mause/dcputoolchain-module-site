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

# generic imports
import math
import random
import logging
# the colorsys module is required for color convertion
from colorsys import hsv_to_rgb

# the dtmm_utils file
from dtmm_utils import get_module_data
from dtmm_utils import get_tree
from dtmm_utils import dorender


# google appengine imports
import webapp2


class HumanSearch(webapp2.RequestHandler):
    "Handler searching of the repo"
    def get(self):
        "provides search interface"
        output = ''
        output += '<h3>Search the available modules</h3>'
        output += '<form method="POST" action="/human/search">'
        output += '<input name="q"/>'
        output += '<select name="type">'
        output += '  <option value="">All results</option>'
        output += '  <option value="hardware">Hardware</option>'
        output += '  <option value="debugger">Debugger</option>'
        output += '  <option value="preprocessor">Preprocessor</option>'
        output += '</select>'
        output += '<input type="submit"/>'
        output += '</form>'
        self.response.write(output)

    def post(self):
        "Handles get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        query = self.request.get('q')
        requested_type = self.request.get('type')
        module_types = ['preprocessor', 'debugger', 'hardware']
        output = ''
        if requested_type.lower() not in module_types:
            requested_type = None
        else:
            requested_type = requested_type.lower()
        data = get_tree()
        if requested_type != None:
            logging.info('Type was specified: '+str(requested_type))
            for fragment in data:
                mod_data_frag = get_module_data(fragment)
                if fragment['path'].endswith('.lua'):
                    logging.info(str(requested_type) + ':' +
                        str(mod_data_frag))
                    if query in fragment['path'].split('/')[-1]:
                        if requested_type == mod_data_frag['Type'].lower():
                            output += (
                                str(fragment['path'].split('/')[-1]) + '\n')
        else:
            logging.info('Type was not specified')
            for fragment in data:
                if fragment['path'].endswith('.lua'):
                    if query in fragment['path'].split('/')[-1]:
                        output += (
                            str(fragment['path'].split('/')[-1]) + '\n')
        self.response.out.write(output)



class HomeHandler(webapp2.RequestHandler):
    "Returns a list of the human pages"
    def get(self):
        "handles get requests"
        output = ''
        output += '<ul>'
        pages = ['search', 'tree', 'tree/pretty']
        for page in pages:
            output += '<li><a href="/human/%s">%s</a></li>' % (page, page)
        self.response.write(output)



def mine(hue, saturation, value):
    """a dumb hsv-rgb converter
    really just mutliplies the input values by 256"""
    hue = hue*256
    saturation = saturation*256
    value = value*256
    return [hue, saturation, value]


def pretty_colours(how_many):
    """uses golden ratio to create pleasant/pretty colours
    returns in rgb form"""
    golden_ratio_conjugate = (1+math.sqrt(5))/2
    logging.info('golden_ratio_conjugate: ' + str(golden_ratio_conjugate))
    hue = random.random()#1,5000) # use random start value
    colours = []
    #hue = 0
    #blocks = 1001
    for tmp in range(how_many):
        hue += golden_ratio_conjugate*(tmp/5)
        hue = hue % 1
        colours.append(hsv_to_rgb(hue, 0.5, 0.95))

    #logging.info('colours: '+str(colours))
    logging.info('one colour: '+str(colours[0]))
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
        module_data = pretty_data_tree(get_tree(), colours)
        logging.info('module_data: '+str(module_data))
        tree = []
        fragment_num = 0
        for fragment in module_data:
            if fragment_num % 10 == 0:
                module_data[fragment]['row'] = True
            else:
                module_data[fragment]['row'] = False
            tree.append(module_data[fragment])
            fragment_num += 1
        dorender(self, 'tree_pretty.html', {'tree': tree})



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


def pretty_data_tree(data, colours):
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
            output[cur_path]['background'] = random.choice(colours)
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

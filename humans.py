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
from dtmm_utils import get_hardware_data
from dtmm_utils import get_tree
from dtmm_utils import dorender
from dtmm_utils import FourOhFourErrorLog

# google appengine imports
import webapp2


class RedirectToHumanHandler(webapp2.RequestHandler):
    "redirects the user to /human"
    def get(self):
        "handles get requests"
        self.redirect('/human')
    def post(self):
        "handles post requests"
        self.redirect('/human')

class HomeHandler(webapp2.RequestHandler):
    "Returns a list of the human pages"
    def get(self):
        "handles get requests"
        output = ''
        output += '<ul>'
        pages = ['search', 'tree', 'tree/pretty', 'listing']
        for page in pages:
            output += '<li><a href="/human/%s">%s</a></li>' % (page, page)
        self.response.write(output)


class PrettyTreeHandler(webapp2.RequestHandler):
    "Basically the same as /tree, but pretty <3"
    def get(self):
        "handles get requests"
        module_data = pretty_data_tree(self, get_tree(self), pretty_colours(50))
        tree = []
        fragment_num = 0
        break_on = 3
        cell_height = 50 # in pixels :D
        for fragment in module_data:
            if fragment_num % break_on == 0:
                module_data[fragment]['row'] = 'yes'
            else:
                module_data[fragment]['row'] = 'no'
            module_data[fragment]['width'] = ''
            tree.append(module_data[fragment])
            fragment_num += 1
        calc = {}
        if len(module_data) % break_on == 1:
            calc['height'] = ((((len(module_data)-2)/break_on) +
                ((len(module_data)-2)%break_on)) *
                cell_height)
            calc['margin_height'] = calc['height']/2
        calc['width'] = 900
        calc['margin_width'] = calc['width']/2
        for fragment in tree:
            fragment['width'] = calc['width']/break_on
        if len(module_data) % break_on != 0:
            logging.info(str(len(module_data)) + ' % ' +
                str(break_on) + ' = ' + str(len(module_data) % break_on))
            if len(module_data) % break_on == 1:
                logging.info(str(tree[-1]['filename']))
                tree[-1]['width'] = calc['width']
            if len(module_data) % break_on == 2:
                logging.info(str(tree[-1]['filename']))
                logging.info(str(tree[-2]['filename']))
                tree[-1]['width'] = calc['width']/2
                tree[-2]['width'] = calc['width']/2
        tree[0]['row'] = 'no'
        dorender(self, 'tree_pretty.html', {'tree': tree,
                                            'calc': calc})


class TreeHandler(webapp2.RequestHandler):
    """A simple debugging interface"""
    def get(self):
        "Handles get requests"
        output = ''
        output = ('<h2>Basic overview</h2>')
        data = get_tree(self)
        output += data_tree(self, data)
        self.response.write(output)

    def post(self):
        "Handlers POST requests"
        self.response.write('POST not handled at this URI')


class InspectHandler(webapp2.RequestHandler):
    """Returns a data tree specific to a module"""
    def get(self):
        "handlers get requests"
        data = get_tree(self)
        to_give = []
        module_name = self.request.get('name')
        for fragment in data:
            if fragment != {}:
                if fragment['path'].split('/')[-1] == module_name:
                    to_give.append(fragment)
        logging.info(str(to_give))
        self.response.write(data_tree(self, to_give))



class ListingHandler(webapp2.RequestHandler):
    """Lists failed module requests"""
    def get(self):
        "handlers get requests"
        requests = FourOhFourErrorLog.all()
        output = ''
        output += '<strong>These modules were requested by users,'
        output += ' but they do not exist in the repository</strong></br>'
        output += 'You may <a href=#>delete</a> these entries if you wish<br>'
        for fragment in requests:
            output += (str(fragment.datetimer) + ' - ' +
                str(fragment.address) + ' - ' +
                str(fragment.requested_module) + '</br>')
        self.response.write(output)


class HumanSearch(webapp2.RequestHandler):
    "Handler searching of the repo"
    def get(self):
        "provides search interface"
        #query = self.request.get('q')
        #requested_type = self.request.get('type')
        #if query == None and requested_type == None:
        dorender(self, 'human_search.html', {})
        #else:
         #   output = search(self, query, requested_type)
          #  self.response.out.write(data_tree(self, output))


    def post(self):
        "Handles get requests"
        query = self.request.get('q')
        requested_type = self.request.get('type')
        output = search(self, query, requested_type)
        self.response.out.write(data_tree(self, output))


def search(handler, query, requested_type):
    "filters fragment accourding to input"
    module_types = ['preprocessor', 'debugger', 'hardware']
    output = []
    if requested_type.lower() not in module_types:
        requested_type = None
    else:
        requested_type = requested_type.lower()
    data = get_tree(handler)
    if requested_type != None:
        logging.info('Type was specified: '+str(requested_type))
        for fragment in data:
            mod_data_frag = get_module_data(handler, fragment)
            if fragment['path'].endswith('.lua'):
#                logging.info(str(requested_type) + ':' +
 #                   str(mod_data_frag))
                if query in fragment['path'].split('/')[-1]:
                    if requested_type == mod_data_frag['Type'].lower():
                        output.append(fragment)
    else:
        logging.info('Type was not specified')
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                if query in fragment['path'].split('/')[-1]:
                    output.append(fragment)
    return output




def iround(num):
    "returns input rounded and int'ed"
    return int(round(num))

def pretty_colours(how_many):
    """uses golden ratio to create pleasant/pretty colours
    returns in rgb form"""
    golden_ratio_conjugate = (1+math.sqrt(5))/2
    hue = random.random()  # use random start value
    colours = []
    for tmp in range(how_many):
        hue += golden_ratio_conjugate*(tmp/(5*random.random()))
        hue = hue % 1
        colours.append(hsv_to_rgb(hue, 0.5, 0.95))

    logging.info('one colour: '+str(colours[0]))
    final_colours = []
    for colour in colours:
        temp_c = (iround(colour[0]*256),
            iround(colour[1]*256),
            iround(colour[2]*256))
        final_colours.append('rgb('+(str(temp_c[0])+', '+
            str(temp_c[1])+', '+
            str(temp_c[2])+')'))
    return final_colours


# the theory for this colour generator was taken from;
# martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
def pretty_data_tree(handler, data, colours=None):
    "given a data tree, will return a dict version"
    output = {}
    colour_num = 0
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_path = str(fragment['path'].split('/')[-1])
            module_data = get_module_data(handler, fragment)
            output[cur_path] = {}
            output[cur_path]['filename'] = cur_path
            output[cur_path]['type'] = module_data['Type']
            output[cur_path]['name'] = module_data['Name']
            output[cur_path]['Version'] = module_data['Version']
            if colours != None:
                output[cur_path]['background'] = colours[colour_num]
                #random.choice(colours)
                colour_num += 1
    return output


def data_tree(handler, data):
    "given a data tree, will return a html-based representation"
    output = ''
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_path = str(fragment['path'].split('/')[-1])
            module_data = get_module_data(handler, fragment)
            output += '<h4>MODULE</h4>\n'
            output += '<ul>\n'     # start the list
            #output += str(fragment)
            output += ('''<li>Filename: <a href="/modules/download?name=%s">%s
                </a></li>\n''' % (cur_path, cur_path))
            output += ('<li>Type: <a href="/human/search?type=%s">%s</a></li>\n'
                % (module_data['Type'], module_data['Type']))
            output += '<li>Name: %s</li>\n' % module_data['Name']
            output += '<li>Version: %s</li>\n' % module_data['Version']
            if module_data['Type'].lower() == 'hardware':
                hardware_data = get_hardware_data(handler, fragment)
                output += "</br>"
                output += "<li>Hardware ID: %s</li>" % str(hardware_data['ID'])
                output += ("<li>Hardware version: %s</li>" %
                    str(hardware_data['Version']))
                output += ("<li>Hardware Manufacturer: %s</li>" %
                    str(hardware_data['Manufacturer']))
            output += '</ul>\n'    # end the list
    return output

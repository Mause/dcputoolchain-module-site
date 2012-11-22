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

import webapp2
from google.appengine.api import memcache

module_types = ['preprocessor', 'debugger', 'hardware', 'optimizer']


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
        pages = ['search', 'tree', 'tree/pretty', 'listing']
        dorender(self, 'human_index.html', {'pages': pages})


class PrettyTreeHandler(webapp2.RequestHandler):
    "Basically the same as /humans/tree, but pretty <3"
    def get(self):
        tree = memcache.get('pretty_tree_tree')
        calc = memcache.get('pretty_tree_calc')
        if not tree or not calc:
            data_tree = get_tree(self)
            data_tree = filter(lambda x: x['path'].endswith('.lua'), data_tree)
            colours = pretty_colours(len(data_tree))

            tree = []
            calc = {}
            break_on = 3
            cell_height = 80  # in pixels :D
            header_diff = 20
            fragment_num = 0
            calc['width'] = 900
            calc['cell_height'] = cell_height
            calc['margin_width'] = calc['width'] / 2

            for fragment in range(len(data_tree)):
                cur_module = get_module_data(self, data_tree[fragment])
                cur_module['filename'] = str(data_tree[fragment]['path']).split('/')[-1]
                cur_module['background'] = colours[fragment]
                if fragment_num % break_on == 0:
                    cur_module['row'] = 'yes'
                else:
                    cur_module['row'] = 'no'
                cur_module['width'] = calc['width'] / break_on
                cur_module['index'] = fragment_num

                tree.append(cur_module)
                fragment_num += 1

            rows = len(filter(lambda x: x['row'] == 'yes', tree))
            calc['height'] = (rows * cell_height) + header_diff
            logging.info('This many rows; %s' % (rows))
            calc['margin_height'] = calc['height'] / 2
            calc['outer_container_height'] = calc['height']

            if len(tree) % break_on != 0:
                if len(tree) % break_on == 1:
                    tree[-1]['width'] = calc['width']
                if len(tree) % break_on == 2:
                    tree[-1]['width'] = calc['width'] / 2
                    tree[-2]['width'] = calc['width'] / 2
            # tree[0]['row'] = 'no'
            memcache.set('pretty_tree_tree', tree)
            memcache.set('pretty_tree_calc', calc)

        dorender(self, 'tree_pretty.html', {'tree': tree,
                                            'calc': calc})


class TreeHandler(webapp2.RequestHandler):
    """A simple debugging interface"""
    def get(self):
        data = get_tree(self)
        if not data:
            self.error(408)
            return
        dorender(self, 'tree.html', {'tree': data_tree(self, data)})

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
        output += '<form method="POST" target="/human/listing">You may <a href="#" onclick="document.getElementById("delete_em").submit()">delete</a> these entries if you wish</form><br>'
        for fragment in requests:
            output += (str(fragment.datetimer) + ' - ' +
                str(fragment.address) + ' - ' +
                str(fragment.requested_module) + '</br>')
        self.response.write(output)

    def post(self):
        map(lambda x: x.delete(), FourOhFourErrorLog.all())


class HumanSearch(webapp2.RequestHandler):
    "Handle searching of the repo"
    def get(self):
        query = self.request.get('q')
        requested_type = self.request.get('type')
        if query or requested_type:
            output = search(self, query, requested_type)
            dorender(
                self,
                'human_search.html',
                {'results': data_tree(self, output),
                'selected_type': requested_type,
                'types': gen_types(requested_type)})
        else:
            dorender(
                self,
                'human_search.html',
                {'selected_type': requested_type,
                'types': gen_types(requested_type)})

    def post(self):
        query = self.request.get('q')
        requested_type = self.request.get('type')
        output = search(self, query, requested_type)
        dorender(
            self,
            'human_search.html',
            {'results': data_tree(self, output),
            'selected_type': requested_type,
            'types': gen_types(requested_type)})


def gen_types(selected=None):
    final = []
    for frag in module_types:
        to_select = ''
        if str(selected).lower() == str(frag).lower():
            to_select = 'selected'
        final.append(
            {'name': frag,
            'selected': to_select})
    return final


def search(handler, query, requested_type=''):
    "filters fragment accourding to input"
    output = []
    query = query.lower()
    data = get_tree(handler)
    requested_type = requested_type.lower()

    if requested_type not in module_types:
        logging.info('Type was not specified')
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                if query in fragment['path'].split('/')[-1]:
                    output.append(fragment)
    else:
        logging.info('Type was specified: ' + str(requested_type))
        for fragment in data:
            mod_data_frag = get_module_data(handler, fragment)
            if fragment['path'].endswith('.lua'):
                if query in fragment['path'].split('/')[-1].lower():
                    if requested_type.lower() == mod_data_frag['Type'].lower():
                        output.append(fragment)
    return output


def iround(num):
    "returns input rounded and int'ed"
    return int(round(num))


# the theory for this colour generator was taken from;
# http://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
def pretty_colours(how_many):
    """uses golden ratio to create pleasant/pretty colours
    returns in rgb form"""
    golden_ratio_conjugate = (1 + math.sqrt(5)) / 2
    hue = random.random()  # use random start value
    final_colours = []
    for tmp in range(how_many):
        hue += golden_ratio_conjugate * (tmp / (5 * random.random()))
        hue = hue % 1
        converted = (hsv_to_rgb(hue, 0.5, 0.95))
        temp_c = map(lambda x: iround(x * 256), converted)
        final_colours.append('rgb(%s, %s, %s)' % tuple(temp_c))
    return final_colours


def data_tree(handler, data):
    "given a data tree, will return a html-based representation"
    output = ''
    if not data:
        return
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_path = str(fragment['path'].split('/')[-1])
            module_data = get_module_data(handler, fragment)
            logging.info('module data; %s' % module_data)
            output += '<h4>MODULE</h4>\n'
            output += '<ul>\n'     # start the list

            output += ('''<li>Filename: <a href="/modules/download?name=%s">%s
                </a></li>\n''' % (cur_path, cur_path))
            output += ('<li>Type: <a href="/human/search?type=%s">%s</a></li>\n'
                % (module_data['Type'], module_data['Type']))
            output += '<li>Name: %s</li>\n' % module_data['Name']
            output += '<li>Version: %s</li>\n' % module_data['Version']
            if 'SDescription' in module_data:
                output += '<li>Short description: %s</li>\n' % module_data['SDescription']
            if 'URL' in module_data:
                output += '<li>URL: <a href="{url}">{url}</a></li>\n'.format(url=module_data['URL'])
            if module_data['Type'].lower() == 'hardware':
                hardware_data = get_hardware_data(handler, fragment)
                logging.info(hardware_data)
                output += "<li>Hardware ID: %s</li>" % hex(hardware_data['ID'])
                output += ("<li>Hardware version: %s</li>" %
                    hex(hardware_data['Version']))
                output += ("<li>Hardware Manufacturer: %s</li>" %
                    hex(hardware_data['Manufacturer']))
            output += '</ul>\n'    # end the list
    return output

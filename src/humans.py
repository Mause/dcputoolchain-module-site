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

# the colorsys module is required for color conversion
from colorsys import hsv_to_rgb

# the dtmm_utils file
import dtmm_utils

from google.appengine.api import memcache

module_types = ['preprocessor', 'debugger', 'hardware', 'optimizer']


class RedirectToHumanHandler(dtmm_utils.BaseRequestHandler):
    "redirects the user to /human"
    def get(self):
        "handles get requests"
        self.redirect('/human')

    def post(self):
        "handles post requests"
        self.redirect('/human')


class HomeHandler(dtmm_utils.BaseRequestHandler):
    "Returns a list of the human pages"
    def get(self):
        pages = ['search', 'tree', 'tree/pretty', 'listing']
        dtmm_utils.dorender(self, 'human_index.html', {'pages': pages})


class PrettyTreeHandler(dtmm_utils.BaseRequestHandler):
    "Basically the same as /humans/tree, but pretty <3"
    def get(self):
        tree = memcache.get('pretty_tree_tree')
        calc = memcache.get('pretty_tree_calc')
        if not tree or not calc:
            data_tree = dtmm_utils.get_tree(self)
            assert data_tree
            data_tree = (x for x in data_tree if x['path'].endswith('.lua'))

            tree = []
            calc = {}
            break_on = 3
            cell_height = 80  # in pixels :D
            header_diff = 20
            calc['width'] = 900
            calc['cell_height'] = cell_height
            calc['margin_width'] = calc['width'] / 2

            for fragment_num, fragment in enumerate(data_tree):
                logging.info('Fragment; %s' % fragment)
                logging.info('Fragment_num; %s' % fragment_num)
                cur_module = dtmm_utils.get_module_data(self, fragment)
                cur_module['filename'] = str(fragment['path']).split('/')[-1]
                if fragment_num % break_on == 0:
                    cur_module['row'] = 'yes'
                else:
                    cur_module['row'] = 'no'
                cur_module['width'] = calc['width'] / break_on
                cur_module['index'] = fragment_num

                tree.append(cur_module)

            rows = sum([1 for module in tree if module['row'] == 'yes'])
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
            tree[0]['row'] = 'no'
            memcache.set('pretty_tree_tree', tree)
            memcache.set('pretty_tree_calc', calc)

        # we want the colours to be different everytime
        colours = pretty_colours(len(tree))
        for colour, fragment in enumerate(tree):
            fragment.update({'background': colours[colour]})

        dtmm_utils.dorender(self, 'tree_pretty.html', {'tree': tree,
                                            'calc': calc})


class TreeHandler(dtmm_utils.BaseRequestHandler):
    """A simple debugging interface"""
    def get(self):
        data = dtmm_utils.get_tree(self)
        if not data:
            self.error(408)
            return
        dtmm_utils.dorender(self, 'tree.html', {'tree': data_tree(self, data)})

    def post(self):
        "Handlers POST requests"
        self.response.write('POST not handled at this URI')


class InspectHandler(dtmm_utils.BaseRequestHandler):
    """Returns a data tree specific to a module"""
    def get(self):
        "handlers get requests"
        tree = dtmm_utils.get_tree(self)
        tree = filter(bool, tree)
        # print 'tree', tree
        assert tree, repr(tree)
        module_name = self.request.get('name')
        to_give = [
            fragment
            for fragment in tree
            if fragment['path'].split('/')[-1] == module_name]
        logging.info(str(to_give))
        self.response.write(data_tree(self, to_give))


class ListingHandler(dtmm_utils.BaseRequestHandler):
    """Lists failed module requests"""
    def get(self):
        "handlers get requests"
        format_str = (
            '{fragment.datetimer} -'
            ' {fragment.address} - '
            '{fragment.module}</br>')
        requests = dtmm_utils.FourOhFourErrorLog.all()
        output = '\n'.join([
            format_str.format(fragment=fragment)
            for fragment in requests])
        dtmm_utils.dorender(
            self, 'module_not_found.html', {'requested': output})

    def post(self):
        for x in dtmm_utils.FourOhFourErrorLog.all():
            x.delete()


class HumanSearch(dtmm_utils.BaseRequestHandler):
    "Handle searching of the repo"
    def get(self):
        query = self.request.get('q')
        requested_type = self.request.get('type')
        if query or requested_type:
            output = search(self, query, requested_type)
            dtmm_utils.dorender(
                self,
                'human_search.html',
                {'results': data_tree(self, output),
                'selected_type': requested_type,
                'types': gen_types(requested_type)})
        else:
            dtmm_utils.dorender(
                self,
                'human_search.html',
                {'selected_type': requested_type,
                'types': gen_types(requested_type)})

    def post(self):
        query = self.request.get('q')
        requested_type = self.request.get('type')
        output = search(self, query, requested_type)
        dtmm_utils.dorender(
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
    "filters modules according to input"
    output = []
    query = query.lower()
    data = dtmm_utils.get_tree(handler)
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
            mod_data_frag = dtmm_utils.get_module_data(handler, fragment)
            if fragment['path'].endswith('.lua'):
                if query in fragment['path'].split('/')[-1].lower():
                    if requested_type.lower() == mod_data_frag['Type'].lower():
                        output.append(fragment)
    return output


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
        temp_c = map(lambda x: int(round(x * 256)), converted)
        final_colours.append('rgb(%s, %s, %s)' % tuple(temp_c))
    return final_colours


def data_tree(handler, data):
    "given a data tree, will return a html-based representation"
    if not data:
        return None
    modules = []
    for fragment in data:
        if fragment['path'].endswith('.lua'):
            cur_module = {}
            cur_module['cur_path'] = str(fragment['path'].split('/')[-1])
            cur_module['module_data'] = dtmm_utils.get_module_data(
                handler, fragment)

            if cur_module['module_data']['Type'].lower() == 'hardware':
                cur_module['hardware_data'] = dtmm_utils.get_hardware_data(
                    handler, fragment)

                cur_module['hardware_data']['ID'] = hex(
                    cur_module['hardware_data']['ID'])
                cur_module['hardware_data']['Version'] = hex(
                    cur_module['hardware_data']['Version'])
                cur_module['hardware_data']['Manufacturer'] = hex(
                    cur_module['hardware_data']['Manufacturer'])
            modules.append(cur_module)
    return dtmm_utils.dorender(
        handler, 'data_tree.html', {'modules': modules}, write=False)

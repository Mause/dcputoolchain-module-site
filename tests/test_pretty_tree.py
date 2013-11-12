# The MIT License (MIT)

# Copyright (c) 2013 Dominic May

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import common
import test_data

from mock import patch
from google.appengine.api import memcache


@patch('dtmm_utils.get_modules', autospec=True)
@patch('dtmm_utils._get_live_data', lambda handler, fragment: test_data.DATA_TREE_DATA)
class TestPrettyTree(common.DMSHandlerTestCase):
    def test_human_tree_pretty_single_module(self, get_modules):
        get_modules.return_value = [{'path': 'assert.lua'}]

        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_rows(self, get_modules):
        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'},
            {'path': 'four.lua'},
            {'path': 'five.lua'}
        ]

        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_single_row(self, get_modules):

        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'}
        ]
        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_memcache(self, _):
        memcache.set(
            'pretty_tree_tree',
            [
                {
                    u'index': 0,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assert.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware',
                    u'row': False
                },
                {
                    u'index': 1,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assertdb.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware', u'row': False
                },
                {
                    u'index': 2,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assertpp.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware', u'row': False
                }
            ]
        )
        memcache.set(
            'pretty_tree_calc',
            {
                u'cell_height': 80,
                u'height': 100,
                u'width': 900,
                u'outer_container_height': 100,
                u'margin_height': 50.0,
                u'margin_width': 450.0
            }
        )

        self.testapp.get('/human/tree/pretty')

if __name__ == '__main__':
    common.main()

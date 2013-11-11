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

# unit testing specific imports
import unittest2
from mock import patch, MagicMock


class TestHumans(common.DMSTestCase):
    def test_gen_types_with_selected(self):
        import humans
        end_data = humans.gen_types()

        self.assertEqual(
            end_data,
            [
                {'selected': False, 'name': 'preprocessor'},
                {'selected': False, 'name': 'debugger'},
                {'selected': False, 'name': 'hardware'},
                {'selected': False, 'name': 'optimizer'}
            ]
        )

    def test_gen_types_without_selected(self):
        import humans

        end_data = humans.gen_types(selected='optimizer')

        self.assertEqual(
            end_data,
            [
                {'selected': False, 'name': 'preprocessor'},
                {'selected': False, 'name': 'debugger'},
                {'selected': False, 'name': 'hardware'},
                {'selected': True, 'name': 'optimizer'}
            ]
        )

    def test_pretty_colours(self):
        import re
        import humans
        import random

        output = humans.pretty_colours(random.randint(200, 500))

        for colour in output:
            self.assertTrue(re.match(
                r'rgb\(\d+?, \d+?, \d+?\)', colour))

    @patch('dtmm_utils._get_live_data', lambda handler, fragment: test_data.DATA_TREE_DATA)
    def test_data_tree(self):
        import humans

        humans.data_tree(MagicMock(), [
            {'path': 'assert.lua', 'url': 'mock'},
            {'path': 'assert.py'}
        ])


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

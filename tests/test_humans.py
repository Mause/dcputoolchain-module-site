# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# this needs to be done before anything to do with gae gets imported
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

# unit testing specific imports
import common
import base64
import unittest2
from mock import patch


class TestHumans(common.DMSTestCase):
    def setUp(self):
        super(TestHumans, self).setUp()

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

    def mock_get_tree(handler=None):
        return [{
            u'url': '',
            u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
            u'mode': u'100644',
            u'path': u'hmd2043.lua',
            u'type': u'blob',
            u'size': 3979
        }]

    def mock_get_url_content(handler=None, url=None):
        content = '''
        MODULE = {
            Type = "Hardware",
            Name = "HMD2043",
            Version = "1.1",
            SDescription = "Deprecated HMD2043 hardware device",
            URL = "False URL"
        };'''
        return {'content': base64.b64encode(content)}

    @patch('dtmm_utils.get_url_content', mock_get_url_content)
    @patch('dtmm_utils.get_tree', mock_get_tree)
    def test_search_with_type(self, *args, **kwargs):
        import humans

        end_data = humans.search(None, 'query', '')
        self.assertEqual(end_data, [])

        end_data = humans.search(None, 'hmd', '')
        self.assertEqual(
            end_data,
            [{
                u'url': '',
                u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
                u'mode': u'100644',
                u'path': u'hmd2043.lua',
                u'type': u'blob',
                u'size': 3979}])

    @patch('dtmm_utils.get_url_content', mock_get_url_content)
    @patch('dtmm_utils.get_tree', mock_get_tree)
    def test_search_without_type(self):
        import humans

        end_data = humans.search(None, 'query', 'hardware')
        self.assertEqual(end_data, [])

        end_data = humans.search(None, 'HMD2043')
        self.assertEqual(
            end_data,
            [{
                u'url': u'',
                u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
                u'mode': u'100644',
                u'path': u'hmd2043.lua',
                u'type': u'blob',
                u'size': 3979}])

    def test_pretty_colours(self):
        import re
        import humans
        import random

        output = humans.pretty_colours(random.randint(200, 500))

        for colour in output:
            self.assertTrue(re.match(
                r'rgb\(\d+?, \d+?, \d+?\)', colour))

    @patch('dtmm_utils.dorender')
    @patch('dtmm_utils._get_live_data', lambda handler, fragment: common.DATA_TREE_DATA)
    def test_data_tree(self, dorender):
        import humans

        humans.data_tree(None, [
            {'path': 'assert.lua', 'url': 'mock'},
            {'path': 'assert.py'}
        ])


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

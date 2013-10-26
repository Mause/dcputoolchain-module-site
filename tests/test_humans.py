# unit testing specific imports
import common
import base64
import unittest2
from mock import patch


class TestHumans(common.DMSTestCase):
    def setUp(self):
        super(TestHumans, self).setUp()

    def test_gen_types(self):
        "testing humans.get_types function"
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
            u'size': 3979}]

    def mock_get_url_content(handler=None, url=None):
        return {
            'content': base64.b64encode('''
                MODULE = {
                    Type = "Hardware",
                    Name = "HMD2043",
                    Version = "1.1",
                    SDescription = "Deprecated HMD2043 hardware device",
                    URL = "False URL"
                };''')}

    @patch('dtmm_utils.get_tree', mock_get_tree)
    @patch('dtmm_utils.get_url_content', mock_get_url_content)
    def test_search(self):
        "testing humans.search function"

        # run the actual tests
        import humans
        # tests with and without success. firstly, without a type specified
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

        # secondly, without a type specified
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
        "testing humans.pretty_colours function"
        import humans
        import re
        import random

        output = humans.pretty_colours(random.randint(200, 500))

        for colour in output:
            self.assertTrue(re.match(
                r'rgb\(\d+?, \d+?, \d+?\)', colour))


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

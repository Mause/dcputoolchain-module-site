# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import base64
import unittest2
from mock import patch
from google.appengine.ext import testbed


class Test_Humans(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_gen_types(self):
        class BaseRequestHandler_replacement:
            pass
        patcher = patch(
            'humans.BaseRequestHandler', BaseRequestHandler_replacement)
        self.addCleanup(patcher.stop)
        patcher.start()
        import humans
        end_data = humans.gen_types()

        self.assertEqual(
            end_data,
            [{'selected': '', 'name': 'preprocessor'},
            {'selected': '', 'name': 'debugger'},
            {'selected': '', 'name': 'hardware'},
            {'selected': '', 'name': 'optimizer'}])

        end_data = humans.gen_types(selected='optimizer')

        self.assertEqual(
            end_data,
            [{'selected': '', 'name': 'preprocessor'},
            {'selected': '', 'name': 'debugger'},
            {'selected': '', 'name': 'hardware'},
            {'selected': 'selected', 'name': 'optimizer'}])

    def test_search(self):
        class BaseRequestHandler_replacement:
            pass
        patcher = patch(
            'humans.BaseRequestHandler', BaseRequestHandler_replacement)
        self.addCleanup(patcher.stop)
        patcher.start()

        # patch some functions
        def get_tree(handler=None):
            return [{
                u'url': '',
                u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
                u'mode': u'100644',
                u'path': u'hmd2043.lua',
                u'type': u'blob',
                u'size': 3979}]

        patcher = patch(
            'humans.get_tree', get_tree)
        self.addCleanup(patcher.stop)
        patcher.start()

        def get_url_content(handler=None, url=None):
            return {
                'content': base64.b64encode('''
                    MODULE = {
                        Type = "Hardware",
                        Name = "HMD2043",
                        Version = "1.1",
                        SDescription = "Deprecated HMD2043 hardware device",
                        URL = "False URL"
                    };''')}
        patcher = patch(
            'dtmm_utils.get_url_content', get_url_content)
        self.addCleanup(patcher.stop)
        patcher.start()

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
        class BaseRequestHandler_replacement:
            pass
        patcher = patch(
            'humans.BaseRequestHandler', BaseRequestHandler_replacement)
        self.addCleanup(patcher.stop)
        patcher.start()
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

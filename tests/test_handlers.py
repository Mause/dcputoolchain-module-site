# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import copy
import urllib
import webtest
import unittest2
import itertools
from mock import patch

# this needs to be done before anything to do with gae gets imported
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

# these next two lines might be broken in the future. not sure what ill do after that :(
from google.appengine.dist import use_library
use_library('django', '1.2')

import common


class TestHandlers(common.DMSTestCase):
    def setUp(self):
        super(TestHandlers, self).setUp()
        self.testbed.init_mail_stub()

        def mock_get_tree(handler):
            return common.TEST_HANDLERS_GET_TREE
        self.get_tree_patcher = patch('dtmm_utils.get_tree', mock_get_tree)
        self.get_tree_patcher.start()

        def mock_get_url_content(handler, url):
            return common.TEST_HANDLERS_URL_CONTENT
        self.get_url_content_patcher = patch('dtmm_utils.get_url_content', mock_get_url_content)
        self.get_url_content_patcher.start()

        from main import app
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.get_tree_patcher.stop()
        self.get_url_content_patcher.stop()
        super(TestHandlers, self).tearDown()

    def test_get_tree(self):
        "testing /human/tree/pretty handler"
        import dtmm_utils
        dtmm_utils.get_tree(0)

    def test_human_tree_pretty(self):
        "testing /human/tree/pretty handler"
        self.testapp.get('/human/tree/pretty')

    def test_human_tree(self):
        "testing /human/tree handler"
        self.testapp.get('/human/tree')

    def test_human_search(self):
        "testing /human/search handler"

        self.testapp.get('/human/search')

        queries = ['', 'random', 'words']
        import humans
        custom_module_types = copy.copy(humans.module_types)
        custom_module_types.append('')
        subtests = itertools.product(queries, custom_module_types)

        for sub in subtests:
            cur_url = '/human/search?'
            cur_url += urllib.urlencode({
                'q': sub[0],
                'type': sub[1]
            })
            self.testapp.get(cur_url)

    def test_human_listing(self):
        "testing /human/listing handler"
        self.testapp.get('/human/listing')

    def test_human_inspect(self):
        "testing /human/inspect handler"
        self.testapp.get('/human/inspect?name=assert.lua')

    def test_human(self):
        "testing /human handler"
        self.testapp.get('/human')

    def test_modules(self):
        pass
        # TODO: check for redirect

    def test_modules_search(self):
        pass


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

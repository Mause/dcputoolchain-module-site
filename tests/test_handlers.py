# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import json
import webtest
import unittest2
import itertools
from mock import patch

# this needs to be done before anything to do with gae gets imported
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

from google.appengine.api import memcache, urlfetch

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
        self.get_url_content_patcher = patch('dtmm_utils.get_url_content',
                                             mock_get_url_content)
        self.get_url_content_patcher.start()

        from main import app
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.get_tree_patcher.stop()
        self.get_url_content_patcher.stop()
        super(TestHandlers, self).tearDown()

    # human interface

    @patch('dtmm_utils.get_modules')
    @patch('dtmm_utils._get_live_data', lambda handler, fragment: common.DATA_TREE_DATA)
    def test_human_tree_pretty(self, get_modules):
        get_modules.return_value = [{'path': 'assert.lua'}]

        self.testapp.get('/human/tree/pretty')
        get_modules.reset_mock()
        memcache.flush_all()

        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'},
            {'path': 'four.lua'},
            {'path': 'five.lua'}
        ]

        self.testapp.get('/human/tree/pretty')

        get_modules.reset_mock()
        memcache.flush_all()

        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'}
        ]
        self.testapp.get('/human/tree/pretty')

        # intentional double-up
        self.testapp.get('/human/tree/pretty')

    @patch('dtmm_utils.get_tree')
    def test_human_tree(self, get_tree):
        self.testapp.get('/human/tree')

        get_tree.return_value = None
        self.assertRaises(webtest.AppError, self.testapp.get, ('/human/tree'))

    def test_human_search(self):
        self.testapp.get('/human/search')
        queries = ['', 'random', 'words']

        import humans
        custom_module_types = humans.module_types + ['']
        subtests = itertools.product(queries, custom_module_types)

        for sub in subtests:
            args = (
                '/human/search?',
                {
                    'q': sub[0],
                    'type': sub[1]
                }
            )

            self.testapp.get(*args)
            self.testapp.post(*args)

    def test_human_inspect(self):
        self.testapp.get('/human/inspect?name=assert.lua')

    def test_human(self):
        self.testapp.get('/human')

    # machine interface

    def test_search_modules(self):
        self.testapp.get('/modules/search?q=assert')

    def test_download_modules(self):
        self.assertRaises(webtest.AppError,
                          self.testapp.get, ('/modules/download'))

        self.testapp.get('/modules/download', {'name': 'assert.lua'})

    def test_list_modules(self):
        self.testapp.get('/modules/list')

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status(self, fetch):

        for platform in ['linux', 'windows', 'mac']:
            url = '/status/{}.png'.format(platform)
            memcache.set('build_status_{}'.format(platform), 'passing')
            self.testapp.get(url)

            memcache.flush_all()
            fetch.reset_mock()

            fetch.return_value.content = json.dumps({'-1': {'text': 'successful'}})
            self.testapp.get(url)

            fetch.reset_mock()

            fetch.return_value.content = json.dumps({'-1': {'text': 'failed'}})
            self.testapp.get(url)

            fetch.reset_mock()

            fetch.return_value.content = json.dumps([])
            self.testapp.get(url)

            fetch.reset_mock()

            # import pudb
            # pudb.set_trace()

            fetch.side_effect = urlfetch.DownloadError
            self.testapp.get(url)

            fetch.reset_mock()

            fetch.side_effect = ValueError
            self.testapp.get(url)

            fetch.reset_mock()

    def test_redirect(self):
        self.testapp.get('/')
        self.testapp.post('/')


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

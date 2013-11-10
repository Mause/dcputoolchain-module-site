import common

# unit testing specific imports
import json
import base64
import webtest
import unittest2
import itertools
from mock import patch, MagicMock

from google.appengine.api import memcache, urlfetch


class TestHandlers(common.DMSTestCase):
    def setUp(self):
        super(TestHandlers, self).setUp()
        self.testbed.init_mail_stub()

        self.get_tree_patcher = patch(
            'dtmm_utils.get_tree',
            lambda handler: common.TEST_HANDLERS_GET_TREE
        )
        self.get_tree_patcher.start()

        self.get_url_content_patcher = patch(
            'dtmm_utils.get_url_content',
            lambda handler, url: common.TEST_HANDLERS_URL_CONTENT
        )
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

    def test_search_modules_with_response(self):
        response = self.testapp.get('/modules/search?q=assert')

        self.assertEqual(
            response.body,
            'assert.lua'
        )

    def test_search_modules_without_response(self):
        response = self.testapp.get('/modules/search?q=nonexistant')

        self.assertEqual(response.body, '')

    def test_download_modules_failure(self):
        self.assertRaises(webtest.AppError,
                          self.testapp.get, ('/modules/download'))

    def test_download_modules_success(self):
        response = self.testapp.get('/modules/download', {'name': 'assert.lua'})
        content = base64.b64decode(common.TEST_HANDLERS_URL_CONTENT['content'])

        self.assertEqual(response.body, content)

    def test_list_modules(self):
        response = self.testapp.get('/modules/list')
        self.assertEqual('200 OK', response.status)

        self.assertEqual(
            response.body,
            'assert.lua'
        )

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_memcache_passing(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            memcache.set('build_status_{}'.format(platform), 'passing')
            self.testapp.get(url)

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_remote_passing(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            fetch.return_value.content = json.dumps({'-1': {'text': 'successful'}})
            self.testapp.get(url)

            self.assertEqual(
                memcache.get('build_status_{}'.format(platform)),
                'passing'
            )

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_remote_failing(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            fetch.return_value.content = json.dumps({'-1': {'text': 'failed'}})
            self.testapp.get(url)

            self.assertEqual(
                memcache.get('build_status_{}'.format(platform)),
                'failing'
            )

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_remote_get_empty(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            fetch.return_value.content = json.dumps([])
            self.testapp.get(url)

            self.assertEqual(
                memcache.get('build_status_{}'.format(platform)),
                'unknown'
            )

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_remote_download_error(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            fetch.side_effect = urlfetch.DownloadError('error')
            self.testapp.get(url)

            self.assertEqual(
                memcache.get('build_status_{}'.format(platform)),
                'unknown'
            )

    @patch('google.appengine.api.urlfetch.fetch')
    def test_build_status_remote_value_error(self, fetch):
        for platform, url in common.PLATFORM_W_URLS:
            fetch.side_effect = ValueError
            self.testapp.get(url)

            self.assertEqual(
                memcache.get('build_status_{}'.format(platform)),
                'unknown'
            )

    def test_redirect(self):
        self.testapp.get('/')
        self.testapp.post('/')

    def test_root_modules_redirect(self):
        self.testapp.get('/modules')

    @patch('dtmm_utils.BaseRequestHandler.dorender')
    @patch('dtmm_utils.development')
    def test_base_handler_not_development(self, development, dorender):
        dorender.return_value = 'world'
        development.return_value = False

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())
        handler.handle_exception(Exception(), MagicMock())

    @patch('dtmm_utils.users')
    @patch('dtmm_utils.development')
    @patch('dtmm_utils.BaseRequestHandler.dorender')
    def test_base_handler_not_admin(self, dorender, development, users):
        dorender.return_value = 'world'
        development.return_value = False
        users.is_current_user_admin.return_value = False

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())
        handler.handle_exception(AssertionError(), MagicMock())

    @patch('dtmm_utils.users')
    @patch('dtmm_utils.development')
    @patch('dtmm_utils.BaseRequestHandler.dorender')
    def test_base_handler_is_admin(self, dorender, development, users):
        dorender.return_value = 'world'
        development.return_value = False
        users.is_current_user_admin.return_value = True

        import dtmm_utils
        handler = dtmm_utils.BaseRequestHandler(MagicMock(), MagicMock())

        self.assertRaises(
            Exception, handler.handle_exception, (Exception(), MagicMock()))

    def test_flush_handler(self):
        self.testapp.get('/flush')
        self.testapp.post('/flush')


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

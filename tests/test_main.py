import os
import json
import base64
import webtest
import unittest2
from mock import patch
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

from google.appengine.ext import testbed


class Test_Main(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_mail_stub()

        # well this sucks. have to start the whole server to test the damn thing
        from main import app
        # Wrap the app with WebTest's TestApp.
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def test_SearchModuleHandler(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "Primary.lua",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                'url': '',
                'content': base64.b64encode(json.dumps({})),
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self

        fetch_patcher = patch(
            'dtmm_utils.authed_fetch', authed_fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        with open('auth_frag.txt', 'w') as fh:
            fh.write('False_Data')
        self.addCleanup(lambda: os.remove('auth_frag.txt'))

        response = self.testapp.get('/human/search')
        # self.assertEqual(response.status_int, 200)

        # from tidylib import tidy_document
        # _, errors = tidy_document(response.body)
        # errors = errors.splitlines()[:-1]
        # self.assertEqual(len(errors), 0)

    def test_PrettyTreeHandler(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "Primary.lua",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                'url': '',
                'content': base64.b64encode(json.dumps({})),
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self

        fetch_patcher = patch(
            'dtmm_utils.authed_fetch', authed_fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        with open('auth_frag.txt', 'w') as fh:
            fh.write('False_Data')
        self.addCleanup(lambda: os.remove('auth_frag.txt'))

        response = self.testapp.get('/human/tree/pretty')
        # self.assertEqual(response.status_int, 200)

        # from tidylib import tidy_document
        # _, errors = tidy_document(response.body)
        # errors = errors.splitlines()[:-1]
        # self.assertEqual(len(errors), 0)

    def test_TreeHandler(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "Primary.lua",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                'url': '',
                'content': base64.b64encode(json.dumps({})),
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self

        fetch_patcher = patch(
            'dtmm_utils.authed_fetch', authed_fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        with open('auth_frag.txt', 'w') as fh:
            fh.write('False_Data')
        self.addCleanup(lambda: os.remove('auth_frag.txt'))

        response = self.testapp.get('/human/tree')
        # self.assertEqual(response.status_int, 200)

        # from tidylib import tidy_document
        # _, errors = tidy_document(response.body)
        # errors = errors.splitlines()[:-1]
        # self.assertEqual(len(errors), 0)


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

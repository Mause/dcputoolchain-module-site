if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

import os
import json
import base64
import unittest2
from mock import patch
from google.appengine.ext import testbed


class Test_DTMM_Utils(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

    def tearDown(self):
        self.testbed.deactivate()

    # @httprettified
    # def test_github_access(self):
        # HTTPretty.register_uri(HTTPretty.GET,
        #     "https://api.github.com/authorizations",
        #     body=json.dumps(
        #         {"token": "df11c284bf0a74752c65efc5595d407f1316837c"}),
        #     status=200)
    #     response = requests.get('http://github.com')
    #     expect(response.status_code).to.equal(201)

    #### dtmm_utils.py file tests ####

    @unittest2.skip
    def test_oauth_token(self):
        class fetch:
            headers = {'x-ratelimit-remaining': 'lots'}
            content = json.dumps(
                {"scopes": ["repo"],
                "token": "df11c284bf0a74752c65efc5595d407f1316837c"})
            status_code = 200

            def __init__(self, **kwargs):
                pass

            def __call__(self):
                return self
        patcher = patch('google.appengine.api.urlfetch.fetch', fetch)
        self.addCleanup(patcher.stop)
        patcher.start()

        import dtmm_utils

        with open('auth_data.json', 'w') as fh:
            auth_data = {u'client_auth_data': {u'client_secret': u'Fake', u'client_id': u'Fake'}}
            fh.write(json.dumps(auth_data))
        data = dtmm_utils.get_oauth_token()
        os.remove('auth_data.json')
        self.assertEqual(data, 'df11c284bf0a74752c65efc5595d407f1316837c')

    def test_authed_fetch(self):
        def get_oauth_token():
            return 'oauth_token'
        oauth_patcher = patch('dtmm_utils.get_oauth_token', get_oauth_token)
        self.addCleanup(oauth_patcher.stop)
        oauth_patcher.start()

        class fetch:
            headers = {'x-ratelimit-remaining': 'lots'}
            content = (
                'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

            def __init__(self, url, headers):
                pass

            def __call__(self):
                return self
        fetch_patcher = patch('google.appengine.api.urlfetch.fetch', fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        import dtmm_utils
        end_data = dtmm_utils.authed_fetch('http://mock.com')
        self.assertEqual(fetch(None, None).content, end_data.content)
        self.assertIsInstance(end_data, fetch)

    def test_get_url_content(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "README.md",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self

        fetch_patcher = patch(
            'dtmm_utils.authed_fetch', authed_fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        import dtmm_utils
        end_data = dtmm_utils.get_url_content(None, 'http://mock.com')
        self.assertEqual(
            end_data,
            {u'tree':
                [{u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'mode': u'100644',
                u'path': u'README.md',
                u'type': u'blob',
                u'size': 314}]}
            )

    def test_get_tree(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "README.md",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self

        fetch_patcher = patch(
            'dtmm_utils.authed_fetch', authed_fetch)
        self.addCleanup(fetch_patcher.stop)
        fetch_patcher.start()

        import dtmm_utils
        end_data = dtmm_utils.get_tree()
        self.assertEqual(
            end_data,
            [{u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
            u'mode': u'100644',
            u'path': u'README.md',
            u'type': u'blob',
            u'size': 314}]
            )

    def test_get_module_data(self):
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

        import dtmm_utils
        end_data = dtmm_utils.get_module_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {'URL': 'False URL',
            'SDescription': 'Deprecated HMD2043 hardware device',
            'Version': '1.1',
            'Type': 'Hardware',
            'Name': 'HMD2043'})

    def test_get_hardware_data(self):
        def get_url_content(handler=None, url=None):
            return {'content': base64.b64encode('''
                        HARDWARE = {
                            ID = 0x74fa4cae,
                            Version = 0x07c2,
                            Manufacturer = 0x21544948 -- HAROLD_IT
                        };''')}

        patcher = patch(
            'dtmm_utils.get_url_content', get_url_content)
        self.addCleanup(patcher.stop)
        patcher.start()

        import dtmm_utils
        end_data = dtmm_utils.get_hardware_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {'Version': 1986, 'ID': 1962560686, 'Manufacturer': 559171912})


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

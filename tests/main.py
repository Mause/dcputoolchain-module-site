# setup the test environment
import sys
import os
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import unittest2
# import requests
# from sure import expect
# from httpretty import HTTPretty, httprettified
import json
import base64

from google.appengine.ext import testbed


class TestFunctions(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

    # @httprettified
    # def test_github_access(self):
        # HTTPretty.register_uri(HTTPretty.GET,
        #     "https://api.github.com/authorizations",
        #     body=json.dumps(
        #         {"token": "df11c284bf0a74752c65efc5595d407f1316837c"}),
        #     status=200)
    #     response = requests.get('http://github.com')
    #     expect(response.status_code).to.equal(201)

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
        import dtmm_utils
        dtmm_utils.urlfetch.real_fetch = dtmm_utils.urlfetch.fetch
        dtmm_utils.urlfetch.fetch = fetch

        with open('auth_frag.txt', 'w') as fh:
            fh.write('False_Data')
        data = dtmm_utils.get_oauth_token()
        os.remove('auth_frag.txt')
        self.assertEqual(data, 'df11c284bf0a74752c65efc5595d407f1316837c')

        dtmm_utils.urlfetch.fetch = dtmm_utils.urlfetch.real_fetch

    def test_authed_fetch(self):
        def get_oauth_token():
            return 'oauth_token'

        class fetch:
            headers = {'x-ratelimit-remaining': 'lots'}
            content = (
                'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

            def __init__(self, url, headers):
                pass

            def __call__(self):
                return self
        import dtmm_utils
        dtmm_utils.urlfetch.real_fetch = dtmm_utils.urlfetch.fetch
        dtmm_utils.urlfetch.fetch = fetch
        dtmm_utils.real_get_oauth_token = dtmm_utils.get_oauth_token
        dtmm_utils.get_oauth_token = get_oauth_token
        end_data = dtmm_utils.authed_fetch('http://mock.com')
        self.assertEqual(fetch(None, None).content, end_data.content)
        self.assertIsInstance(end_data, fetch)
        dtmm_utils.urlfetch.fetch = dtmm_utils.urlfetch.real_fetch
        dtmm_utils.get_oauth_token = dtmm_utils.real_get_oauth_token

    def test_get_url_content(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "README.md",
                "mode": "100644",
                "url": "https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self
        import dtmm_utils
        dtmm_utils.real_authed_fetch = dtmm_utils.authed_fetch
        dtmm_utils.authed_fetch = authed_fetch
        end_data = dtmm_utils.get_url_content(None, 'http://mock.com')
        self.assertEqual(
            end_data,
            {u'tree':
                [{u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'mode': u'100644',
                u'path': u'README.md',
                u'type': u'blob',
                u'size': 314}]}
            )
        dtmm_utils.authed_fetch = dtmm_utils.real_authed_fetch

    def test_get_tree(self):
        class authed_fetch:
            content = json.dumps({"tree": [
                {"type": "blob",
                "path": "README.md",
                "mode": "100644",
                "url": "https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "size": 314}]})

            def __init__(self, url):
                pass

            def __call__(self):
                return self
        import dtmm_utils
        dtmm_utils.real_authed_fetch = dtmm_utils.authed_fetch
        dtmm_utils.authed_fetch = authed_fetch
        end_data = dtmm_utils.get_tree()
        self.assertEqual(
            end_data,
            [{u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/ac178f6489f2d3f601df6a9a5e641b62a0388eae',
            u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
            u'mode': u'100644',
            u'path': u'README.md',
            u'type': u'blob',
            u'size': 314}]
            )
        dtmm_utils.authed_fetch = dtmm_utils.real_authed_fetch

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
        import dtmm_utils
        dtmm_utils.real_get_url_content = dtmm_utils.get_url_content
        dtmm_utils.get_url_content = get_url_content
        end_data = dtmm_utils.get_module_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {'URL': 'False URL',
            'SDescription': 'Deprecated HMD2043 hardware device',
            'Version': '1.1',
            'Type': 'Hardware',
            'Name': 'HMD2043'})
        dtmm_utils.get_url_content = dtmm_utils.real_get_url_content

    def test_get_hardware_data(self):
        def get_url_content(handler=None, url=None):
            return {'content': base64.b64encode('''
                        HARDWARE = {
                            ID = 0x74fa4cae,
                            Version = 0x07c2,
                            Manufacturer = 0x21544948 -- HAROLD_IT
                        };''')}
        import dtmm_utils
        dtmm_utils.real_get_url_content = dtmm_utils.get_url_content
        dtmm_utils.get_url_content = get_url_content
        end_data = dtmm_utils.get_hardware_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {'Version': 1986, 'ID': 1962560686, 'Manufacturer': 559171912})
        dtmm_utils.get_url_content = dtmm_utils.real_get_url_content


def main():
    import dev_appserver
    dev_appserver.fix_sys_path()
    unittest2.main()

if __name__ == '__main__':
    main()

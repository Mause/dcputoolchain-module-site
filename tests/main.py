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
# import json
import base64

from google.appengine.ext import testbed


class TestFunctions(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    # @httprettified
    # def test_github_access(self):
    #     HTTPretty.register_uri(HTTPretty.GET, "http://github.com/",
    #                            body="here is the mocked body",
    #                            status=201)

    #     response = requests.get('http://github.com')
    #     expect(response.status_code).to.equal(201)

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

if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

import json
import common
import base64
import unittest2
from mock import patch
from StringIO import StringIO


def mock_authed_fetch(*args, **kwargs):
    class AuthedFetchObject(object):
        content = json.dumps({
            "tree": [{
                "type": "blob",
                "path": "README.md",
                "mode": "100644",
                "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
                "size": 314
            }]
        })
        raw = StringIO(content)

    return AuthedFetchObject()


def mock_fetch(url, headers):
    class FetchObject(object):
        headers = {'x-ratelimit-remaining': 'lots'}
        content = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

    return FetchObject()


class TestDTMMUtils(common.DMSTestCase):
    @patch('google.appengine.api.urlfetch.fetch', mock_fetch)
    def test_authed_fetch(self):

        import dtmm_utils
        end_data = dtmm_utils.authed_fetch('http://mock.com')
        self.assertEqual(mock_fetch(None, None).content, end_data.content)

    @patch('dtmm_utils.authed_fetch', mock_authed_fetch)
    def test_get_url_content(self):

        import dtmm_utils
        end_data = dtmm_utils.get_url_content(None, 'http://mock.com')
        self.assertEqual(
            end_data,
            {
                u'tree': [{
                    u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                    u'mode': u'100644',
                    u'path': u'README.md',
                    u'type': u'blob',
                    u'size': 314
                }]
            }
        )

    @patch('dtmm_utils.authed_fetch', mock_authed_fetch)
    def test_get_tree(self):

        import dtmm_utils
        end_data = dtmm_utils.get_tree()
        self.assertEqual(
            end_data,
            [{
                u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'mode': u'100644',
                u'path': u'README.md',
                u'type': u'blob',
                u'size': 314
            }]
        )

    @patch('dtmm_utils.get_url_content')
    def test_get_live_module_data(self, get_url_content):
        get_url_content.return_value = {
            'content': base64.b64encode('''
                MODULE = {
                    Type = "Hardware",
                    Name = "HMD2043",
                    Version = "1.1",
                    SDescription = "Deprecated HMD2043 hardware device",
                    URL = "False URL"
                };''')
        }

        import dtmm_utils
        end_data = dtmm_utils.get_live_module_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {
                'URL': 'False URL',
                'SDescription': 'Deprecated HMD2043 hardware device',
                'Version': '1.1',
                'Type': 'Hardware',
                'Name': 'HMD2043'
            }
        )

    @patch('dtmm_utils.get_url_content')
    def test_get_live_hardware_data(self, get_url_content):
        get_url_content.return_value = {
            'content': base64.b64encode('''
                HARDWARE = {
                    ID = 0x74fa4cae,
                    Version = 0x07c2,
                    Manufacturer = 0x21544948 -- HAROLD_IT
                };''')
        }

        import dtmm_utils
        end_data = dtmm_utils.get_live_hardware_data(
            None, {"url": "http://mock.url/hardware_file"})
        self.assertEqual(
            end_data,
            {
                'Version': 1986,
                'ID': 1962560686,
                'Manufacturer': 559171912
            }
        )


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

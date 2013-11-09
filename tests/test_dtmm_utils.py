if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

import json
import common
import base64
import hashlib
import unittest2
from mock import patch, MagicMock

from google.appengine.api import memcache, urlfetch

mock_authed_fetch = MagicMock()
content = json.dumps({
    "tree": [{
        "type": "blob",
        "path": "README.md",
        "mode": "100644",
        "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
        "size": 314
    }]
})
mock_authed_fetch.return_value.raw = MagicMock()
mock_authed_fetch.return_value.raw.read = lambda: content
mock_authed_fetch.return_value.content = content


class TestDTMMUtils(common.DMSTestCase):
    @patch('google.appengine.api.urlfetch.fetch')
    def test_authed_fetch(self, fetch):
        fetch.return_value.headers = {'x-ratelimit-remaining': 'lots'}
        fetch.return_value.content = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

        import dtmm_utils
        end_data = dtmm_utils.authed_fetch('http://mock.com')
        self.assertEqual(fetch.return_value.content, end_data.content)

        fetch.return_value.headers['x-ratelimit-remaining'] = None
        end_data = dtmm_utils.authed_fetch('http://mock.com')

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

        url_digest = hashlib.md5('http://mock.com').hexdigest()

        memcache.set(url_digest, {'content': 'word'})
        end_data = dtmm_utils.get_url_content(None, 'http://mock.com')
        self.assertEqual(end_data, {'content': 'word'})
        memcache.set(url_digest, None)

        mock_handler = MagicMock()
        mock_authed_fetch.side_effect = urlfetch.DownloadError
        end_data = dtmm_utils.get_url_content(mock_handler, 'http://mock.com')

        self.assertEqual(mock_handler.error.call_args[0][0], 408)

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

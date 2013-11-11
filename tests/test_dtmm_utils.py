import common

import json
import base64
import hashlib
import unittest2
from mock import patch, Mock

from google.appengine.api import memcache, urlfetch


class TestDTMMUtils(common.DMSTestCase):
    @patch('google.appengine.api.urlfetch.fetch', autospec=True)
    def test_authed_fetch_with_remaining(self, fetch):
        fetch.return_value.headers = {'x-ratelimit-remaining': 'lots'}
        fetch.return_value.content = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

        import dtmm_utils
        end_data = dtmm_utils.authed_fetch('http://mock.com')
        self.assertEqual(fetch.return_value.content, end_data.content)

        fetch.assert_called_with(
            url='http://mock.com?client_auth_data=%7Bu%27client_secret%27%3A+u%27false_data%27%2C+u%27client_id%27%3A+u%27false_data%27%7D',
            headers={'X-Admin-Contact': 'admin@lysdev.com'}
        )

    @patch('google.appengine.api.urlfetch.fetch', autospec=True)
    def test_authed_fetch_without_remaining(self, fetch):
        fetch.return_value.headers = {'x-ratelimit-remaining': None}
        fetch.return_value.content = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

        import dtmm_utils
        dtmm_utils.authed_fetch('http://mock.com')

        fetch.assert_called_with(
            url='http://mock.com?client_auth_data=%7Bu%27client_secret%27%3A+u%27false_data%27%2C+u%27client_id%27%3A+u%27false_data%27%7D',
            headers={'X-Admin-Contact': 'admin@lysdev.com'}
        )
        # a little unsure how to ensure correct behaviour here

    @patch('dtmm_utils.authed_fetch')
    def test_get_url_content_fetch_from_remote(self, mock_authed_fetch):
        url = 'http://mock.com'
        content = {
            u'tree': [{
                u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'mode': u'100644',
                u'path': u'README.md',
                u'type': u'blob',
                u'size': 314
            }]
        }
        mock_authed_fetch.return_value.content = json.dumps(content)

        import dtmm_utils
        end_data = dtmm_utils.get_url_content(None, url)
        self.assertEqual(end_data, content)

        mock_authed_fetch.assert_called_with(url)
        self.assertEqual(
            memcache.get(hashlib.md5(url).hexdigest()),
            content
        )

    def test_get_url_content_retrieve_from_memcache(self):
        import dtmm_utils

        url_digest = hashlib.md5('http://mock.com').hexdigest()

        memcache.set(url_digest, {'content': 'word'})
        end_data = dtmm_utils.get_url_content(None, 'http://mock.com')
        self.assertEqual(end_data, {'content': 'word'})

    @patch('dtmm_utils.authed_fetch', autospec=True)
    @patch('logging.error', autospec=True)
    def test_get_url_content_download_error_handling(self, _, authed_fetch):
        authed_fetch.side_effect = urlfetch.DownloadError

        import dtmm_utils

        mock_handler = Mock()
        dtmm_utils.get_url_content(mock_handler, 'http://mock.com')

        mock_handler.error.assert_called_with(408)

    @patch('dtmm_utils.authed_fetch')
    def test_get_tree(self, mock_authed_fetch):
        content = {
            'tree': [{
                u'sha': u'ac178f6489f2d3f601df6a9a5e641b62a0388eae',
                u'mode': u'100644',
                u'path': u'README.md',
                u'type': u'blob',
                u'size': 314
            }]
        }
        mock_authed_fetch.return_value.content = json.dumps(content)

        import dtmm_utils
        end_data = dtmm_utils.get_tree()
        self.assertEqual(end_data, content['tree'])

    @patch('dtmm_utils.get_url_content', autospec=True)
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

    @patch('dtmm_utils.get_url_content', autospec=True)
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

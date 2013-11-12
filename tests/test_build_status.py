import common
import test_data

import json
from mock import patch, DEFAULT, Mock

from google.appengine.api import memcache


@patch('dtmm_utils.get_url_content', autospec=True)
class TestBuildStatus(common.DMSHandlerTestCase):
    def test_build_status_passing(self, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = {'-1': {'text': 'successful'}}
            self.testapp.get(url)

            self.assertEqualMemcache('build_status_' + platform, 'passing')

    def test_build_status_failing(self, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:

            get_url_content.return_value = {'-1': {'text': 'failed'}}
            self.testapp.get(url)

            self.assertEqualMemcache('build_status_' + platform, 'failing')

    def test_build_status_unknown_with_bad_data(self, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = []
            self.testapp.get(url)

            self.assertEqualMemcache('build_status_' + platform, 'unknown')

    def test_build_status_unknown_with_no_status(self, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = {'-1': {'text': 'garbage'}}
            self.testapp.get(url)

            self.assertEqualMemcache('build_status_' + platform, 'unknown')

    def test_build_status_invalid_platfrom(self, _):
        self.testapp.get('/status/invalid.png')

        values = memcache.get_multi(test_data.PLATFORMS, 'build_status_')
        self.assertTrue(not any(values))

if __name__ == '__main__':
    common.main()

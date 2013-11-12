import common
import test_data

import os
from mock import patch, ANY, MagicMock

from google.appengine.api import memcache


@patch('dtmm_utils.get_url_content', autospec=True)
@patch('build_status.BuildStatusHandler.notify_status', autospec=True)
class TestBuildStatus(common.DMSHandlerTestCase):
    def test_build_status_passing(self, notify_status, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = {'-1': {'text': 'successful'}}
            self.testapp.get(url)

            notify_status.assert_called_with(ANY, 'passing')

    def test_build_status_failing(self, notify_status, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:

            get_url_content.return_value = {'-1': {'text': 'failed'}}
            self.testapp.get(url)

            notify_status.assert_called_with(ANY, 'failing')

    def test_build_status_unknown_with_bad_data(self, notify_status, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = []
            self.testapp.get(url)

            notify_status.assert_called_with(ANY, 'unknown')

    def test_build_status_unknown_with_no_status(self, notify_status, get_url_content):
        for platform, url in test_data.PLATFORM_W_URLS:
            get_url_content.return_value = {'-1': {'text': 'garbage'}}
            self.testapp.get(url)

            notify_status.assert_called_with(ANY, 'unknown')

    def test_build_status_invalid_platfrom(self, notify_status, _):
        self.testapp.get('/status/invalid.png')

        values = memcache.get_multi(test_data.PLATFORMS, 'build_status_')
        self.assertTrue(not any(values))

    def test_build_status_with_memcache(self, notify_status, _):
        memcache.set('build_status_linux', 'unknown')
        self.testapp.get('/status/linux.png')

        notify_status.assert_called_with(ANY, 'unknown')


@patch('webapp2.RequestHandler.response', autospec=True)
class TestNotifyStatus(common.DMSTestCase):
    def test_notify_status(self, response):
        path = os.path.join(os.path.dirname(__file__), '../src/results/passing.png')
        with open(path, 'rb') as fh:
            data = fh.read()

        import build_status
        handler = build_status.BuildStatusHandler(MagicMock(), MagicMock())
        handler.notify_status('passing')

        handler.response.write.assert_called_with(data)


if __name__ == '__main__':
    common.main()

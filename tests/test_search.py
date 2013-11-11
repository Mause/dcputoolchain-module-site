import common

import base64
import json
from mock import patch, Mock, MagicMock


mock_get_tree = Mock(return_value=[{
    u'url': '',
    u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
    u'mode': u'100644',
    u'path': u'hmd2043.lua',
    u'type': u'blob',
    u'size': 3979
}])


mock_fetch = MagicMock()
mock_fetch.return_value.content = json.dumps({'content': base64.b64encode(
    '''
    MODULE = {
        Type = "Hardware",
        Name = "HMD2043",
        Version = "1.1",
        SDescription = "Deprecated HMD2043 hardware device",
        URL = "False URL"
    };'''
)})


@patch('google.appengine.api.urlfetch.fetch', mock_fetch)
@patch('dtmm_utils.get_tree', mock_get_tree)
class TestSearch(common.DMSTestCase):
    def test_search_with_type(self, *args, **kwargs):
        import humans

        end_data = humans.search(None, 'query', '')
        self.assertEqual(end_data, [])

        end_data = humans.search(None, 'hmd', '')
        self.assertEqual(
            end_data,
            [{
                u'url': '',
                u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
                u'mode': u'100644',
                u'path': u'hmd2043.lua',
                u'type': u'blob',
                u'size': 3979}])

    def test_search_without_type(self):
        import humans

        end_data = humans.search(None, 'query', 'hardware')
        self.assertEqual(end_data, [])

        end_data = humans.search(None, 'HMD2043')
        self.assertEqual(
            end_data,
            [{
                u'url': u'',
                u'sha': u'7cc95910b367f08159cf207c08918ae5d4c04bb5',
                u'mode': u'100644',
                u'path': u'hmd2043.lua',
                u'type': u'blob',
                u'size': 3979}])

if __name__ == '__main__':
    common.main()

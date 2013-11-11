import common

import webtest
from mock import patch
from google.appengine.api import memcache


@patch('dtmm_utils.get_modules', autospec=True)
@patch('dtmm_utils._get_live_data', lambda handler, fragment: common.DATA_TREE_DATA)
class TestPrettyTree(common.DMSTestCase):
    def setUp(self, *args, **kwargs):
        super(TestPrettyTree, self).setUp(*args, **kwargs)

        from main import app
        self.testapp = webtest.TestApp(app)

    def test_human_tree_pretty_single_module(self, get_modules):
        get_modules.return_value = [{'path': 'assert.lua'}]

        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_rows(self, get_modules):
        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'},
            {'path': 'four.lua'},
            {'path': 'five.lua'}
        ]

        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_single_row(self, get_modules):

        get_modules.return_value = [
            {'path': 'assert.lua'},
            {'path': 'assertdb.lua'},
            {'path': 'assertpp.lua'}
        ]
        self.testapp.get('/human/tree/pretty')

    def test_human_tree_pretty_memcache(self, _):
        memcache.set(
            'pretty_tree_tree',
            [
                {
                    u'index': 0,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assert.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware',
                    u'row': False
                },
                {
                    u'index': 1,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assertdb.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware', u'row': False
                },
                {
                    u'index': 2,
                    'Version': '1.1',
                    'Name': 'HMD2043',
                    'URL': 'False URL',
                    u'filename': u'assertpp.lua',
                    u'width': 300.0,
                    'SDescription': 'Deprecated HMD2043 hardware device',
                    'Type': 'Hardware', u'row': False
                }
            ]
        )
        memcache.set(
            'pretty_tree_calc',
            {
                u'cell_height': 80,
                u'height': 100,
                u'width': 900,
                u'outer_container_height': 100,
                u'margin_height': 50.0,
                u'margin_width': 450.0
            }
        )

        self.testapp.get('/human/tree/pretty')

if __name__ == '__main__':
    common.main()

# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import copy
import urllib
import webtest
import unittest2
import itertools
from mock import patch

# this needs to be done before anything to do with gae gets imported
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()

# these next two lines might be broken in the future. not sure what ill do after that :(
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import testbed
from google.appengine.api import memcache


class Test_Handlers(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dev~dcputoolchain-module-site')
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_mail_stub()
        memcache.set('client_auth_data',
            {u'client_auth_data': {u'client_secret': u'false_data', u'client_id': u'false_data'}})

        from main import app
        self.testapp = webtest.TestApp(app)

        def mock_get_tree(handler):
            return [{
                u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
                u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
                u'mode': u'100644',
                u'path': u'assert.lua',
                u'type': u'blob',
                u'size': 823}]

        get_tree_patcher = patch('dtmm_utils.get_tree', mock_get_tree)
        get_tree_patcher.start()

    def tearDown(self):
        self.testbed.deactivate()

    def test_human_tree_pretty(self):
        # /human/tree/pretty
        self.testapp.get('/human/tree/pretty')

    def test_human_tree(self):
        # human tree
        self.testapp.get('/human/tree')

    def test_human_search(self):
        # /human/search

        self.testapp.get('/human/search')

        queries = ['', 'random', 'words']
        import humans
        custom_module_types = copy.copy(humans.module_types)
        custom_module_types.append('')
        subtests = itertools.product(queries, custom_module_types)

        for sub in subtests:
            cur_url = '/human/search?' + urllib.urlencode(
                {'q': sub[0],
                'type': sub[1]})
            self.testapp.get(cur_url)

    def test_human_listing(self):
        self.testapp.get('/human/listing')

    def test_human_inspect(self):
        self.testapp.get('/human/inspect?name=assert.lua')

    def test_human(self):
        self.testapp.get('/human')

    def test_modules(self):
        pass
        # TODO: check for redirect

    def test_modules_search(self):
        pass


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

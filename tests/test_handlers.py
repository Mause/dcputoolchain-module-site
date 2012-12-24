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
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_mail_stub()
        memcache.set('client_auth_data',
            {u'client_auth_data': {u'client_secret': u'false_data', u'client_id': u'false_data'}})

        def mock_get_tree(handler):
            return [{
                u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
                u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
                u'mode': u'100644',
                u'path': u'assert.lua',
                u'type': u'blob',
                u'size': 823}]
        self.get_tree_patcher = patch('dtmm_utils.get_tree', mock_get_tree)
        self.get_tree_patcher.start()

        def mock_get_url_content(handler, url):
            # assert url == 'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225'
            return {
                "url": "https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225",
                      "content": "ZnVuY3Rpb24gYXNzZXJ0X2hhbmRsZXIoc3RhdGUsIHBhcmFtcykKICAtLSB3\nZSBleHBlY3QgYSBzaW5nbGUgcGFyYW1ldGVyIHRoYXQgaXMgYW4gZXhwcmVz\nc2lvbi4KICBpZiAoI3BhcmFtcyB+PSAxIG9yIChwYXJhbXNbMV0udHlwZSB+\nPSAiU1RSSU5HIiBhbmQgcGFyYW1zWzFdLnR5cGUgfj0gIkVYUFJFU1NJT04i\nKSkgdGhlbgogICAgZXJyb3IoImVycm9yOiAuQVNTRVJUIGRpcmVjdGl2ZSBl\neHBlY3RzIHNpbmdsZSBleHByZXNzaW9uIHBhcmFtZXRlci4iKQogIGVuZAog\nIGxvY2FsIGV4cHIgPSBuaWw7CiAgaWYgKHBhcmFtc1sxXS50eXBlID09ICJT\nVFJJTkciKSB0aGVuCiAgICBleHByID0gZXhwcmVzc2lvbl9jcmVhdGUocGFy\nYW1zWzFdLnZhbHVlKTsKICBlbHNlCiAgICBleHByID0gcGFyYW1zWzFdLnZh\nbHVlCiAgZW5kCgogIC0tIG91dHB1dCBhIHN5bWJvbCBmb3IgdGhlIGV4cHJl\nc3Npb24uCiAgc3RhdGU6YWRkX3N5bWJvbCgiYXNzZXJ0aW9uOiIgLi4gZXhw\ncjpyZXByZXNlbnRhdGlvbigpKTsKZW5kCgpmdW5jdGlvbiBzZXR1cCgpCiAg\nLS0gcGVyZm9ybSBzZXR1cAogIGFkZF9wcmVwcm9jZXNzb3JfZGlyZWN0aXZl\nKCJBU1NFUlQiLCBhc3NlcnRfaGFuZGxlciwgZmFsc2UsIHRydWUpCmVuZAoK\nTU9EVUxFID0gewogIFR5cGUgPSAiUHJlcHJvY2Vzc29yIiwKICBOYW1lID0g\nIi5BU1NFUlQgZGlyZWN0aXZlIiwKICBWZXJzaW9uID0gIjEuMCIsCiAgU0Rl\nc2NyaXB0aW9uID0gIlRoZSAuQVNTRVJUIGRpcmVjdGl2ZSIsCiAgVVJMID0g\nImh0dHA6Ly9kY3B1dG9vbGNoYS5pbi9kb2NzL21vZHVsZXMvbGlzdC9hc3Nl\ncnQuaHRtbCIKfTsKCg==\n",
                      "sha": "443f114dceaca63eda1771fbf61d55cf85685225",
                      "size": 823,
                      "encoding": "base64"
                }
        self.get_url_content_patcher = patch('dtmm_utils.get_url_content', mock_get_url_content)
        self.get_url_content_patcher.start()


        from main import app
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.get_tree_patcher.stop()
        self.get_url_content_patcher.stop()
        self.testbed.deactivate()

    def test_get_tree(self):
        "testing /human/tree/pretty handler"
        import dtmm_utils
        dtmm_utils.get_tree(0)

    def test_human_tree_pretty(self):
        "testing /human/tree/pretty handler"
        self.testapp.get('/human/tree/pretty')

    def test_human_tree(self):
        "testing /human/tree handler"
        self.testapp.get('/human/tree')

    def test_human_search(self):
        "testing /human/search handler"

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
        "testing /human/listing handler"
        self.testapp.get('/human/listing')

    def test_human_inspect(self):
        "testing /human/inspect handler"
        self.testapp.get('/human/inspect?name=assert.lua')

    def test_human(self):
        "testing /human handler"
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

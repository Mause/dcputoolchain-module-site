CLIENT_AUTH_DATA = {
    u'client_auth_data': {
        u'client_secret': u'false_data',
        u'client_id': u'false_data'
    }
}

TEST_HANDLERS_URL_CONTENT = {
    "url": "https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225",
    "content": "ZnVuY3Rpb24gYXNzZXJ0X2hhbmRsZXIoc3RhdGUsIHBhcmFtcykKICAtLSB3\nZSBleHBlY3QgYSBzaW5nbGUgcGFyYW1ldGVyIHRoYXQgaXMgYW4gZXhwcmVz\nc2lvbi4KICBpZiAoI3BhcmFtcyB+PSAxIG9yIChwYXJhbXNbMV0udHlwZSB+\nPSAiU1RSSU5HIiBhbmQgcGFyYW1zWzFdLnR5cGUgfj0gIkVYUFJFU1NJT04i\nKSkgdGhlbgogICAgZXJyb3IoImVycm9yOiAuQVNTRVJUIGRpcmVjdGl2ZSBl\neHBlY3RzIHNpbmdsZSBleHByZXNzaW9uIHBhcmFtZXRlci4iKQogIGVuZAog\nIGxvY2FsIGV4cHIgPSBuaWw7CiAgaWYgKHBhcmFtc1sxXS50eXBlID09ICJT\nVFJJTkciKSB0aGVuCiAgICBleHByID0gZXhwcmVzc2lvbl9jcmVhdGUocGFy\nYW1zWzFdLnZhbHVlKTsKICBlbHNlCiAgICBleHByID0gcGFyYW1zWzFdLnZh\nbHVlCiAgZW5kCgogIC0tIG91dHB1dCBhIHN5bWJvbCBmb3IgdGhlIGV4cHJl\nc3Npb24uCiAgc3RhdGU6YWRkX3N5bWJvbCgiYXNzZXJ0aW9uOiIgLi4gZXhw\ncjpyZXByZXNlbnRhdGlvbigpKTsKZW5kCgpmdW5jdGlvbiBzZXR1cCgpCiAg\nLS0gcGVyZm9ybSBzZXR1cAogIGFkZF9wcmVwcm9jZXNzb3JfZGlyZWN0aXZl\nKCJBU1NFUlQiLCBhc3NlcnRfaGFuZGxlciwgZmFsc2UsIHRydWUpCmVuZAoK\nTU9EVUxFID0gewogIFR5cGUgPSAiUHJlcHJvY2Vzc29yIiwKICBOYW1lID0g\nIi5BU1NFUlQgZGlyZWN0aXZlIiwKICBWZXJzaW9uID0gIjEuMCIsCiAgU0Rl\nc2NyaXB0aW9uID0gIlRoZSAuQVNTRVJUIGRpcmVjdGl2ZSIsCiAgVVJMID0g\nImh0dHA6Ly9kY3B1dG9vbGNoYS5pbi9kb2NzL21vZHVsZXMvbGlzdC9hc3Nl\ncnQuaHRtbCIKfTsKCg==\n",
    "sha": "443f114dceaca63eda1771fbf61d55cf85685225",
    "size": 823,
    "encoding": "base64"
}

TEST_GET_TREE = TEST_HANDLERS_GET_TREE = [{
    u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
    u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
    u'mode': u'100644',
    u'path': u'assert.lua',
    u'type': u'blob',
    u'size': 823
}]

DATA_TREE_DATA = '''
MODULE = {
    Type = "Hardware",
    Name = "HMD2043",
    Version = "1.1",
    SDescription = "Deprecated HMD2043 hardware device",
    URL = "False URL"
};
HARDWARE = {
    ID = 0x74fa4cae,
    Version = 0x07c2,
    Manufacturer = 0x21544948 -- HAROLD_IT
};'''


PLATFORMS = ['linux', 'mac', 'windows']
PLATFORM_URLS = ['/status/{}.png'.format(platform) for platform in PLATFORMS]

PLATFORM_W_URLS = list(zip(PLATFORMS, PLATFORM_URLS))

# setup the test environment
import os
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# this needs to be done before anything to do with gae gets imported
from run_tests import setup_environ
setup_environ()

import unittest2
from google.appengine.ext import testbed
from google.appengine.api import memcache


class DMSTestCase(unittest2.TestCase):
    def setUp(self):
        # setup the testbed
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(
            APPENGINE_RUNTIME='python27',
            app_id='dcputoolchain-module-site'
        )
        self.testbed.activate()

        # initiate the stubs
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

        # setup data
        memcache.set('client_auth_data', CLIENT_AUTH_DATA)

    def tearDown(self):
        self.testbed.deactivate()


def main():
    unittest2.main()

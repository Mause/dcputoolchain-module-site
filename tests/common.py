client_auth_data = {
    u'client_auth_data': {
        u'client_secret': u'false_data',
        u'client_id': u'false_data'
    }
}

test_handlers_url_content = {
    "url": "https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225",
    "content": "ZnVuY3Rpb24gYXNzZXJ0X2hhbmRsZXIoc3RhdGUsIHBhcmFtcykKICAtLSB3\nZSBleHBlY3QgYSBzaW5nbGUgcGFyYW1ldGVyIHRoYXQgaXMgYW4gZXhwcmVz\nc2lvbi4KICBpZiAoI3BhcmFtcyB+PSAxIG9yIChwYXJhbXNbMV0udHlwZSB+\nPSAiU1RSSU5HIiBhbmQgcGFyYW1zWzFdLnR5cGUgfj0gIkVYUFJFU1NJT04i\nKSkgdGhlbgogICAgZXJyb3IoImVycm9yOiAuQVNTRVJUIGRpcmVjdGl2ZSBl\neHBlY3RzIHNpbmdsZSBleHByZXNzaW9uIHBhcmFtZXRlci4iKQogIGVuZAog\nIGxvY2FsIGV4cHIgPSBuaWw7CiAgaWYgKHBhcmFtc1sxXS50eXBlID09ICJT\nVFJJTkciKSB0aGVuCiAgICBleHByID0gZXhwcmVzc2lvbl9jcmVhdGUocGFy\nYW1zWzFdLnZhbHVlKTsKICBlbHNlCiAgICBleHByID0gcGFyYW1zWzFdLnZh\nbHVlCiAgZW5kCgogIC0tIG91dHB1dCBhIHN5bWJvbCBmb3IgdGhlIGV4cHJl\nc3Npb24uCiAgc3RhdGU6YWRkX3N5bWJvbCgiYXNzZXJ0aW9uOiIgLi4gZXhw\ncjpyZXByZXNlbnRhdGlvbigpKTsKZW5kCgpmdW5jdGlvbiBzZXR1cCgpCiAg\nLS0gcGVyZm9ybSBzZXR1cAogIGFkZF9wcmVwcm9jZXNzb3JfZGlyZWN0aXZl\nKCJBU1NFUlQiLCBhc3NlcnRfaGFuZGxlciwgZmFsc2UsIHRydWUpCmVuZAoK\nTU9EVUxFID0gewogIFR5cGUgPSAiUHJlcHJvY2Vzc29yIiwKICBOYW1lID0g\nIi5BU1NFUlQgZGlyZWN0aXZlIiwKICBWZXJzaW9uID0gIjEuMCIsCiAgU0Rl\nc2NyaXB0aW9uID0gIlRoZSAuQVNTRVJUIGRpcmVjdGl2ZSIsCiAgVVJMID0g\nImh0dHA6Ly9kY3B1dG9vbGNoYS5pbi9kb2NzL21vZHVsZXMvbGlzdC9hc3Nl\ncnQuaHRtbCIKfTsKCg==\n",
    "sha": "443f114dceaca63eda1771fbf61d55cf85685225",
    "size": 823,
    "encoding": "base64"
}

test_handlers_get_tree = [{
    u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
    u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
    u'mode': u'100644',
    u'path': u'assert.lua',
    u'type': u'blob',
    u'size': 823
}]

import unittest2
from google.appengine.ext import testbed
from google.appengine.api import memcache


class DMSTestCase(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        memcache.set('client_auth_data', client_auth_data)

    def tearDown(self):
        self.testbed.deactivate()

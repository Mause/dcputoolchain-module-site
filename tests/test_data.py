# The MIT License (MIT)

# Copyright (c) 2013 Dominic May

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

TEST_GET_MODULES = [{
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

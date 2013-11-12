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

# setup the test environment
import os
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, os.path.join('..', 'src'))

import webtest
import test_data
import unittest2


def setup_environ():
    if hasattr(setup_environ, '_is_setup'):
        return
    else:
        setup_environ._is_setup = True

    POSSIBLE_LOCATIONS = [
        'C:\\Program Files (x86)\\Google\\google_appengine\\',
        '~/.google_appengine/',
        '.'
    ]

    # locate app-engine SDK
    POSSIBLE_LOCATIONS = map(os.path.expanduser, POSSIBLE_LOCATIONS)
    POSSIBLE_LOCATIONS = filter(os.path.exists, POSSIBLE_LOCATIONS)
    POSSIBLE_LOCATIONS = filter(os.path.isdir, POSSIBLE_LOCATIONS)
    POSSIBLE_LOCATIONS = filter(
        lambda path: os.path.exists(os.path.join(path, 'appcfg.py')),
        POSSIBLE_LOCATIONS
    )
    sys.path.append(POSSIBLE_LOCATIONS[0])

    import dev_appserver
    dev_appserver.fix_sys_path()


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
        memcache.set('client_auth_data', test_data.CLIENT_AUTH_DATA)

    def tearDown(self):
        self.testbed.deactivate()


class DMSHandlerTestCase(DMSTestCase):
    def setUp(self, *args, **kwargs):
        super(DMSHandlerTestCase, self).setUp(*args, **kwargs)

        from main import app
        self.testapp = webtest.TestApp(app)


# this needs to be done before anything to do with gae gets imported
setup_environ()
from google.appengine.ext import testbed
from google.appengine.api import memcache


def main():
    unittest2.main()

# setup the test environment
import os
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, os.path.join('..', 'src'))

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


# this needs to be done before anything to do with gae gets imported
setup_environ()
from google.appengine.ext import testbed
from google.appengine.api import memcache


def main():
    unittest2.main()

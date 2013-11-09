from __future__ import print_function

# setup the test environment
import sys
import os
import time


def setup_environ():
    # locate app-engine SDK
    AE_PATH = "."

    # path to app code
    APP_PATH = os.path.abspath(".")

    # load the AE paths (as stolen from dev_appserver.py)
    EXTRA_PATHS = [
        APP_PATH,
        AE_PATH,
        os.path.join(AE_PATH, 'lib', 'antlr3'),
        os.path.join(AE_PATH, 'lib', 'django'),
        os.path.join(AE_PATH, 'lib', 'ipaddr'),
        os.path.join(AE_PATH, 'lib', 'webob'),
        os.path.join(AE_PATH, 'lib', 'yaml', 'lib'),
        os.path.join(AE_PATH, 'lib', 'fancy_urllib'),
        os.path.join(os.getcwd(), 'src'),
        os.path.join(os.getcwd(), '..', 'src'),
        os.path.join(os.getcwd(), 'google_appengine'),
        'C:\\Program Files (x86)\\Google\\google_appengine\\',
        '/home/dominic/.google_appengine/',
        '/home/action/.google_appengine/'
    ]
    sys.path = EXTRA_PATHS + sys.path

    import dev_appserver
    dev_appserver.fix_sys_path()

setup_environ()

# unit testing specific imports
import unittest2

# unit test subunits
SUB_UNITS = [
    'test_humans',
    'test_dtmm_utils',
    'test_handlers',
    'test_module_utils'
]


def main():
    loader = unittest2.TestLoader()
    suite = loader.loadTestsFromNames(SUB_UNITS)

    runner = unittest2.TextTestRunner(verbosity=2)
    # wait a second or so for things to start
    time.sleep(2)
    end = runner.run(suite)
    if len(end.errors) > 0 or len(end.failures) > 0:
        sys.exit('{} errors appear to have occured.'.format(len(end.errors)))

if __name__ == '__main__':
    main()

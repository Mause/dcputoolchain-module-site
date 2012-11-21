
# setup the test environment
import sys
import os


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
        os.path.join(AE_PATH, 'lib', 'fancy_urllib'),  # issue[1]
    ]
    sys.path = EXTRA_PATHS + sys.path

    sys.path.insert(0, 'src')
    sys.path.insert(0, '..%ssrc' % os.sep)
    sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

    import dev_appserver
    dev_appserver.fix_sys_path()

setup_environ()

# unit testing specific imports
import unittest2

import test_humans
import test_dtmm_utils
import test_main


def main():
    loader = unittest2.TestLoader()
    suite = loader.loadTestsFromModule(test_humans)
    suite.addTests(loader.loadTestsFromModule(test_dtmm_utils))
    suite.addTests(loader.loadTestsFromModule(test_main))
    # print suite.__dict__
    runner = unittest2.TextTestRunner(verbosity=2)
    runner.run(suite)
    # unittest2.main()

if __name__ == '__main__':
    main()

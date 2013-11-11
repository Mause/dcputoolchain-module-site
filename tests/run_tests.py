from __future__ import print_function

# setup the test environment
import sys
import time
import unittest2

# unit test subunits
SUB_UNITS = [
    'test_humans',
    'test_dtmm_utils',
    'test_handlers',
    'test_module_utils',
    'test_pretty_tree',
    'test_search'
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
    import common
    common.setup_environ()

    main()

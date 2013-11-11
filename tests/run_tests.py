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

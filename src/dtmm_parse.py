#!/usr/bin/env python
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


from __future__ import (
    division,
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    with_statement
)

import os
import sys
import argparse
from module_utils import get_module_data, get_hardware_data


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('filename', metavar='filename', type=str)
    args = parser.parse_args()

    if os.path.exists(sys.argv[1]):
        with open(args.filename, 'r') as fh:
            data = fh.read()
        module_data = get_module_data(data)
        print('Name:', module_data['Name'])
        print('Type:', module_data['Type'])
        print('Version:', module_data['Version'])
        print
        if module_data['Type'].lower() == 'hardware':
            hardware_data = get_hardware_data(data)
            print('Hardware Version:', hardware_data['Version'])
            print('Hardware ID:', hardware_data['ID'])
            print('Hardware Manufacturer:', hardware_data['Manufacturer'])
    else:
        print('File could not be found')

if __name__ == '__main__':
    main()

#!/usr/bin/env python
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

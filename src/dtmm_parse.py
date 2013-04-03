#!/usr/bin/env python
from __future__ import print_function

import os
import re
import sys
from slpp import slpp as lua


def get_hardware_data(data):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    hardware_data = (
        re.search('HARDWARE\s*=\s*(?P<data>\{[^}]*\})',
                  data))
    if hardware_data:
        hardware_data = lua.decode(hardware_data.groupdict()['data'])
        return hardware_data
    else:
        return {}


def get_module_data(data):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    module_data = (
        re.search('MODULE\s*=\s*(?P<data>\{[^}]*\})',
                  data))
    if module_data:
        module_data = lua.decode(module_data.groupdict()['data'])
        return module_data
    else:
        return {}


def main():
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as fh:
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
    else:
        print("This program requires at least one argument")

if __name__ == '__main__':
    main()

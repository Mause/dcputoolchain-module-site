#!/usr/bin/env python
import os
import re
import sys
import logging
from slpp import slpp as lua


def get_hardware_data(data):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    hardware_data = (
        re.search('HARDWARE\s*=\s*\{([^}]*)\}',
                  data))
    try:
        hardware_data = hardware_data.group(0)
        hardware_data = hardware_data.strip('HARDWARE=')
        hardware_data = hardware_data.strip('HARDWARE =')
        hardware_data = lua.decode(hardware_data)
    except AttributeError:
        logging.info('hardware_data: ' + str(hardware_data))
    new_output = {}
    new_output['Version'] = hardware_data[1]
    new_output['ID'] = hardware_data[3]
    new_output['Manufacturer'] = hardware_data[5]
    return new_output


def get_module_data(data):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    module_data = (
        re.search('MODULE\s*=\s*\{([^}]*)\}',
                  data))
    try:
        module_data = module_data.group(0)
        module_data = module_data.strip('MODULE=')
        module_data = module_data.strip('MODULE =')
        module_data = lua.decode(module_data)
    except AttributeError:
        logging.info('module_data: ' + str(module_data))
    return module_data


def main():
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as fh:
                data = fh.read()
            module_data = get_module_data(data)
            print 'Name:', module_data['Name']
            print 'Type:', module_data['Type']
            print 'Version:', module_data['Version']
            print
            if module_data['Type'].lower() == 'hardware':
                hardware_data = get_hardware_data(data)
                print 'Hardware Version:', hardware_data['Version']
                print 'Hardware ID:', hardware_data['ID']
                print 'Hardware Manufacturer:', hardware_data['Manufacturer']
        else:
            print 'File could not be found'
    else:
        print "This program requires at least one argument"

if __name__ == '__main__':
    main()

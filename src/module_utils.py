import re
from slpp import slpp as lua

HARDWARE_RE = re.compile(r'HARDWARE\s*=\s*(?P<data>\{[^}]*\})')
MODULE_RE = re.compile(r'MODULE\s*=\s*(?P<data>\{[^}]*\})')


def generic_get_module_data(module, REGEX):
    data = REGEX.search(module)

    return lua.decode(data.groupdict()['data']) if data else {}


def get_hardware_data(data):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    return generic_get_module_data(data, HARDWARE_RE)


def get_module_data(data):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    return generic_get_module_data(data, MODULE_RE)

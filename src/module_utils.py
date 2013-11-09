import re
import base64
from slpp import slpp as lua


def generic_get_module_data(module, regex):
    data = base64.b64decode(module['content'])
    data = re.search(regex, data)

    return lua.decode(data.groupdict()['data']) if data else {}


def get_hardware_data(data):
    """Given a get_tree fragment,
    returns hardware data in a python dict"""
    return generic_get_module_data(data, r'HARDWARE\s*=\s*(?P<data>\{[^}]*\})')


def get_module_data(data):
    """Given a get_tree fragment,
    returns module data in a python dict"""
    return generic_get_module_data(data, r'MODULE\s*=\s*(?P<data>\{[^}]*\})')

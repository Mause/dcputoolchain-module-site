import common
import test_data

# unit testing specific imports
import unittest2
from mock import patch, MagicMock


class TestHumans(common.DMSTestCase):
    def test_gen_types_with_selected(self):
        import humans
        end_data = humans.gen_types()

        self.assertEqual(
            end_data,
            [
                {'selected': False, 'name': 'preprocessor'},
                {'selected': False, 'name': 'debugger'},
                {'selected': False, 'name': 'hardware'},
                {'selected': False, 'name': 'optimizer'}
            ]
        )

    def test_gen_types_without_selected(self):
        import humans

        end_data = humans.gen_types(selected='optimizer')

        self.assertEqual(
            end_data,
            [
                {'selected': False, 'name': 'preprocessor'},
                {'selected': False, 'name': 'debugger'},
                {'selected': False, 'name': 'hardware'},
                {'selected': True, 'name': 'optimizer'}
            ]
        )

    def test_pretty_colours(self):
        import re
        import humans
        import random

        output = humans.pretty_colours(random.randint(200, 500))

        for colour in output:
            self.assertTrue(re.match(
                r'rgb\(\d+?, \d+?, \d+?\)', colour))

    @patch('dtmm_utils._get_live_data', lambda handler, fragment: test_data.DATA_TREE_DATA)
    def test_data_tree(self):
        import humans

        humans.data_tree(MagicMock(), [
            {'path': 'assert.lua', 'url': 'mock'},
            {'path': 'assert.py'}
        ])


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

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

import common


class TestModuleUtils(common.DMSTestCase):
    def test_get_module_data(self):
        data = \
            '''
            MODULE = {
                Type = "Hardware",
                Name = "HMD2043",
                Version = "1.1",
                SDescription = "Deprecated HMD2043 hardware device",
                URL = "False URL"
            };'''

        import module_utils
        end_data = module_utils.get_module_data(data)
        self.assertEqual(
            end_data,
            {
                'URL': 'False URL',
                'SDescription': 'Deprecated HMD2043 hardware device',
                'Version': '1.1',
                'Type': 'Hardware',
                'Name': 'HMD2043'
            }
        )

    def test_get_hardware_data(self):
        data = \
            '''
            HARDWARE = {
                ID = 0x74fa4cae,
                Version = 0x07c2,
                Manufacturer = 0x21544948 -- HAROLD_IT
            };'''

        import module_utils
        end_data = module_utils.get_hardware_data(data)
        self.assertEqual(
            end_data,
            {
                'Version': 1986,
                'ID': 1962560686,
                'Manufacturer': 559171912
            }
        )

if __name__ == '__main__':
    common.main()

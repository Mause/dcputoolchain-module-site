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

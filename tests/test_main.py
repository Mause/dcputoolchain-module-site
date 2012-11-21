# import os
# import json
# import base64
import unittest2
from mock import patch
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()
from google.appengine.ext import testbed


class Test_Main(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id='dcputoolchain-module-site')
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

    def test_SearchModuleHandler(self):
        class MockRequestHandler:
            html_output = ''

            class response:
                headers = {}

            class request:
                def write(string):
                    self.html_output += str(string)

        # def get_url_content(handler=None, url=None):
        #     return {'content': base64.b64encode('''
        #                 HARDWARE = {
        #                     ID = 0x74fa4cae,
        #                     Version = 0x07c2,
        #                     Manufacturer = 0x21544948 -- HAROLD_IT
        #                 };''')}

        # patcher = patch(
        #     'dtmm_utils.get_url_content', get_url_content)
        # self.addCleanup(patcher.stop)
        # patcher.start()

        # from tidylib import tidy_document

        import main
        print dir(main)

        html_output = main.SearchModulesHandler.get(MockRequestHandler())
        print html_output
        # document, errors = tidy_document(html_output)
        # self.assertEqual()


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

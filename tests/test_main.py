# import os
# import json
# import base64
import webob
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

    def tearDown(self):
        self.testbed.deactivate()

    def test_SearchModuleHandler(self):
        class Response(webob.Response):
            def write(self, text):
                if not isinstance(text, basestring):
                    text = unicode(text)

                if isinstance(text, unicode) and not self.charset:
                    self.charset = self.default_charset

                super(Response, self).write(text)

            def _get_headers(self):
                """The headers as a dictionary-like object."""
                if self._headers is None:
                    self._headers = []

                return self._headers

            def _set_headers(self, value):
                if hasattr(value, 'items'):
                    value = value.items()
                elif not isinstance(value, list):
                    raise TypeError(
                        'Response headers must be a list or dictionary.')

                self.headerlist = value
                self._headers = None

            headers = property(
                _get_headers, _set_headers, doc=_get_headers.__doc__)

        patcher = patch(
            'main.BaseRequestHandler.response', Response)
        self.addCleanup(patcher.stop)
        patcher.start()

        # from tidylib import tidy_document

        import main
        print dir(main)

        html_output = main.SearchModulesHandler().get()
        print html_output
        # document, errors = tidy_document(html_output)
        # self.assertEqual()


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

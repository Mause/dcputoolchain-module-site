import os
import webtest
# import webapp2
import unittest2
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
        self.testbed.init_mail_stub()

        # well this sucks. have to start the whole server to test the damn thing
        from main import app
        # Wrap the app with WebTest's TestApp.
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def test_SearchModuleHandler(self):
        with open('auth_frag.txt', 'w') as fh:
            fh.write('False_Data')
        response = self.testapp.get('/human/search')
        print [x for x in dir(response) if not x.startswith('_')]
        # request = webapp2.Request.blank('/modules/search')
        # request.method = 'GET'
        # response = request.get_response(main.app)
        # print response
        self.assertEqual(response.status_int, 200)
        from tidylib import tidy_document
        # print html_output
        document, errors = tidy_document(response.body)
        self.assertEqual(len(errors), 0)
        print errors
        os.remove('auth_frag.txt')


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

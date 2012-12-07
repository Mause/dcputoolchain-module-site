# setup the test environment
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '..%ssrc' % os.sep)
sys.path.insert(0, 'C:\\Program Files (x86)\\Google\\google_appengine\\')

# unit testing specific imports
import unittest2
# from mock import patch
import webtest
from mock import patch
if __name__ == '__main__':
    from run_tests import setup_environ
    setup_environ()
# from httpretty import HTTPretty, httprettified
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import testbed
from google.appengine.api import memcache


from main import app
testapp = webtest.TestApp(app)


class Test_Humans(unittest2.TestCase):
    def setUp(self):
        my_testbed = testbed.Testbed()
        my_testbed.activate()
        my_testbed.setup_env(app_id='dev~dcputoolchain-module-site')
        my_testbed.init_memcache_stub()
        my_testbed.init_urlfetch_stub()
        my_testbed.init_mail_stub()
        memcache.set('client_auth_data',
            {u'client_auth_data': {u'client_secret': u'false_data', u'client_id': u'false_data'}})

        def mock_get_tree(handler):
            return [{
                u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
                u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
                u'mode': u'100644',
                u'path': u'assert.lua',
                u'type': u'blob',
                u'size': 823}]

        get_tree_patcher = patch('dtmm_utils.get_tree', mock_get_tree)
        get_tree_patcher.start()

    def tearDown(self):
        self.testbed.deactivate()

    def test_human_tree(self):
        testapp.get('/human/tree')


# @httprettified
# def main():
    # try:
        # test_data = {
        #     u'tree': [{
        #         u'url': u'https://api.github.com/repos/DCPUTeam/DCPUModules/git/blobs/443f114dceaca63eda1771fbf61d55cf85685225',
        #         u'sha': u'443f114dceaca63eda1771fbf61d55cf85685225',
        #         u'mode': u'100644',
        #         u'path': u'assert.lua',
        #         u'type': u'blob',
        #         u'size': 823
        #     }]
        # }

        # HTTPretty.register_uri(HTTPretty.GET,
        #     "https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master",
        #     body=json.dumps(test_data),
        #     status=200)

        # class authed_fetch:
        #     content = json.dumps({"tree": [
        #         {"type": "blob",
        #         "path": "Primary.lua",
        #         "mode": "100644",
        #         "sha": "ac178f6489f2d3f601df6a9a5e641b62a0388eae",
        #         'url': '',
        #         # 'content': base64.b64encode(json.dumps({})),
        #         'content': base64.b64encode('MODULE = {}'),
        #         "size": 314}]})

        #     def __init__(self, url):
        #         print '#' * 500
        #         pass

        #     def __call__(self):
        #         print '#' * 500
        #         return self

        # del dtmm_utils

        # def mock_get_module_data(*args, **kwargs):
        #     print args

        # get_module_data_patcher = patch(
        #     'dtmm_utils.get_module_data', mock_get_module_data)
        # get_module_data_patcher.start()
        # import dtmm_utils

        # print dtmm_utils.get_url_content(None, '')

        # print dtmm_utils.get_module_data(None, {'url': ''})

    # finally:
        # get_tree_patcher.stop()
        # get_module_data_patcher.stop()
        # my_testbed.deactivate()
        # pass


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

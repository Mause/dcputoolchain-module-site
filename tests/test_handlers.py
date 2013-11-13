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
import test_data

# unit testing specific imports
# import json
import base64
import webtest
import unittest2
import itertools
from mock import patch, MagicMock

# from google.appengine.api import memcache


@patch('dtmm_utils.get_modules', lambda handler: test_data.TEST_GET_MODULES)
@patch('dtmm_utils.get_url_content', lambda handler, url: test_data.TEST_HANDLERS_URL_CONTENT)
class TestHandlers(common.DMSHandlerTestCase):
    # human interface
    def test_human_tree(self):
        self.testapp.get('/human/tree')

    def test_human_search(self):
        response = self.testapp.get('/human/search')
        form = response.form

        queries = ['', 'random', 'words']

        import humans
        custom_module_types = humans.module_types + ['']
        subtests = itertools.product(queries, custom_module_types)

        for sub in subtests:
            form.set('q', sub[0])
            form.select('type', sub[1])
            response = form.submit()
            self.assertEqual(response.status, '200 OK')

            response = self.testapp.get(
                '/human/search?',
                {'q': sub[0], 'type': sub[1]}
            )
            self.assertEqual(response.status, '200 OK')

    def test_human_inspect(self):
        self.testapp.get('/human/inspect?name=assert.lua')

    def test_human(self):
        self.testapp.get('/human')

    # machine interface

    def test_search_modules_with_response(self):
        response = self.testapp.get('/modules/search?q=assert')

        self.assertEqual(
            response.body,
            'assert.lua'
        )

    def test_search_modules_without_response(self):
        response = self.testapp.get('/modules/search?q=nonexistant')

        self.assertEqual(response.body, '')

    def test_download_modules_failure(self):
        self.assertRaises(webtest.AppError,
                          self.testapp.get, ('/modules/download'))

    def test_download_modules_success(self):
        response = self.testapp.get('/modules/download', {'name': 'assert.lua'})
        content = base64.b64decode(test_data.TEST_HANDLERS_URL_CONTENT['content'])

        self.assertEqual(response.body, content)

    def test_list_modules(self):
        response = self.testapp.get('/modules/list')
        self.assertEqual('200 OK', response.status)

        self.assertEqual(
            response.body,
            'assert.lua'
        )

    def test_redirect(self):
        self.testapp.get('/')
        self.testapp.post('/')

    def test_root_modules_redirect(self):
        self.testapp.get('/modules')

    def test_flush_handler(self):
        self.testapp.get('/flush')
        self.testapp.post('/flush')


def main():
    unittest2.main()

if __name__ == '__main__':
    main()

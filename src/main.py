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

"""
This is a simple webapp2 based application for the Google App Engine PaaS;
it uses the GitHub API v3 to request one of the numerous available files
within the DCPUModules (http://github.com/DCPUTeam/DCPUModules) repository.
It decodes the json returned by the API and the thence linked to base64 encoded
files and provides said files in their original formats, ready to be served to
the DCPUToolchain executables that make use of them.
"""

from __future__ import (
    division,
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    with_statement
)

# generic imports
import os
import json
import base64
import logging
from operator import itemgetter

# google appengine imports
import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import memcache

# humans.py file
from humans import (
    HomeHandler,
    TreeHandler,
    HumanSearch,
    InspectHandler,
    PrettyTreeHandler,
    RedirectToHumanHandler
)

# the dtmm_utils file
import dtmm_utils

from dtmm_utils import (
    BaseRequestHandler,
    rpart
)


class SearchModulesHandler(BaseRequestHandler):
    "Handle searching of the repo"
    def get(self):
        "Handles get requests"
        query = self.request.get('q')

        filenames = dtmm_utils.get_module_names(self)
        filenames = filter(lambda filename: query in filename, filenames)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        self.response.write('\n'.join(filenames))


class DownloadModulesHandler(BaseRequestHandler):
    "Handles download requests"
    def get(self):
        "Handlers get requests"

        data = dtmm_utils.get_modules(self)

        module_name = self.request.get('name')
        if module_name not in map(itemgetter('path'), data):
            self.error(404)
            return

        data_dict = {
            rpart(fragment['path']): fragment['url']
            for fragment in data
        }

        encoded_content = dtmm_utils.get_url_content(self, data_dict[module_name])
        content = base64.b64decode(encoded_content['content'])

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        self.response.write(content)


class ListModulesHandler(BaseRequestHandler):
    "returns a list of accessable modules"
    def get(self):
        "Handlers get requests"
        modules = dtmm_utils.get_module_names(self)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        self.response.write('\n'.join(modules))


def flusher(handler):
    "Performs a memcache flush"
    memcache.flush_all()
    handler.response.write('Memcache flushed')


class FlushHandler(BaseRequestHandler):
    "Flushes the memcache, like an idiot"
    def get(self):
        flusher(self)

    def post(self):
        flusher(self)


class BuildStatusHandler(BaseRequestHandler):
    def get(self, platform):
        end_status = 'unknown'
        FMT_STRING = 'http://bb.dcputoolcha.in:8080/json/builders/build_{}/builds?select=-1&as_text=1'
        # ensure the platform is valid
        if platform in ['mac', 'linux', 'windows']:
            # create the build status url
            url = FMT_STRING.format(platform)
            logging.info(url)
            # check whether the build status is cached
            cached_status = memcache.get('build_status_%s' % (platform))

            if not cached_status:
                logging.info('Okay, no cached status, hitting the buildbot')

                content = None
                try:
                    # try to pull build status from the buildbot
                    content = urlfetch.fetch(url).content
                    raw_data = json.loads(content)
                except urlfetch.DownloadError:
                    logging.info('Could not get the info from the build server')
                    end_status = 'unknown'
                except ValueError:
                    logging.info(
                        'No JSON object could be decoded, from the buildbot '
                        'output\nOutput was as follows; %s' % (content))
                    end_status = 'unknown'
                else:
                    # if no exceptions occured
                    if '-1' in raw_data and 'text' in raw_data['-1']:
                        status_text = raw_data['-1']['text']

                        if 'successful' in status_text:
                            logging.info('Builds are passing')

                            end_status = 'passing'
                        elif ('failed' in status_text or
                                'exception' in status_text):
                            logging.info('Builds are failing')

                            end_status = 'failing'
                    else:
                        logging.info('Build status is unknown')
                        end_status = 'unknown'

                memcache.set('build_status_%s' % (platform), end_status, 60)
            else:
                # if the build status was indeed cached
                # inform the user so
                logging.info('Cached status found')
                # set the build status to the cached build status
                end_status = cached_status

        # create the filename of the build status image
        filename = os.path.join(os.path.dirname(__file__), 'results/%s.png' % (end_status))

        self.response.headers['Content-Type'] = 'image/png'
        # try to ensure github and the browser do not cache the build status
        self.response.headers['Cache-Control'] = 'no-Cache'

        with open(filename, 'rb') as fh:
            self.response.write(fh.read())


class RootModulesHandler(BaseRequestHandler):
    def get(self):
        self.redirect('/human/')


app = webapp2.WSGIApplication(
    [
        (r'/human/tree/pretty.?', PrettyTreeHandler),
        (r'/human/tree.?', TreeHandler),
        (r'/human/search.?', HumanSearch),
        (r'/human/inspect.?', InspectHandler),
        (r'/human.?', HomeHandler),
        (r'/modules.?', RootModulesHandler),
        (r'/modules/search.?', SearchModulesHandler),
        (r'/modules/download.?', DownloadModulesHandler),
        (r'/modules/list.?', ListModulesHandler),
        (r'/status/(?P<platform>.*).png', BuildStatusHandler),
        (r'/flush', FlushHandler),
        (r'/', RedirectToHumanHandler)
    ],
    debug=dtmm_utils.development()
)

logging.info('Running in {} mode'.format(
    'development' if dtmm_utils.development() else 'production'))

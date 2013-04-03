#!/usr/bin/env python
#
# Copyright 2012 Dominic May
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This is a simple webapp2 based application for the Google App Engine PaaS;
it uses the GitHub API v3 to request one of the numerous available files
within the DCPUModules (http://github.com/DCPUTeam/DCPUModules) repository.
It decodes the json returned by the API and the thence linked to base64 encoded
files and provides said files in their original formats, ready to be served to
the DCPUToolchain executables that make use of them.
"""

# generic imports
import os
import json
import base64
import logging

# google appengine imports
import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import memcache

#  humans.py file
from humans import search
from humans import HomeHandler
from humans import TreeHandler
from humans import HumanSearch
from humans import ListingHandler
from humans import InspectHandler
from humans import PrettyTreeHandler
from humans import RedirectToHumanHandler


# the dtmm_utils file
from dtmm_utils import get_tree
from dtmm_utils import get_url_content
from dtmm_utils import FourOhFourErrorLog
from dtmm_utils import BaseRequestHandler


class SearchModulesHandler(BaseRequestHandler):
    "Handle searching of the repo"
    def get(self):
        "Handles get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        query = self.request.get('q')
        data = get_tree(self)
        for fragment in data:
            if (fragment['path'].endswith('.lua') and
                    query in fragment['path'].split('/')[-1]):
                self.response.out.write(
                    str(fragment['path'].split('/')[-1]) + '\n')


class DownloadModulesHandler(BaseRequestHandler):
    "Handles download requests"
    def get(self):
        "Handlers get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        module_name = self.request.get('name')

        data = get_tree(self)

        data_dict = dict(
            (fragment['path'].split('/')[-1], fragment['url'])
            for fragment in data)

        if module_name in data_dict:
            self.response.out.write(base64.b64decode(
                get_url_content(self, data_dict[module_name])['content']))
        else:
            logging.info("Module not found: " + str(module_name))
            entry = FourOhFourErrorLog(
                module=module_name or 'No module name was specified',
                address=str(self.request.remote_addr))
            entry.put()
            self.error(404)


class ListModulesHandler(BaseRequestHandler):
    "returns a list of accessable modules"
    def get(self):
        "Handlers get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        data = get_tree(self)
        for fragment in data:
            if fragment['path'].endswith('.lua'):
                self.response.out.write(
                    str(fragment['path'].split('/')[-1]) + '\n')


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
        # we assume that the build status is unknown
        end_status = 'unknown'
        # ensure the platform is valid
        if platform in ['mac', 'linux', 'windows']:
            # create the build status url
            url = ('http://bb.dcputoolcha.in:8080/'
                    'json/builders/build_{}/builds?select=-1&as_text=1'.format(
                        platform))
            logging.info(url)
            # check whether the build status is cached
            cached_status = memcache.get('build_status_%s' % (platform))
            # if it was not cached, or is no longer in the cache
            if not cached_status:
                # inform the logger of such
                logging.info('Okay, no cached status, hitting the buildbot')
                try:
                    # try to pull build status from the buildbot
                    content = urlfetch.fetch(url).content
                    raw_data = json.loads(content)
                except urlfetch.DownloadError:
                    # inform the logger that we could not get the build status
                    logging.info(
                        'Could not get the info from the build server')
                    end_status = 'unknown'
                except ValueError:
                    logging.info(
                        'No JSON object could be decoded, from the buildbot '
                        'output\nOutput was as follows; %s' % (content))
                    end_status = 'unknown'
                else:
                    # if no exceptions occured
                    if '-1' in raw_data and 'text' in raw_data['-1']:
                        if 'successful' in raw_data['-1']['text']:
                            logging.info('Builds are passing')
                            # set the build status to 'passing'
                            end_status = 'passing'
                        elif ('failed' in raw_data['-1']['text'] or
                                'exception' in raw_data['-1']['text']):
                            logging.info('Builds are failing')
                            # set the build status to 'failing'
                            end_status = 'failing'
                    else:
                        # if the required fields were not available
                        # inform the logger so
                        logging.info('Build status is unknown')
                        end_status = 'unknown'
                # cache the end build status
                memcache.set('build_status_%s' % (platform), end_status, 60)
            else:
                # if the build status was indeed cached
                # inform the user so
                logging.info('Cached status found')
                # set the build status to the cached build status
                end_status = cached_status

        # create the filename of the build status image
        filename = os.path.join(os.getcwd(), 'results/%s.png' % (end_status))

        self.response.headers['Content-Type'] = 'image/png'
        # try to ensure github and the browser do not cache the build status
        self.response.headers['Cache-Control'] = 'no-Cache'

        with open(filename, 'rb') as fh:
            self.response.write(fh.read())


class DebugHandler(BaseRequestHandler):
    def get(self):
        self.response.write(search(None, 'hmd', ''))


class ExceptionTestHandler(BaseRequestHandler):
    def get(self):
        raise Exception


class RootModulesHandler(BaseRequestHandler):
    def get(self):
        self.redirect('/human/')


app = webapp2.WSGIApplication([
    (r'/human/tree/pretty.?', PrettyTreeHandler),
    (r'/human/tree.?', TreeHandler),
    (r'/human/search.?', HumanSearch),
    (r'/human/listing.?', ListingHandler),
    (r'/human/inspect.?', InspectHandler),
    (r'/human.?', HomeHandler),
    (r'/modules.?', RootModulesHandler),
    (r'/modules/search.?', SearchModulesHandler),
    (r'/modules/download.?', DownloadModulesHandler),
    (r'/modules/list.?', ListModulesHandler),
    (r'/status/(?P<platform>.*).png', BuildStatusHandler),
    (r'/exception', ExceptionTestHandler),
    (r'/flush', FlushHandler),
    (r'/debug', DebugHandler),
    (r'/', RedirectToHumanHandler)
    ], debug=True)

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import hashlib
import base64
import json
import logging

# gooogle appengine imports
import webapp2
from google.appengine.api import memcache

# the humans.py file
from humans import HomeHandler
from humans import PrettyTreeHandler
from humans import TreeHandler
from humans import HumanSearch
from humans import RedirectToHumanHandler
from humans import ListingHandler
from humans import InspectHandler

# the mailer.py file
from mailer import sendmail

# the dtmm_utils file
from dtmm_utils import get_url_content
from dtmm_utils import get_tree
from dtmm_utils import FourOhFourErrorLog


class SearchModulesHandler(webapp2.RequestHandler):
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


class DownloadModulesHandler(webapp2.RequestHandler):
    "Handles download requests"
    def get(self):
        "Handlers get requests"
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'no-Cache'
        module_name = self.request.get('name')
        module_found = False
        data = get_tree(self)
        for fragment in data:
            if fragment != {}:
                if fragment['path'].split('/')[-1] == module_name:
                    module_found = True
                    self.response.out.write(base64.b64decode(
                        get_url_content(self, fragment['url'])['content']))
        if not module_found:
            logging.info("Module not found: " + str(module_name))
            entry = FourOhFourErrorLog(address=self.request.remote_addr, requested_module=str(module_name))
            entry.put()
            self.error(404)

    def post(self):
        "Handlers post requests"
        self.response.write('This uri does not handle post requests')


class ListModulesHandler(webapp2.RequestHandler):
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


class FlushHandler(webapp2.RequestHandler):
    "Flushes the memcache, like an idiot"
    def get(self):
        "handles get requests"
        flusher(self)

    def post(self):
        "handles post requests"
        flusher(self)


class SmartFlushHandler(webapp2.RequestHandler):
    "Tries to efficiently flush the memcache"
    def get(self):
        "Handles get requests to this uri"
        self.response.out.write(
            'The Smart Flusher Handler can be reached at this address')

    def post(self):
        "Handles post requests to this uri"
        payload = self.request.get('payload')
        payload = json.loads(payload)
        files_changed = False
        changed_files = []
        info_dict = {}
        for commit in payload['commits']:
            changed_files += commit['modified']
            try:
                changed_files += commit['removed']
            except KeyError:
                pass
        for changed_file in changed_files:
            info_dict[str(changed_file)] = False
        if len(changed_files) != 0 and changed_files != []:
            files_changed = True
            for changed_file in changed_files:
                logging.info('type: ' + str(changed_file))
                if changed_file != None and changed_file != '':
                    logging.info(
                        changed_file + ':' +
                        str(memcache.get(changed_file)) + ':' +
                        hashlib.md5(
                            str(memcache.get(changed_file))).hexdigest())
                    if memcache.get(changed_file) != None:
                        memcache.delete(
                            hashlib.md5(
                                memcache.get(changed_file)).hexdigest())
                    memcache.delete(changed_file)
                    try:
                        info_dict[str(changed_file)] = True
                    except KeyError:
                        pass
            sendmail(
                'Here is a list \n\n' +
                str(changed_files) + '\n\n\n\n\n\n\n' + str(info_dict))

        removed_files = []
        for commit in payload['commits']:
            removed_files += commit['removed']
        if len(removed_files) != 0 and removed_files != []:
            files_changed = True
            for removed_file in removed_files:
                if removed_file != None and removed_file != '':
                    if memcache.get(removed_file) != None:
                        memcache.delete(
                            hashlib.md5(
                                memcache.get(removed_file)).hexdigest())
                    memcache.delete(removed_file)

        added_files = []
        for commit in payload['commits']:
            added_files += commit['added']
        if len(added_files) != 0 and added_files != []:
            files_changed = True
            get_tree(self)
        if not files_changed:
            sendmail('Odd. No files were changed in this commit')


app = webapp2.WSGIApplication([
    (r'/human/tree/pretty', PrettyTreeHandler),
    (r'/human/tree*', TreeHandler),
    (r'/human/search*', HumanSearch),
    (r'/human/listing', ListingHandler),
    (r'/human/inspect', InspectHandler),
    (r'/human/*', HomeHandler),
    (r'/human*', HomeHandler),
    (r'/modules/search*', SearchModulesHandler),
    (r'/modules/download*', DownloadModulesHandler),
    (r'/modules/list', ListModulesHandler),
#    (r'/flush', SmartFlushHandler),
    (r'/flush', FlushHandler),
    (r'/', RedirectToHumanHandler)
    ], debug=True)

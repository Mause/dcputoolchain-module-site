import os
import logging

import dtmm_utils
from google.appengine.api import memcache

STATUS_URL = 'http://bb.dcputoolcha.in:8080/json/builders/build_{}/builds?select=-1&as_text=1'


class BuildStatusHandler(dtmm_utils.BaseRequestHandler):
    def notify_status(self, status):
        # determine the filename of the build status image
        filename = 'results/%s.png' % (status)
        filename = os.path.join(os.path.dirname(__file__), filename)

        # try to ensure github and the browser do not cache the build status
        self.response.headers.update({
            'Content-Type': 'image/png',
            'Cache-Control': 'no-Cache'
        })

        with open(filename, 'rb') as fh:
            self.response.write(fh.read())

    def get(self, platform):
        platform = platform.lower()
        key = 'build_status_{}'.format(platform)
        # import pudb
        # pu.db

        # ensure the platform is valid
        if platform not in ['mac', 'linux', 'windows']:
            return self.notify_status('unknown')

        status = memcache.get(key)
        if not status:
            # create the build status url
            url = STATUS_URL.format(platform)

            raw_data = dtmm_utils.get_url_content(self, url)

            # if no exceptions occured
            if '-1' in raw_data and 'text' in raw_data['-1']:
                status_text = raw_data['-1']['text']

                if 'successful' in status_text:
                    logging.info('Builds are passing')

                    status = 'passing'
                elif ('failed' in status_text or
                        'exception' in status_text):
                    logging.info('Builds are failing')

                    status = 'failing'
                else:
                    status = 'unknown'
            else:
                logging.info('Build status is unknown')
                status = 'unknown'

            memcache.set(key, status)

        return self.notify_status(status)

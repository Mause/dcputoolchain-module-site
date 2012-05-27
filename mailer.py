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
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


# www.lysdev.com/mailer?dest=jack.thatch@gmail.com&message=This person has RVSPed: Dominic May&dest_name=Dominic&addr=/events?hash=d31d9e54997706f8caec751a788aa053&subject=RSVP

def sendmail(message):
    #message=self.request.get('message')
    dest_name = 'Dominic' #dest_name=self.request.get('dest_name')
    dest = 'jack.thatch@gmail.com' #dest=self.request.get('dest')
    subject = 'DTMM Debug Message' #subject=self.request.get('subject')
    mail.send_mail(sender="Admin Jones <admin@lysdev.com>",
          to=dest,
          subject=subject,
          body=('''
Dear '''+dest_name+'''

'''+message+'''

Please let us know if you have any questions.

The Lysdev.com Team
'''))



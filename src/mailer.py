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
from google.appengine.api import mail
BODY = (
    '\n'
    'Dear Dominic,'
    '\n'
    '%s'
    '\n'
    '\n'
    'Please let us know if you have any questions.'
    '\n'
    '\n'
    'The Lysdev.com Team\n'
)


def sendmail(message):
    return mail.send_mail(
        sender="Admin Jones <admin@lysdev.com>",
        to='jack.thatch@gmail.com',
        subject='DTMM Debug Message',
        body=BODY.format(message)
    )

import os
from google.appengine.dist import use_library
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '1.4.2.final.0')


appstats_CALC_RPC_COSTS = True
webapp_django_version = '1.4.2.final.0'


def webapp_add_wsgi_middleware(app):
    "Add the appstats middleware"
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app

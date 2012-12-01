import webapp2
from google.appengine.ext.appstats import ui
from google.appengine.ext.appstats import recording

import pickle
import collections


class MainHandler(webapp2.RequestHandler):
    def get(self):
        new_data = ui.SummaryHandler()._get_summary_data(
            recording.load_summary_protos())
        requests = new_data["requests"]
        sep = '\n'

        def traverse(what, layer, iterations):
            if iterations == 20:
                return
            else:
                iterations += 1
            if isinstance(what, collections.Iterable):
                layer += 1
                for sub_frag in what:
                    traverse(sub_frag, layer, iterations)
            elif hasattr(what, '__dict__'):
                self.response.write(
                    '%s%s%s' % (('\t' * layer), str(what), sep))
                layer += 1
                for key in what.__dict__.keys():
                    self.response.write(
                        '%s%s;\n' % (
                            ('\t' * layer),
                            str(key)
                            ))

                    traverse(what.__dict__[key], layer, iterations)
            else:
                self.response.write('%s%s%s' % (('\t' * layer), what, sep))

        traverse(requests, 0, 0)


class DumpHandler(webapp2.RequestHandler):
    def get(self):
        new_data = ui.SummaryHandler()._get_summary_data(
            recording.load_summary_protos())
        self.response.write(pickle.dumps(new_data))


class SpecSpecHandler(webapp2.RequestHandler):
    def get(self):
        new_data = ui.SummaryHandler()._get_summary_data(
            recording.load_summary_protos())
        self.response.write(new_data)


app = webapp2.WSGIApplication(
    [
    ('/spec/dump', DumpHandler),
    ('/spec/spec', SpecSpecHandler),
    ('.?', MainHandler),
    ],
    debug=True)

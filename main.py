import webapp2
import sqlite3
conn = sqlite3.connect('lua_file_data.db')

class HomeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('''
<form action="/modules/search">
<input name="q"/>
<input type="submit"/>
</form>''')


class AddModulesHandler(webapp2.RequestHandler):
    def get(self):
        conn = lite.connect('test.db')
        with con:
            cursor = con.cursor()
            cursor.execute("CREATE TABLE FILES(Id INT, Filename TEXT, Path TEXT)")
            cur.execute("INSERT INTO Cars VALUES(1,'rng.lua',')")


class SearchModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(self.request.get('q')+'</br>')
        try:
            conn = None
            conn = sqlite3.connect('lua_file_data.db')
            cursor = (conn).cursor()
            cursor.execute('SELECT * FROM FILES WHERE "'+self.request.get('q')+'" IN TAGS')
            data = cursor.fetchone()
            self.response.write(data)
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if conn:
                conn.close()

class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(self.request.get('name'))

app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/modules/search*', SearchModulesHandler),
    ('/modules/add*', AddModulesHandler),
    ('/modules/download*', DownloadModulesHandler)
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()


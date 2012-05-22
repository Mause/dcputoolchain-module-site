import webapp2
import sqlite3
import datetime
import hashlib
import urllib
import base64
import json


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('''
<h3>Search the available modules</h3>
<form action="/modules/search">
<input name="q"/>
<input type="submit"/>
</form>''')


class AddModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('''
<h3>Add a file to the database</h3>
<form action="/modules/add" enctype="multipart/form-data" method="post">
<div><label>File:</label></div>
<div><input type="file" name="file" required /></div>
<!--<div><label>Password to upload file:</label></div>
<input type="password" name="upload_password" required><br>-->
<input type="submit"/>
</form>''')
    def post(self):
#        if hashlib.md5(self.request.get('upload_password')).hexdigest() != '1fb02e8ea692944e211252903db8544a':
 #           self.respond.write('Sorry. That was the incorrect input password')
  #          return
        data = self.request.POST[u'file'].value
        filename = self.request.POST[u'file'].filename
        conn = sqlite3.connect('lua_file_data.db')        
        with conn:
            cursor = conn.cursor()
            # CREATE TABLE FILES(Id INTEGER PRIMARY KEY, Filename TEXT, Data LONGTEXT, Date DATE, Hash TEXT);
            cursor.execute("INSERT INTO FILES VALUES(NULL,'"+
                           filename+"','"+
                           data+"','"+
                           str(datetime.date.today())+"', '"+
                           hashlib.sha1(data).hexdigest()+"')")


class SearchModulesHandler(webapp2.RequestHandler):
    def get(self):
        try:
            conn = None
            conn = sqlite3.connect('lua_file_data.db')
            cursor = (conn).cursor()
            cursor.execute('SELECT filename FROM FILES WHERE filename LIKE "%'+self.request.get('q')+'%"')
            data = cursor.fetchall()
            if len(data) != 0:
                for entry in data:
                    self.response.write(entry[0]+'\n')
        except sqlite3.Error, e:
            pass # we cant really throw an error, can we?
            #print "Error %s:" % e.args[0]
        finally:
            if conn:
                conn.close()

class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(urllib.urlopen('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').read())
        for x in data['tree']:
            if x['path'].split('/')[-1] == self.request.get('name'):
                #self.response.out.write(x['content']))
                self.response.out.write(base64.b64decode(json.loads(urllib.urlopen(x['url']).read())['content']))
                
#        try:
 #           conn = None
  #          conn = sqlite3.connect('lua_file_data.db')
   #         cursor = (conn).cursor()
    #        command = 'SELECT data FROM files WHERE filename = "'+self.request.get('name')+'";'
     #       cursor.execute(command)
      #      data = cursor.fetchall()
       #     if len(data) != 0:
        #        self.response.write(str(data[0][0]))
#        except sqlite3.Error, e:
 #           pass # we cant really throw an error, can we?
  #          #print "Error %s:" % e.args[0]
   #     finally:
    #        if conn:
     #           conn.close()


class ListModulesHandler(webapp2.RequestHandler):
    def get(self):
        data = json.loads(urllib.urlopen('https://api.github.com/repos/DCPUTeam/DCPUModules/git/trees/master').read())
        for x in data['tree']:
            self.response.out.write(x['path']+'\n')

app = webapp2.WSGIApplication([
    ('/modules/search*', SearchModulesHandler),
    ('/modules/add*', AddModulesHandler),
    ('/modules/download*', DownloadModulesHandler),
    ('/modules/list', ListModulesHandler),
    ('/', HomeHandler)
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8010')#127.0.0.1

if __name__ == '__main__':
    main()


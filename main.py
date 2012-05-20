import webapp2
import sqlite3
import datetime


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
        conn = sqlite3.connect('lua_file_data.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO FILES VALUES(NULL,'rng.lua','
-- if the emulator is at a path like: path/to/dtemu.exe
-- then put this in a path like:      path/to/hw/rng.lua

-- interrupt values
local INT_GENERATE = 0;
local INT_SEED = 1;

function interrupt(cpu)
  -- cpu is a table that lets you do things to the CPU.
  if (cpu.registers.A == INT_GENERATE) then
    cpu.registers.B = math.random(0x0, 0xFFFF);
  elseif (cpu.registers.A == INT_SEED) then
    math.randomseed(cpu.registers.B);
  end
end

function cycle(cpu)
  -- cpu is a table that lets you do things to the CPU.
  -- according to hardware standards, this is not called
  -- until the first interrupt has been received and handled,
  -- however at the moment the toolchain ignores this
  -- requirement and its called anyway :P
  
  --[[print(string.format("0x%X", cpu.ram[0x0]))
  print(cpu.registers.Z)
  print(cpu.registers.PC)
  cpu.registers.Z = math.random(0x0, 0xFFFF);
  cpu.ram[0x0] = 0x0;]]--
end

function write(cpu, pos)
  -- cpu is a table that lets you do things to the CPU.
  -- pos is the memory address that was written to.
end

MODULE = {
  Type = "Hardware",
  Name = "RNG Hardware",
  Version = "1.0"
};

HARDWARE = {
  ID = 0x739df773,
  Version = 0x0001,
  Manufacturer = 0x93765997
};',"""+str(datetime.date.today())+")")


class SearchModulesHandler(webapp2.RequestHandler):
    def get(self):
        try:
            conn = None
            conn = sqlite3.connect('lua_file_data.db')
            cursor = (conn).cursor()
            cursor.execute('SELECT filename FROM FILES WHERE filename LIKE "%'+self.request.get('q')+'%"')
            data = cursor.fetchall()
            for entry in data:
                self.response.write(entry[0]+'\n')
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if conn:
                conn.close()

class DownloadModulesHandler(webapp2.RequestHandler):
    def get(self):
        #self.response.write(self.request.get('name'))
        #self.response.write(self.request.get('name')+'</br>')
        try:
            conn = None
            conn = sqlite3.connect('lua_file_data.db')
            cursor = (conn).cursor()
            command = 'SELECT data FROM files WHERE filename = "'+self.request.get('name')+'";'
            cursor.execute(command)
            data = cursor.fetchall()
            self.response.write(str(data[0]))
        except sqlite3.Error, e:
            pass # we cant really throw an error, can we?
            #print "Error %s:" % e.args[0]
        finally:
            if conn:
                conn.close()


class ListModulesHandler(webapp2.RequestHandler):
    def get(self):
        #self.response.write(self.request.get('name'))
        self.response.write(self.request.get('name')+'</br>')
        try:
            conn = None
            conn = sqlite3.connect('lua_file_data.db')
            cursor = (conn).cursor()
            cursor.execute('SELECT * FROM FILES')
            data = cursor.fetchall()
            for x in data:
                self.response.write(str(x)+'</br>')
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if conn:
                conn.close()








app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/modules/search*', SearchModulesHandler),
    ('/modules/add*', AddModulesHandler),
    ('/modules/download*', DownloadModulesHandler),
    ('/modules/list', ListModulesHandler)
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='', port='8080')#127.0.0.1

if __name__ == '__main__':
    main()


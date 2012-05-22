DCPUToolchain Lua Site
======================

This is a simple webapp2 based webapp; it uses the GitHub api v3 to request one of the numerous files within the DCPUModules[http://github.com/DCPUTeam/DCPUModules] repository.
It decodes the returned json and base64 and provides it in its original format to be served to the DCPUToolchain executables that support the lua modules.
DCPUToolchain Module Site
======================

Unit test status; [![Unit test status](https://secure.travis-ci.org/Mause/dcputoolchain-module-site.png?branch=master)](https://travis-ci.org/Mause/dcputoolchain-module-site)


This is a simple webapp2 based application that runs on Google App Engine; it uses the [GitHub API](http://developer.github.com/) to request one of the numerous available files within the [DCPUModules](http://github.com/DCPUTeam/DCPUModules) repository.
It decodes the json returned by the API and the thence linked to base64 encoded files and provides said files in their original formats, ready to be served to the DCPUToolchain executables that make use of them. It also uses Oauth tokens to allow for greater allowances in terms of GitHub API access.

An ancillary function also provided by the Module Site is demonstrated as follows;

 *  Windows build status; ![Windows build status](http://dms.dcputoolcha.in/status/windows.png)
 *  Linux build status; ![Linux build status](http://dms.dcputoolcha.in/status/linux.png)
 *  Mac build status; ![Mac build status](http://dms.dcputoolcha.in/status/mac.png)

This simply polls the buildbot for the status of the most recent build for each platform; you are welcome to inspect the [code behind it](https://github.com/Mause/dcputoolchain-module-site/blob/master/src/main.py#L188);

Finally, this project makes use of SirAnthony's simple lua-python data structures parser (slpp) to pull module and hardware information from the module files.

P.S: if you make use of some of the code here, please let me know and/or attribute some credit to me :smile:

Please see [reference.md](reference.md) for some details behind the original design spec.

This project was constructed from the following two discussions on the IRC network freenode, with hachque, the project leader.
These are edited slightly from the originals, but said originals can be found in the reference folder in the repository :)

```
Session Start: Sat May 19 18:17:28 2012
Session Ident: hachque
[18:17] <hachque> hey
[18:17] <Lord_DeathMatch> hi :)
[18:17] <hachque> can you set up some kind of online module system?
[18:18] <Lord_DeathMatch> how do you mean?
[18:18] <hachque> just a repository that can be queried for modules
[18:18] <hachque> like
[18:18] <hachque> /modules/search?q=blah
[18:18] <hachque> returns the result as just newline-seperated results
[18:18] <hachque> and then
[18:18] <hachque> /modules/download?name=blah
[18:18] <hachque> would give the lua script
[18:18] <Lord_DeathMatch> yeah, i can do that
[18:18] <Lord_DeathMatch> easy wnough
[18:18] <Lord_DeathMatch> *enough
[18:19] <hachque> later on we could make it so that people could upload their own scripts to the repo
[18:19] <hachque> but initially we just need that
[18:19] <Lord_DeathMatch> im not doing anything tonight, i can write a prototype
[18:19] <hachque> kk, that would be cool
[18:19] <hachque> also
[18:19] <Lord_DeathMatch> yeah?
[18:19] <hachque> do you want to remove the documentation compilation steps in build_for_windows
[18:19] <hachque> since build_for_linux already does that
[18:19] <hachque> no point doing it twice
[18:20] <Lord_DeathMatch> yeah, but is it possible to add a make command that just builds the documentation
[18:20] <Lord_DeathMatch> ?
[18:20] <Lord_DeathMatch> then i put into a seperate factoy
[18:20] <Lord_DeathMatch> *i can
[18:20] <hachque> I was more thinking that since both jobs will the built as new commits come in
[18:21] <Lord_DeathMatch> fair enough :)
[18:21] <Lord_DeathMatch> ill do it now
[18:21] <hachque> awesome
Session Close: Sat May 19 19:06:51 2012
```

```
Session Start: Sun May 20 19:51:02 2012
Session Ident: hachque
[19:51] <hachque> for?
[20:08] <Lord_DeathMatch> for the link i sent you :P the one to upload modules :P
[20:08] <Lord_DeathMatch> http://irc.lysdev.com:8080/modules/add
[20:09] <hachque> ah okay
[20:09] <hachque> well it's open source, so there's no point having a password
[20:09] <hachque> modules interface should just be HTTP-only
[20:09] <hachque> *modules add interface
[20:09] <hachque> like you did with the search form
[20:11] <Lord_DeathMatch> what, as opposed to https?
[20:11] <Lord_DeathMatch> theres no javascript or anything like that
[20:11] <Lord_DeathMatch> its python
[20:12] <hachque> nah I mean
[20:12] <hachque> d/w about providing a programmable interface to add modules
[20:12] <hachque> it's not needed
[20:12] <hachque> only need programmable interfaces for install/remove/search
[20:13] <Lord_DeathMatch> righteo
[20:13] <Lord_DeathMatch> though im apprehensive of proving a free-for-all remove interface :P
[20:13] <Lord_DeathMatch> *providing
[20:25] <Lord_DeathMatch> hachque: anything special for 'install'? or do you mean just serving the file?
[20:25] <hachque> just serve the file
[20:25] <hachque> and you don't need to do anything for remove
[20:25] <hachque> since that's all local
[20:25] <Lord_DeathMatch> oh, righteo
[20:25] <Lord_DeathMatch> cool
[20:26] <Lord_DeathMatch> hachque: do we want to be able to search the contents of the files too?
[20:26] <hachque> aww
[20:26] <hachque> not really
[20:26] <hachque> although
[20:26] <hachque> it would be good if you could evaluate the file in Lua
[20:26] <hachque> and then pull out the module information
[20:26] <hachque> so they could search by module name
[20:27] <Lord_DeathMatch> yeah, i dont know how well that would go down in python though
[20:29] <Lord_DeathMatch> well what do you know: http://code.google.com/p/slpp/
[20:29] <Lord_DeathMatch> huh
Session Close: Sun May 20 22:02:49 2012
```

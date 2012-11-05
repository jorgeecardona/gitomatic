# Gitomatic

[![Build Status](https://travis-ci.org/jorgeecardona/gitomatic.png)](https://travis-ci.org/jorgeecardona/gitomatic)

Gitomatic is a tool to easy control a git repository in a single account with multiples repositories.

It has a basic access control, controled from a command tool called with gitomatic.


## Requirements.

Gitomatic creates a directory '.gitomatic' in the home path of the user that runs the command 'gitomatic init'. An user called 'git' would be very attractive to use, but you can use any.


## Example:

In this examples I assume you have a user 'git', and you have the public rsa key of the user 'doe' (which is not a user of the system, just an user of the repository) in /tmp/id_rsa.pub.


To initialize the whole system in your server just do this:

    git@server:~$ gitomatic initialize
    git@server:~$ gitomatic repository create test.git
    git@server:~$ gitomatic keys add -f /tmp/id_rsa.pub username
    git@server:~$ gitomatic permissions add doe -r test.git R

You can now remove the public key of doe and check from outside that doe has now read access, so it can clone the repo, but it can't push to it.

    doe@laptop:~$ git clone git@server:test.git
    ... It works

    doe@laptop:~$ git push origin master
    ... It fails

    doe@laptop:~$ git pull origin master
    ... It works

Now add write permission:

    git@server:~$ gitomatic permissions add -r test.git doe W

And doe has now permission to push to the server.

    doe@laptop:~$ git clone git@server:test.git
    ... It works    

    doe@laptop:~$ git push origin master
    ... It works

    doe@laptop:~$ git pull origin master
    ... It works

Now remove the read permission, since we need read permission to keep the write permission both are going to be removed.

    git@server:~$ gitomatic permissions remove -r test.git username R

Check then that doe can't neither clone nor push to the server.

    doe@laptop:~$ git clone git@server:test.git
    ... It fails

    doe@laptop:~$ git push origin master
    ... It fails

    doe@laptop:~$ git pull origin master
    ... It fails


## Gitomatic as a library

You can use gitomatic from a python code like this:

    from gitomatic import Gitomatic
    
    g = Gitomatic()
    g.initialize()
    g.repository.create('test')
    g.permissions.add('username', 'test', 'RW')
    g.keys.add('username', 'ssh-rsa xxxxx')

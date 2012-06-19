# Gitomatic

Gitomatic is a tool to easy control a git repository in a single account with multiples repositories.

It has a basic access control, controled from a command tool called with gitomatic.


## Requirements.

Gitomatic creates a directory '.gitomatic' in the home path of the user that runs the command 'gitomatic init'. An user called 'git' would be very attractive to use, but you can use anyone.


## Example:

In this examples I assume you have a user 'git', and you have the public rsa key of the user username (which is not a user of the system, just an user of the repository) in /tmp/id_rsa.pub.


    $ gitomatic initialize
    $ gitomatic repository create test.git
    $ gitomatic keys add -f /tmp/id_rsa.pub username
    $ gitomatic permissions add username -r test.git R

...

    $ git clone git@server:test.git
    OK

    $ git push origin master
    FAILED

    $ git pull origin master
    OK

...

    $ gitomatic permissions add -r test.git username W

...

    $ git clone git@server:test.git
    OK

    $ git push origin master
    OK

    $ git pull origin master
    OK

...

    $ gitomatic permissions remove -r test.git username R

...

    $ git clone git@server:test.git
    FAIL

    $ git push origin master
    FAIL

    $ git pull origin master
    FAIL

You can use gitomatic from a python code like this:

    from gitomatic import Gitomatic
    
    g = Gitomatic()
    g.initialize()
    g.repository.create('test')
    g.permissions.add('username', 'test', 'RW')
    g.keys.add('username', 'ssh-rsa xxxxx')

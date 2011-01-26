# Gitomatic

Gitomatic is a tool to easy control a git repository in a single account with multiples repositories.

It has a basic access control, controled from a command tool called with gitomatic.


## Requirements.

Gitomatic creates a directory '.gitomatic' in the home path of the user that runs the command 'gitomatic init'. An user called 'git' would be very attractive to use, but you can use anyone.


## Example:

In this examples I assume you have a user 'git', and you have the public rsa key of the user username (which is not a user of the system, just an user of the repository) in /tmp/id_rsa.pub.


    $ gitomatic init
    $ gitomatic add_repo test.git
    $ gitomatic add_key -f /tmp/id_rsa.pub username
    $ gitomatic add_perm username test.git R

...

    $ git clone git@server:test.git
    OK

    $ git push origin master
    FAILED

    $ git pull origin master
    OK

...

    $ gitomatic add_perm username test.git W

...

    $ git clone git@server:test.git
    OK

    $ git push origin master
    OK

    $ git pull origin master
    OK

...

    $ gitomatic remove_perm username test.git R

...

    $ git clone git@server:test.git
    FAIL

    $ git push origin master
    FAIL

    $ git pull origin master
    FAIL

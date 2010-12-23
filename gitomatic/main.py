import logging
import re
import os
import argparse
import configobj
import subprocess
import shutil
from hashlib import sha1
import configuration


def init(args):
    # Initializ the gitomatic structure.
    home_path = os.environ['HOME']

    if not os.path.exists(os.path.join(home_path, '.ssh')):
        print "Creating ~/.ssh path"
        os.mkdir(os.path.join(home_path, '.ssh'), 0o700)
        os.chown(os.path.join(home_path, '.ssh'), os.geteuid(), os.getegid())

    # Create gitomatic path
    if not os.path.exists(os.path.join(home_path, '.gitomatic')):
        print "Creating ~/.gitomatic/ path ..."
        os.mkdir(os.path.join(home_path, '.gitomatic'))
        os.chown(os.path.join(home_path, '.gitomatic'),
                 os.geteuid(), os.getegid())

    # Create gitomatic key path.
    if not os.path.exists(os.path.join(home_path, '.gitomatic/keys')):
        print "Creating ~/.gitomatic/keys path ..."
        os.mkdir(os.path.join(home_path, '.gitomatic/keys'))
        os.chown(os.path.join(home_path, '.gitomatic/keys'),
                 os.geteuid(), os.getegid())

    # Create config path
    if not os.path.exists(os.path.join(home_path, '.gitomatic/conf.d')):
        print "Creating ~/.gitomatic/conf.d path ..."
        os.mkdir(os.path.join(home_path, '.gitomatic/conf.d'))
        os.chown(os.path.join(home_path, '.gitomatic/conf.d'),
                 os.geteuid(), os.getegid())

    # Create repos path
    if not os.path.exists(os.path.join(home_path, '.gitomatic/repos')):
        print "Creating ~/.gitomatic/repos path ..."
        os.mkdir(os.path.join(home_path, '.gitomatic/repos'))
        os.chown(os.path.join(home_path, '.gitomatic/repos'),
                 os.geteuid(), os.getegid())

    # Create global config.
    config = configobj.ConfigObj(
        os.path.join(home_path, '.gitomatic/conf.d/000-global'))
    config.write()


def add_repo(args):
    # Add a new repo.
    home_path = os.environ['HOME']
    repo_path = os.path.join(
        home_path, '.gitomatic/repos', args.repo)

    if os.path.exists(repo_path):
        logging.error("Duplicated repo.")
        exit(2)

    # Create repo.
    p = subprocess.Popen(['git', 'init', '--bare', repo_path])
    p.wait()


def remove_repo(args):
    # Remove a repo.
    home_path = os.environ['HOME']
    repo_path = os.path.join(
        home_path, '.gitomatic/repos', args.repo)

    if not os.path.exists(repo_path):
        logging.error("Repo not found.")
        exit(2)

    # Remove path.
    shutil.rmtree(repo_path)


def add_key(args):
    # Add a new key.

    # Read key.
    if args.key is not None:
        key = args.key
    elif args.filename is not None:
        fd = open(args.filename)
        key = fd.read()
        fd.close()
    else:
        logging.error("Please specify a key.")
        exit(2)

    hash_key = sha1(key).hexdigest()
    print "SHA1 of key: %s" % (hash_key, )

    basename = '%s:%s' % (args.username, hash_key)

    home_path = os.environ['HOME']
    key_path = os.path.join(
        home_path, '.gitomatic/keys', basename)

    # Write key
    fd = open(key_path, 'w')
    fd.write(key)
    fd.close()

    # Update Authorized Keys
    update_authorized_keys()


def remove_key(args):
    # Get filename
    basename = '%s:%s' % (args.username, args.hash_key)
    home_path = os.environ['HOME']
    key_path = os.path.join(
        home_path, '.gitomatic/keys', basename)

    # Read key.
    fd = open(key_path)
    data = fd.read()
    fd.close()

    if args.hash_key != sha1(data).hexdigest():
        logging.error("Invalid hash key")
        exit(2)

    # Remove path
    os.remove(key_path)

    # Update Authorized Keys
    update_authorized_keys()


def update_authorized_keys():

    home_path = os.environ['HOME']

    # Build gitolite section.
    gitolite_section = ['### Start Gitolite ###']

    # Gather keys.
    filenames = os.walk(os.path.join(home_path, '.gitomatic/keys')).next()[2]
    for filename in filenames:
        # Userbame and hash_key
        username, hash_key = filename.split(':')

        # Read Key
        fd = open(os.path.join(home_path, '.gitomatic/keys', filename))
        key = fd.read()
        fd.close()

        # Create entry
        cmd = '/usr/local/bin/gitomatic-auth %s' % (username, )
        gitolite_section.append(
            "command=\"%s\",no-port-forwarding,no-X11-forwarding,"\
            "no-agent-forwarding,no-pty %s" % (cmd, key))

    #  Gitolite final section
    gitolite_section.append('### End Gitolite ###')
    gitolite_section = "\n\n".join(gitolite_section)

    # Read authorized_keys
    try:
        fd = open(os.path.join(home_path, '.ssh', 'authorized_keys'))
        authorized_keys = fd.read()
        fd.close()
    except IOError:
        authorized_keys = ''

    # Extract gitolite section.
    regex = re.compile(
        '(.*)### Start Gitolite ###.*?### End Gitolite ###(.*).*',
        re.DOTALL | re.MULTILINE)
    res = regex.match(authorized_keys)

    if res:
        # Remove gitolite keys.
        authorized_keys = list(res.groups())
        authorized_keys.insert(1, gitolite_section)
        authorized_keys = "".join(authorized_keys)
    else:
        authorized_keys += "\n" + gitolite_section

    # Write authorized_keys
    fd = open(os.path.join(home_path, '.ssh', 'authorized_keys'), 'w')
    os.fchmod(fd.fileno(), 0o600)
    fd.write(authorized_keys)
    fd.close()


def add_perm(args):
    # Add a permission.
    actual = configuration.read_permission(args.repo, args.username)
    new_perm = actual.union(set(args.perm))
    configuration.write_permission(args.repo, args.username, new_perm)


def remove_perm(args):
    # Remove a permission.
    actual = configuration.read_permission(args.repo, args.username)
    new_perm = actual - set(args.perm)
    configuration.write_permission(args.repo, args.username, new_perm)


def main():

    # Start Parser
    parser = argparse.ArgumentParser(
        description="Git management tool.")

    # Commands subparser
    commands = parser.add_subparsers(title='commands')

    # Init command
    command_init = commands.add_parser('init')
    command_init.set_defaults(func=init)

    # Add Repo Command
    command_add_repo = commands.add_parser('add_repo')
    command_add_repo.add_argument('repo', type=str, help="Repository name")
    command_add_repo.set_defaults(func=add_repo)

    # Remove Repo Command
    command_remove_repo = commands.add_parser('remove_repo')
    command_remove_repo.add_argument('repo', type=str, help="Repository name")
    command_remove_repo.set_defaults(func=remove_repo)

    # Add key Command
    command_add_key = commands.add_parser('add_key')
    command_add_key.add_argument('username', type=str, help="Username")
    command_add_key.add_argument('-f', '--filename', type=str,
                                 help="Filename that holds the key.")
    command_add_key.add_argument('-k', '--key', type=str,
                                 help="Literal Key")
    command_add_key.set_defaults(func=add_key)

    # Remove user command
    command_remove_key = commands.add_parser('remove_key')
    command_remove_key.add_argument('username', type=str, help="Username")
    command_remove_key.add_argument('hash_key', type=str,
                                    help='SHA1 of the key')
    command_remove_key.set_defaults(func=remove_key)

    # Add Permission command.
    command_add_perm = commands.add_parser('add_perm')
    command_add_perm.add_argument('username')
    command_add_perm.add_argument('repo')
    command_add_perm.add_argument('perm')
    command_add_perm.set_defaults(func=add_perm)

    # Remove Permission command
    command_remove_perm = commands.add_parser('remove_perm')
    command_remove_perm.add_argument('username')
    command_remove_perm.add_argument('repo')
    command_remove_perm.add_argument('perm')
    command_remove_perm.set_defaults(func=remove_perm)

    # Set permission command.

    args = parser.parse_args()
    args.func(args)

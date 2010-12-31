import logging
import os
import argparse
import configobj
import repo
import perms
import keys


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
    return repo.add(args.repo)


def remove_repo(args):
    return repo.remove(args.repo)


def add_key(args):
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

    return keys.add(args.username, key)


def remove_key(args):
    return keys.remove(args.username, args.hash_key)


def add_perm(args):
    return perms.add(args.repo, args.username, args.perm)


def remove_perm(args):
    return perms.remove(args.repo, args.username, args.perm)


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

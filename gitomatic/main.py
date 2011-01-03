import logging
import argparse
from base import Gitomatic


def init(args):
    g = Gitomatic()
    return g.initialize()


def add_repo(args):
    g = Gitomatic()
    return g.repo_add(args.repo)


def remove_repo(args):
    g = Gitomatic()
    return g.repo_delete(args.repo)


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

    g = Gitomatic()
    return g.key_add(args.username, key)


def remove_key(args):
    g = Gitomatic()
    return g.key_delete(args.username, args.hash_)


def add_perm(args):
    g = Gitomatic()
    return g.perm_add(args.username, args.repo, args.perm)


def remove_perm(args):
    g = Gitomatic()
    return g.perm_delete(args.username, args.repo, args.perm)


def add_hook(args):
    g = Gitomatic()

    # Read hook.
    fd = open(args.filename)
    hook = fd.read()
    fd.close()

    return g.hook_add(args.repo, args.type, hook, args.name, args.order)


def remove_hook(args):
    g = Gitomatic()
    return g.hook_delete(args.repo, args.type, args.name, args.order)


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

    # Add hook command.
    command_hook_add = commands.add_parser('add_hook')
    command_hook_add.add_argument('type', choices=['post-receive'])
    command_hook_add.add_argument('repo')
    command_hook_add.add_argument('name', help='Name used to store the hook.')
    command_hook_add.add_argument('-f', '--filename', type=str,
                                 help="Filename that holds the hook.")
    command_hook_add.add_argument(
        '--order', type=int, default=0, help='Hook apply order.')
    command_hook_add.set_defaults(func=add_hook)

    # Remove hook command.
    command_hook_remove = commands.add_parser('remove_hook')
    command_hook_remove.add_argument('type', choices=['post-receive'])
    command_hook_remove.add_argument('repo')
    command_hook_remove.add_argument('name',
                                     help='Name used to store the hook.')
    command_hook_remove.add_argument(
        '--order', type=int, default=0, help='Hook apply order.')
    command_hook_remove.set_defaults(func=remove_hook)

    args = parser.parse_args()
    args.func(args)

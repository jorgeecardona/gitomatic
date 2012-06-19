import argparse

from commands import RepositoryCommands
from commands import KeysCommands
from commands import InitCommands
from commands import PermissionCommands
from commands import HookCommands


def main():
    """
    We build here the structure of the main user cli:

    - Create/Delete repositories:
       gitomatic repository create <name>
       gitomatic repository delete <name>

    - Add/Remove keys for users.
      gitomatic keys add <username> <key>
      gitomatic keys add <username> -f file.key
      gitomatic keys add <username> -f file.key

    - Add/Modify/Remove permissions of user for repositories:
      gitomatic permissions <username> <repo> <perm>

    """

    # Start Parser
    parser = argparse.ArgumentParser(
        description="Git management tool.")

    # Add defailt args.
    parser.add_argument(
        '--base-dir', help="Base path for gitomatic", action='store',
        default='~/.gitomatic')

    parser.add_argument(
        '--ssh-dir', help="Base path for ssh", action='store',
        default='~/.ssh')

    parser.add_argument(
        '--force', action='store_true', help="Base path for gitomatic",
        default=False)

    parser.add_argument(
        '--init', action='store_true', help="Initialize gitomatic",
        default=False)

    # Commands subparser
    commands = parser.add_subparsers(title='Gitomatic commands')

    RepositoryCommands()._add_to_parser(commands)
    KeysCommands()._add_to_parser(commands)
    InitCommands()._add_to_parser(commands)
    PermissionCommands()._add_to_parser(commands)
    HookCommands()._add_to_parser(commands)

    args = parser.parse_args()
    args.func(args)

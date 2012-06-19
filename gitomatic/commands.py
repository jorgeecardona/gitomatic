from configuration import Configuration
import functools
from gitomatic import Gitomatic


class BaseCommands(object):

    def _wrap_func(self, orig_func, args):

        # Create the base gitomatic.
        self.gitomatic = Gitomatic(conf=Configuration(
            base_dir=args.base_dir, ssh_dir=args.ssh_dir, force=args.force))

        orig_func(args)


class InitCommands(BaseCommands):
    " Init commands."

    def _add_to_parser(self, commands):
        " Add to parser."

        init = commands.add_parser('initialize')
        init.set_defaults(func=functools.partial(self._wrap_func, self.init))

    def init(self, args):
        # self._extract_configuration(args)
        self.gitomatic.initialize()


class RepositoryCommands(BaseCommands):
    " Base commands for repositories."

    def _add_to_parser(self, commands):
        " Add to parser."

        # Create subcommands.
        subcommands = commands.add_parser('repository').add_subparsers(
            title='Create and delete repositories')

        # Add basic subcommands.
        create = subcommands.add_parser('create')
        create.add_argument('name', help="Name of the repository")
        create.set_defaults(
            func=functools.partial(self._wrap_func, self.create))

        delete = subcommands.add_parser('delete')
        delete.add_argument('name', help="Name of the repository")
        delete.set_defaults(
            func=functools.partial(self._wrap_func, self.delete))

    def create(self, args):
        " Create from the cli."
        return self.gitomatic.repository.create(args.name)

    def delete(self, args):
        " Delete from the cli."
        return self.gitomatic.repository.delete(args.name)


class KeysCommands(BaseCommands):
    " Keys commands"

    def _add_to_parser(self, commands):
        " Add to parser."

        # Create subcommands.
        subcommands = commands.add_parser('keys').add_subparsers(
            title='Add and remove keys of users')

        # Add basic subcommands.
        add = subcommands.add_parser('add')
        add.add_argument('username', help="Add the key to this user")
        add.add_argument('-f', '--filename', help="Filename holding the key")
        add.add_argument('-k', '--key', help="Literal key")
        add.set_defaults(func=functools.partial(self._wrap_func, self.add))

        remove = subcommands.add_parser('remove')
        remove.add_argument('username', help="Remove the key to this user")
        remove.add_argument('--hash', help="Hash of the key.")
        remove.set_defaults(
            func=functools.partial(self._wrap_func, self.remove))

    def add(self, args):
        " Add from the CLI."

        if args.key is not None:
            key = args.key

        elif args.filename is not None:
            with open(args.filename) as fd:
                key = fd.read()

        else:
            raise Exception("Specify a key.")

        return self.gitomatic.keys.add(args.username, key)

    def remove(self, args):
        " Remove from the cli"

        return self.gitomatic.keys.remove(args.username, args.key_hash)


class PermissionsCommands(BaseCommands):
    " Permissions commands."

    def _add_to_parser(self, commands):

        # Create subcommands.
        subcommands = commands.add_parser('permissions').add_subparsers(
            title='Add and remove permissions.')

        # Add basic subcommands.
        add = subcommands.add_parser('add')
        add.add_argument('username')
        add.add_argument('-r', '--repository', required=True)
        add.add_argument('perm')
        add.set_defaults(func=functools.partial(self._wrap_func, self.add))

        remove = subcommands.add_parser('remove')
        remove.add_argument('-r', '--repository', required=True)
        remove.add_argument('username')
        remove.add_argument('perm')
        remove.set_defaults(
            func=functools.partial(self._wrap_func, self.remove))

    def add(self, args):
        self.gitomatic.permission.add(
            args.username, args.repository, args.perm)

    def remove(self, args):
        self.gitomatic.permission.remove(
            args.username, args.repository, args.perm)


class HooksCommands(BaseCommands):

    def _add_to_parser(self, commands):

        # Create subcommands.
        subcommands = commands.add_parser('hooks').add_subparsers(
            title='Add and remove hooks')

        # Add basic subcommands.
        add = subcommands.add_parser('add')
        add.add_argument('-r', '--repository', required=True)
        add.add_argument('--hook', required=True)
        add.add_argument(
            '-f', '--filename', help="Hook's filename", required=True)
        add.set_defaults(func=functools.partial(self._wrap_func, self.add))

        remove = subcommands.add_parser('remove')
        remove.add_argument('-r', '--repository', required=True)
        remove.add_argument('hook')
        remove.set_defaults(
            func=functools.partial(self._wrap_func, self.remove))

    def add(self, args):
        with open(args.filename) as fd:
            content = fd.read()
        self.gitomatic.hook.add(args.repository, args.hook, content)

    def remove(self, args):
        self.gitomatic.hook.remove(args.repository, args.hook)

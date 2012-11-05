import os


class Configuration(object):
    " Control the configuration of gitomatic from a single class."

    def __init__(self, base_dir='~/.gitomatic', ssh_dir='~/.ssh', force=False):

        # Set base info.
        self.base_dir = base_dir
        self.force = force

        # Default paths.
        self.gitomatic_path = os.path.expanduser(self.base_dir)
        self.keys_path = os.path.join(self.gitomatic_path, 'keys')
        self.repositories_path = os.path.join(
            self.gitomatic_path, 'repositories')

        # SSH path.
        self.ssh_path = os.path.expanduser(ssh_dir)

        # Authorized keys.
        self.authorized_keys = os.path.join(self.ssh_path, 'authorized_keys')

        # Command to authenticate.
        self.command = 'gitomatic-auth'

        # Valid permissions.
        self.valid_permissions = ['', 'R', 'RW', 'RW+']

    def repository_path(self, name):
        " Return the path of a single repository."
        if not name.endswith('.git'):
            name += '.git'
        return os.path.join(self.repositories_path, name)

    def hook_path(self, repository, hook):
        " Return the path to a hook."
        return os.path.join(self.repository_path(repository), 'hooks', hook)

    def key_path(self, basename):
        # Get Key path.
        return os.path.join(self.keys_path, basename)


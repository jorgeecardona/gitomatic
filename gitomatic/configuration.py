import os
import argparse
import configobj


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


def global_hooks(self):
    " Return global hooks path."


def main():
    " Function called for 'gitomatic-configuration'"

    # Global parser.
    parser = argparse.ArgumentParser(description="Gitomatic configuration.")

    # Read hooks path.
    parser.add_argument('--global-hooks', type=bool, help="Global hooks path.")

    args = parser.parse_args()
    args.func(args)


def read_all_configurations():

    home_path = os.environ['HOME']
    conf_path = os.path.join(
        home_path, '.gitomatic', 'conf.d')

    # Build configurations.
    files = os.walk(conf_path).next()[2]

    confs = []

    for filename in files:
        confs.append(configobj.ConfigObj(os.path.join(
            conf_path, filename)))

    return confs


def read_permission(repo, username):

    confs = read_all_configurations()

    for conf in confs:
        if repo in conf:
            if username in conf[repo]:
                return set(conf[repo][username])
    return set()


def write_permission(repo, username, perm):
    # Valiuate permissions
    perm = validate_perms(perm)

    confs = read_all_configurations()

    for conf in confs:
        if repo in conf:
            if username in conf[repo]:
                conf[repo][username] = perm
                conf.write()
                return set(conf[repo][username])

    # New permission in global file.
    conf = confs[0]
    if repo not in conf:
        conf[repo] = {}

    conf[repo][username] = perm
    conf.write()
    return set(conf[repo][username])


def validate_perms(perms):
    # Permissions sets
    valid_permissions = ['', 'R', 'RW', 'RW+']
    valid = valid_permissions[0]

    # Valid permissions.
    for permission in valid_permissions[1:]:
        if set(permission).issubset(perms):
            valid = permission
        else:
            break

    # Return valid permission.
    return valid

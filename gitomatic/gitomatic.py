import os
import git
import re
import shutil

from hashlib import sha1

from configuration import Configuration


class GitomaticBase(object):
    def __init__(self, conf=None):
        self.conf = conf


class GitomaticPermission(GitomaticBase):

    def check(self, username, repository, perm):

        real_perm = self.get(username, repository)

        return set(perm).issubset(real_perm)

    def validate(self, perm):

        valid = self.conf.valid_permissions[0]

        # Valid permissions.
        for permission in self.conf.valid_permissions[1:]:
            if set(permission).issubset(perm):
                valid = permission
            else:
                break

        # Return valid permission.
        return valid

    def set(self, username, repository, perm):

        # Get repository
        repository = git.Repo(self.conf.repository_path(repository))

        # Validate permission.
        perm = self.validate(perm)

        # Configurations.
        c = repository.config_writer()

        # Add permission section if it doesn't  exists.
        if not c.has_section('permissions'):
            c.add_section('permissions')

        # Add a permission.
        username = 'sha1-%s' % (sha1(username).hexdigest(), )
        c.set('permissions', username, perm)

        return c.get('permissions', username)

    def get(self, username, repository):
        " Get the permissions of username on repository"

        # Get repository
        repository = git.Repo(self.conf.repository_path(repository))

        # Configurations.
        c = repository.config_reader()

        # Add permission section if it doesn't  exists.
        if not c.has_section('permissions'):
            return set()

        # Add a permission.
        username = 'sha1-%s' % (sha1(username).hexdigest(), )
        try:
            return set(c.get('permissions', username))
        except Exception:
            return set()

    def add(self, username, repository, perm):
        " Add permission of username on repository."

        # Add a permission.
        perms = self.get(username, repository)

        # Compute new permissions
        new_perms = perms.union(set(perm))

        # Write new permission
        self.set(username, repository, new_perms)

        return username

    def remove(self, username, repository, perm):
        " Remove permission of username on repository."

        # Add a permission.
        perms = self.get(username, repository)

        # Compute new permissions
        new_perms = perms - set(perm)

        # Write new permission
        self.set(username, repository, new_perms)

        return username


class GitomaticRepository(GitomaticBase):

    def get(self, name):
        " Get a repository from its name."
        return git.Repo(self.conf.repository_path(name))

    def create(self, name):
        " Create a new repository."

        # Repository path.
        repository_path = self.conf.repository_path(name)

        # Check if path exists.
        if os.path.exists(repository_path):
            raise Exception("The directory of the repo is already used.")

        # Create repo
        repository = git.Repo.init(repository_path, bare=True)

        return repository

    def delete(self, name):
        " Delete a repository."

        # Repository path.
        repository_path = self.conf.repository_path(name)

        if not os.path.exists(repository_path):
            raise Exception("Repo doesn't not exist.")

        # Remove path.
        shutil.rmtree(repository_path)

        return name


class GitomaticKeys(GitomaticBase):

    def remove(self, username, key_hash):
        " Remove a key based on the username and the hash."

        # Get filename
        basename = '%s:%s' % (username, key_hash)

        # Read key.
        with open(self.conf.key_path(basename)) as fd:
            data = fd.read()

        if key_hash != sha1(data).hexdigest():
            raise Exception("Invalid hash.")

        # Remove path
        os.remove(self.conf.key_path(basename))

        # Update Authorized Keys
        self.update_authorized_keys()

        return username

    def add(self, username, key):
        " Add a new user."

        # Get hash of the key.
        key_hash = sha1(key).hexdigest()
        basename = '%s:%s' % (username, key_hash)

        # Write key
        with open(self.conf.key_path(basename), 'w') as fd:
            fd.write(key)

        # Update Authorized Keys
        self.update_authorized_keys()

        # Return the Key
        return key_hash

    def update_authorized_keys(self):

        # Build gitomatic section.
        gitomatic_sections = ['### Start Gitomatic ###']

        # Gather keys.
        filenames = os.walk(self.conf.keys_path).next()[2]
        for filename in filenames:

            # Username and hash_key
            username, key_hash = filename.split(':')

            # Read Key
            with open(os.path.join(self.conf.keys_path, filename)) as fd:
                key = fd.read()

            # Create entry
            cmd = '%s %s' % (self.conf.command, username, )
            gitomatic_sections.append(
                "command=\"%s\",no-port-forwarding,no-X11-forwarding,"\
                "no-agent-forwarding,no-pty %s" % (cmd, key))

        #  Gitomatic final section
        gitomatic_sections.append('### End Gitomatic ###')
        gitomatic_sections = "\n\n".join(gitomatic_sections)

        # Read authorized_keys
        try:
            with open(self.conf.authorized_keys) as fd:
                authorized_keys = fd.read()
        except IOError:
            authorized_keys = ''

        # Extract gitomatic section.
        regex = re.compile(
            '(.*)### Start Gitomatic ###.*?### End Gitomatic ###(.*).*',
            re.DOTALL | re.MULTILINE)
        res = regex.match(authorized_keys)

        if res:
            # Remove gitomatic keys.
            authorized_keys = list(res.groups())
            authorized_keys.insert(1, gitomatic_sections)
            authorized_keys = "".join(authorized_keys)
        else:
            authorized_keys += "\n" + gitomatic_sections

        # Write authorized_keys
        with open(self.conf.authorized_keys, 'w') as fd:
            os.fchmod(fd.fileno(), 0600)
            fd.write(authorized_keys)


class GitomaticHook(GitomaticBase):
    " Hook commands."

    def add(self, repository, hook, content):

        # Add hook in order.
        hook_path = self.conf.hook_path(repository, hook)

        # Create file
        with open(hook_path, 'w') as fd:
            fd.write(content)
            os.fchmod(fd.fileno(), 0750)

        return hook_path

    def remove(self, repository, hook):

        # Add hook in order.
        hook_path = self.conf.hook_path(repository, hook)

        if os.path.exists(hook_path):
            os.unlink(hook_path)


class Gitomatic(GitomaticBase):
    " Base object in gitomatic."

    def __init__(self, conf=None):
        " Set the basic configuration in place."

        if conf is None:
            conf = Configuration()

        super(Gitomatic, self).__init__(conf=conf)

        # Basic structure.
        self.repository = GitomaticRepository(conf=self.conf)
        self.keys = GitomaticKeys(conf=self.conf)
        self.permission = GitomaticPermission(conf=self.conf)
        self.hook = GitomaticHook(conf=self.conf)

    def _create_directory(self, path, mode):
        print "Creating %s ..." % (path, )
        os.mkdir(path, mode)
        os.chown(path, os.geteuid(), os.getegid())

    def _ensure_directory(self, path, mode=0700):
        " Ensure a directory."

        if not os.path.exists(path):
            self._create_directory(path, mode)

        elif os.path.isdir(path):
            os.chmod(path, mode)
            os.chown(path, os.geteuid(), os.getegid())

        elif self.conf.force:
            print "Delete file in location %s."
            os.unlink(path)
            self._create_directory(path, mode)

        else:
            raise self.EnsureDirectory(path)

    def initialize(self):
        " Initialize the gitomatic fs structure."

        print "Initialize gitomatic ..."

        # Create .ssh path.
        self._ensure_directory(self.conf.ssh_path, 0700)

        # Create gitomatic path.
        self._ensure_directory(self.conf.gitomatic_path, 0750)

        # Create gitomatic keys path.
        self._ensure_directory(self.conf.keys_path, 0750)

        # Create gitomatic repos path.
        self._ensure_directory(self.conf.repositories_path, 0750)

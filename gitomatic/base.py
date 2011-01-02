import re
import tempfile
import os
import subprocess
import shutil
import logging
import configobj
from hashlib import sha1


class Gitomatic(object):
    """
    This class hold all the information of a gitomatic instance.
    """

    def __init__(self, base_path=None, virtualenv=None):

        if base_path is None:
            base_path = os.environ['HOME']

        self.home_path = base_path
        self.ssh_path = os.path.join(self.home_path, '.ssh')
        self.authorized_path = os.path.join(self.ssh_path, 'authorized_keys')
        self.gitomatic_path = os.path.join(self.home_path, '.gitomatic')
        self.keys_path = os.path.join(self.gitomatic_path, 'keys')
        self.conf_path = os.path.join(self.gitomatic_path, 'conf.d')
        self.repos_path = os.path.join(self.gitomatic_path, 'repos')

        # SSH Command for virtualenv.
        if virtualenv:
            self.command = os.path.join(virtualenv, 'bin', 'gitomatic-auth')
        else:
            self.command = 'gitomatic-auth'

        # Valid permissions in order.
        self.valid_permissions = ['', 'R', 'RW', 'RW+']

    def initialize(self):
        """
        Initialize all the system.
        """

        # Create .ssh path.
        if not os.path.exists(self.ssh_path):
            print "Creating %s ..." % (self.ssh_path, )
            os.mkdir(self.ssh_path, 0o700)
            os.chown(self.ssh_path, os.geteuid(), os.getegid())

        # Create gitomatic path.
        if not os.path.exists(self.gitomatic_path):
            print "Creating %s ..." % (self.gitomatic_path, )
            os.mkdir(self.gitomatic_path, 0o750)
            os.chown(self.gitomatic_path, os.geteuid(), os.getegid())

        # Create gitomatic keys path.
        if not os.path.exists(self.keys_path):
            print "Creating %s ..." % (self.keys_path, )
            os.mkdir(self.keys_path, 0o750)
            os.chown(self.keys_path, os.geteuid(), os.getegid())

        # Create gitomatic conf path.
        if not os.path.exists(self.conf_path):
            print "Creating %s ..." % (self.conf_path, )
            os.mkdir(self.conf_path, 0o750)
            os.chown(self.conf_path, os.geteuid(), os.getegid())

        # Create gitomatic repos path.
        if not os.path.exists(self.repos_path):
            print "Creating %s ..." % (self.repos_path, )
            os.mkdir(self.repos_path, 0o750)
            os.chown(self.repos_path, os.geteuid(), os.getegid())

    def repo_add(self, name):
        # Get repo path.
        repo_path = os.path.join(self.repos_path, name)

        if os.path.exists(repo_path):
            raise Exception("Duplicated repo.")

        # Create repo.
        p = subprocess.Popen(['git', 'init', '--bare', repo_path],
                             stdout=-1, stderr=-1)
        ret = p.wait()
        stdout, stderr = p.communicate()

        if stderr != '':
            logging.error(stderr)
        if stdout != '':
            logging.info(stdout)

        if ret != 0:
            raise Exception("Git error.")

        return name

    def repo_delete(self, name):

        # Get repo path.
        repo_path = os.path.join(self.repos_path, name)

        if not os.path.exists(repo_path):
            raise Exception("Repo doesn't not exist.")

        # Remove path.
        shutil.rmtree(repo_path)

        return name

    def repo_archive(self, name, tree='HEAD'):

        # Get repo path.
        repo_path = os.path.join(self.repos_path, name)

        if not os.path.exists(repo_path):
            raise Exception("Repo doesn't not exist.")

        # Create repo.
        p = subprocess.Popen(['git', 'archive', '--format==zip', tree],
                             cwd=repo_path, stdout=-1, stderr=-1)
        ret = p.wait()
        stdout, stderr = p.communicate()

        if stderr != '':
            logging.error(stderr)

        if ret != 0:
            raise Exception("Git error.")

        return stdout

    def key_add(self, username, key):

        # Test for Valid Key.

        # Get hash of the key.
        hash_ = sha1(key).hexdigest()
        basename = '%s:%s' % (username, hash_)

        # Get Key path.
        key_path = os.path.join(self.keys_path, basename)

        # Write key
        fd = open(key_path, 'w')
        fd.write(key)
        fd.close()

        # Update Authorized Keys
        self.update_authorized_keys()

        # Return the Key
        return hash_

    def key_delete(self, username, hash_):

        # Get filename
        basename = '%s:%s' % (username, hash_)

        # Get Key path.
        key_path = os.path.join(self.keys_path, basename)

        # Read key.
        fd = open(key_path)
        data = fd.read()
        fd.close()

        if hash_ != sha1(data).hexdigest():
            raise Exception("Invalid hash.")

        # Remove path
        os.remove(key_path)

        # Update Authorized Keys
        self.update_authorized_keys()

        return username

    def update_authorized_keys(self):

        # Build gitolite section.
        gitolite_section = ['### Start Gitolite ###']

        # Gather keys.
        filenames = os.walk(self.keys_path).next()[2]
        for filename in filenames:
            # Userbame and hash_key
            username, hash_ = filename.split(':')

            # Read Key
            fd = open(os.path.join(self.keys_path, filename))
            key = fd.read()
            fd.close()

            # Create entry
            cmd = '%s %s' % (self.command, username, )
            gitolite_section.append(
                "command=\"%s\",no-port-forwarding,no-X11-forwarding,"\
                "no-agent-forwarding,no-pty %s" % (cmd, key))

        #  Gitolite final section
        gitolite_section.append('### End Gitolite ###')
        gitolite_section = "\n\n".join(gitolite_section)

        # Read authorized_keys
        try:
            fd = open(self.authorized_path)
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
        fd = open(self.authorized_path, 'w')
        os.fchmod(fd.fileno(), 0o600)
        fd.write(authorized_keys)
        fd.close()

    def perm_read(self, repo, username):
        # Get conf path
        conf_path = os.path.join(self.conf_path, repo)

        # Read Configuration.
        config = configobj.ConfigObj(conf_path)

        if username in config:
            return set(config[username])

        return set()

    def validate_perm(self, perm):
        valid = self.valid_permissions[0]

        # Valid permissions.
        for permission in self.valid_permissions[1:]:
            if set(permission).issubset(perm):
                valid = permission
            else:
                break

        # Return valid permission.
        return valid

    def perm_write(self, repo, username, perm):

        perm = self.validate_perm(perm)

        # Get conf path
        conf_path = os.path.join(self.conf_path, repo)

        # Read Configuration.
        config = configobj.ConfigObj(conf_path)

        # Write to file
        config[username] = perm
        config.write()

        return set(config[username])

    def perm_add(self, username, repo, perm):
        # Add a permission.
        actual = self.perm_read(repo, username)

        # Compute new permissions
        new_perm = actual.union(set(perm))

        # Write new permission
        self.perm_write(repo, username, new_perm)

        return username

    def perm_delete(self, username, repo, perm):
        # Add a permission.
        actual = self.perm_read(repo, username)

        # Compute new permissions
        new_perm = actual - set(perm)

        # Write new permission
        self.perm_write(repo, username, new_perm)

        return username

    def perm_check(self, username, repo, perm):
        # Read perm
        real_perm = self.perm_read(repo, username)

        return set(perm).issubset(real_perm)

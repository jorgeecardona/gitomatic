# import logging
# from hashlib import sha1
# import configobj
# import shutil
# import git
# import re
# import os
# import StringIO


# class Gitomatic(object):

#     class EnsureDirectory(Exception):
#         def __init__(self, path):
#             super(Exception, self).__init__(
#                 "Impossible to ensure directory %s" % (path, ))

#     def __init__(self, rc='~/.gitomatic.rc'):

#         # Try to read configuration.
#         config_path = os.path.expanduser(rc)

#         # Read configuration.
#         configuration = configobj.ConfigObj(config_path)

#         if 'global' not in configuration:
#             configuration['global'] = {}

#         # SSH path.
#         if 'ssh_path' in configuration['global']:
#             self.ssh_path = configuration['global']['ssh_path']
#         else:
#             self.ssh_path = os.path.expanduser('~/.ssh')

#         #  Gitomatic path.
#         if 'gitomatic_path' in configuration['global']:
#             self.gitomatic_path = configuration['global']['gitomatic_path']
#         else:
#             self.gitomatic_path = os.path.expanduser('~/.gitomatic')

#         # Repositories path.
#         if 'repositories_path' in configuration['global']:
#             self.repositories_path = \
#                                    configuration['global']['repositories_path']
#         else:
#             self.repositories_path = os.path.join(
#                 self.gitomatic_path, 'repositories')

#         # Keys path.
#         if 'keys_path' in configuration['global']:
#             self.keys_path = configuration['global']['keys_path']
#         else:
#             self.keys_path = os.path.join(
#                 self.gitomatic_path, 'keys')

#         # Command path.
#         if 'command' in configuration['global']:
#             self.command = configuration['global']['command']
#         else:
#             self.command = 'gitomatic-auth'

#         # Valid permissions
#         if 'permissions' in configuration['global']:
#             self.valid_permissions = configuration['global']['permissions']
#         else:
#             self.valid_permissions = ['', 'R', 'RW', 'RW+']

#         # Global hooks.
#         self.gitomatic_hooks = os.path.join(self.gitomatic_path, 'hooks')

    # def _create_directory(self, path, mode):
    #     print "Creating %s ..." % (path, )
    #     os.mkdir(path, mode)
    #     os.chown(path, os.geteuid(), os.getegid())

    # def _ensure_directory(self, path, mode=0700):
    #     " Ensure a directory."

    #     if not os.path.exists(path):
    #         self._create_directory(path, mode)

    #     elif os.path.isdir(path):
    #         os.chmod(path, mode)
    #         os.chown(path, os.geteuid(), os.getegid())

    #     elif self.conf.force:
    #         print "Delete file in location %s."
    #         os.unlink(path)
    #         self._create_directory(path, mode)

    #     else:
    #         raise self.EnsureDirectory(path)

    # def initialize(self):
    #     """
    #     Initialize all the system.
    #     """

    #     # Create .ssh path.
    #     self._ensure_directory(self.ssh_path, 0700)

    #     # Create gitomatic path.
    #     self._ensure_directory(self.gitomatic_path, 0750)

    #     # Create gitomatic keys path.
    #     self._ensure_directory(self.keys_path, 0750)

    #     # Create gitomatic repos path.
    #     self._ensure_directory(self.repositories_path, 0750)

    # def _repo_path(self, name):
    #     if not name.endswith('.git'):
    #         name += '.git'
    #     return os.path.join(self.repositories_path, name)

    # def get_repository(self, name):
    #     " Get a repository using its name."

    #     return git.Repo(self._repo_path(name))

    # def repo_add(self, name):

    #     # Get repo location
    #     repo_path = self._repo_path(name)

    #     # Check if path exists.
    #     if os.path.exists(repo_path):
    #         raise Exception("The directory of the repo is already used.")

    #     # Create repo
    #     repo = git.Repo.init(repo_path, bare=True)

    #     # Create hooks skel
    #     self._create_hook_skel(name)

    #     return repo

    # def repo_delete(self, name):
    #     # Get repo path.
    #     repo_path = self._repo_path(name)

    #     if not os.path.exists(repo_path):
    #         raise Exception("Repo doesn't not exist.")

    #     # Remove path.
    #     shutil.rmtree(repo_path)

    #     return name

    # def repo_archive(self, name, treeish='HEAD'):

    #     # Get repo path.
    #     repo_path = self._repo_path(name)

    #     # Get repo.
    #     repo = git.Repo(repo_path)

    #     # Create archive buffer
    #     archive = StringIO.StringIO()
    #     repo.archive(archive, treeish=treeish, format='zip')
    #     archive.close()

    #     return ''.join(archive.buflist)

    # def key_add(self, username, key):

    #     # Get hash of the key.
    #     hash_ = sha1(key).hexdigest()
    #     basename = '%s:%s' % (username, hash_)

    #     # Get Key path.
    #     key_path = os.path.join(self.keys_path, basename)

    #     # Write key
    #     fd = open(key_path, 'w')
    #     fd.write(key)
    #     fd.close()

    #     # Update Authorized Keys
    #     self.update_authorized_keys()

    #     # Return the Key
    #     return hash_

    # def key_delete(self, username, hash_):

    #     # Get filename
    #     basename = '%s:%s' % (username, hash_)

    #     # Get Key path.
    #     key_path = os.path.join(self.keys_path, basename)

    #     # Read key.
    #     fd = open(key_path)
    #     data = fd.read()
    #     fd.close()

    #     if hash_ != sha1(data).hexdigest():
    #         raise Exception("Invalid hash.")

    #     # Remove path
    #     os.remove(key_path)

    #     # Update Authorized Keys
    #     self.update_authorized_keys()

    #     return username

    # def update_authorized_keys(self):

    #     # Build gitolite section.
    #     gitolite_section = ['### Start Gitolite ###']

    #     # Gather keys.
    #     filenames = os.walk(self.keys_path).next()[2]
    #     for filename in filenames:
    #         # Userbame and hash_key
    #         username, hash_ = filename.split(':')

    #         # Read Key
    #         fd = open(os.path.join(self.keys_path, filename))
    #         key = fd.read()
    #         fd.close()

    #         # Create entry
    #         cmd = '%s %s' % (self.command, username, )
    #         gitolite_section.append(
    #             "command=\"%s\",no-port-forwarding,no-X11-forwarding,"\
    #             "no-agent-forwarding,no-pty %s" % (cmd, key))

    #     #  Gitolite final section
    #     gitolite_section.append('### End Gitolite ###')
    #     gitolite_section = "\n\n".join(gitolite_section)

    #     # Read authorized_keys
    #     try:
    #         fd = open(os.path.join(self.ssh_path, 'authorized_keys'))
    #         authorized_keys = fd.read()
    #         fd.close()
    #     except IOError:
    #         authorized_keys = ''

    #     # Extract gitolite section.
    #     regex = re.compile(
    #         '(.*)### Start Gitolite ###.*?### End Gitolite ###(.*).*',
    #         re.DOTALL | re.MULTILINE)
    #     res = regex.match(authorized_keys)

    #     if res:
    #         # Remove gitolite keys.
    #         authorized_keys = list(res.groups())
    #         authorized_keys.insert(1, gitolite_section)
    #         authorized_keys = "".join(authorized_keys)
    #     else:
    #         authorized_keys += "\n" + gitolite_section

    #     # Write authorized_keys
    #     fd = open(os.path.join(self.ssh_path, 'authorized_keys'), 'w')
    #     os.fchmod(fd.fileno(), 0600)
    #     fd.write(authorized_keys)
    #     fd.close()

    # def perm_read(self, username, repo):
    #     # Get repo
    #     repo = self._get_repo(repo)

    #     # Configurations.
    #     c = repo.config_reader()

    #     # Add permission section if it doesn't  exists.
    #     if not c.has_section('permissions'):
    #         return set()

    #     # Add a permission.
    #     username = 'sha1-%s' % (sha1(username).hexdigest(), )
    #     try:
    #         return set(c.get('permissions', username))
    #     except Exception, e:
    #         logging.info(e)
    #         return set()

    # def validate_perm(self, perm):

    #     valid = self.valid_permissions[0]

    #     # Valid permissions.
    #     for permission in self.valid_permissions[1:]:
    #         if set(permission).issubset(perm):
    #             valid = permission
    #         else:
    #             break

    #     # Return valid permission.
    #     return valid

    # def perm_write(self, username, repo, perm):

    #     # Get repo
    #     repo = self._get_repo(repo)

    #     # Validate permission.
    #     perm = self.validate_perm(perm)

    #     # Configurations.
    #     c = repo.config_writer()

    #     # Add permission section if it doesn't  exists.
    #     if not c.has_section('permissions'):
    #         c.add_section('permissions')

    #     # Add a permission.
    #     username = 'sha1-%s' % (sha1(username).hexdigest(), )
    #     c.set('permissions', username, perm)

    #     return c.get('permissions', username)

    # def perm_add(self, username, repo, perm):

    #     # Add a permission.
    #     actual = self.perm_read(username, repo)

    #     # Compute new permissions
    #     new_perm = actual.union(set(perm))

    #     # Write new permission
    #     self.perm_write(username, repo, new_perm)

    #     return username

    # def perm_delete(self, username, repo, perm):
    #     # Add a permission.
    #     actual = self.perm_read(username, repo)

    #     # Compute new permissions
    #     new_perm = actual - set(perm)

    #     # Write new permission
    #     self.perm_write(username, repo, new_perm)

    #     return username

    # def perm_check(self, username, repo, perm):
    #     # Read perm
    #     real_perm = self.perm_read(username, repo)

    #     return set(perm).issubset(real_perm)

#     def hook_add(self, repo, type, hook, name, order=0):

#         # Create hook structure.
#         self._create_hook_skel(repo)

#         # Get repo
#         repo = self._get_repo(repo)

#         # Add hook in order.
#         hook_path = os.path.join(
#             repo.git_dir, 'hooks', '%s.d' % (type, ), '%03d-%s' % (
#                 order, name))

#         # Create file
#         fd = open(hook_path, 'w')
#         fd.write(hook)
#         os.fchmod(fd.fileno(), 0750)
#         fd.close()

#         return hook_path

#     def hook_delete(self, repo, type, name, order=0):

#         # Create hook structure.
#         self._create_hook_skel(repo)

#         # Add hook in order.
#         hook_path = os.path.join(
#             self.repositories_path, repo, 'hooks', '%s.d' % (type, ),
#             '%03d-%s' % (order, name))

#         # Delete hook
#         os.remove(hook_path)

#         return hook_path

#     def _create_hook_skel(self, name):

#         # Get repo
#         repo = self._get_repo(name)

#         # Hooks to create.
#         hooks = ['post-receive']

#         for hook in hooks:
#             # Create hook path.
#             hooks_path = os.path.join(repo.git_dir, 'hooks', hook + '.d')

#             # Create directory.
#             if not os.path.exists(hooks_path):
#                 os.mkdir(hooks_path, 0750)
#             os.chown(hooks_path, os.geteuid(), os.getegid())
#             #os.chown(hooks_path, self.owner, self.group)

#             hook_path = os.path.join(repo.git_dir, 'hooks', hook)

#             # Replace hook for a script that calls the internal hooks.
#             fd = open(hook_path, 'w')
#             fd.write("""
# cd ${0}.d
# while read oldrev newrev refname
# do
#   for i in $(find . -regex './[0-9][0-9][0-9]-.*[^~]')
#   do
#     echo "$oldrev $newrev $refname" | $i
#   done
# done
# """)
#             os.fchmod(fd.fileno(), 0750)
#             fd.close()

#         return repo

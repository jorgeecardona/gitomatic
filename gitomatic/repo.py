import logging
import os
import git


class Repo(git.Repo):

    @classmethod
    def init(self, path, mkdir=True, **kwargs):
        # Create repository in bare format.
        kwargs['bare'] = True

        # Init repo.
        repo = super(Repo, self).init(path, mkdir, **kwargs)

        # Create hook structures.
        repo._create_hook_structure()


    def _create_hook_structure(self):
        # For every hook create a hook.d path.
        hooks = ['post-receive']

        for hook in hooks:
            # Create hook path.
            hooks_path = os.path.join(self.git_dir, 'hooks', hook + '.d')
            if not os.path.exists(hooks_path):
                os.mkdir(hooks_path, 0o750)
                os.chown(hooks_path, self.owner, self.group)

            hook_path = os.path.join(self.git_dir, 'hooks', hook)

            # Replace hook for a script that calls the internal hooks.
            fd = open(hook_path, 'w')
            fd.write("""
cd ${0}.d
while read oldrev newrev refname
do
  for i in $(find . -regex './[0-9][0-9][0-9]-.*')
  do
    echo '$oldrev $newrev $refname' | $i
  done
done
""")
            fd.close()

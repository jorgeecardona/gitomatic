import os
import logging
import shutil
import subprocess


def add(name):

    # Add a new repo.
    home_path = os.environ['HOME']
    repo_path = os.path.join(
        home_path, '.gitomatic/repos', name)

    if os.path.exists(repo_path):
        raise Exception("Duplicated repo")

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


def remove(name):
    # Remove a repo.
    home_path = os.environ['HOME']
    repo_path = os.path.join(
        home_path, '.gitomatic/repos', name)

    if not os.path.exists(repo_path):
        raise Exception("Repo doesn't not exist.")

    # Remove path.
    shutil.rmtree(repo_path)

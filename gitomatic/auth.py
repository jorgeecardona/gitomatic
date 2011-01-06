import argparse
import logging
import os
import re
import subprocess
from base import Gitomatic


def upload_pack(repo):
    g = Gitomatic()
    repo = g._get_repo(repo)
    p = subprocess.Popen(['/usr/bin/git-upload-pack', repo.git_dir])
    return p.wait()


def receive_pack(repo):
    g = Gitomatic()
    repo = g._get_repo(repo)
    p = subprocess.Popen(['/usr/bin/git-receive-pack', repo.git_dir])
    return p.wait()


def main():

    # Start Parser
    parser = argparse.ArgumentParser(
        description="Git auth tool.")
    parser.add_argument('username')
    args = parser.parse_args()

    # Get ids
    username = args.username
    try:
        command = os.environ['SSH_ORIGINAL_COMMAND']
    except KeyError:
        logging.error('Command missed.')
        exit(2)

    # Commands handler.
    commands_regex = {

        re.compile(r"git-upload-pack '(?P<repo>[a-zA-Z0-9_.]*?.git)'"): (
            upload_pack, 'R'),

        re.compile(r"git-receive-pack '(?P<repo>[a-zA-Z0-9_.]*?.git)'"): (
            receive_pack, 'RW'),

        }

    # Get Gitomatic object.
    g = Gitomatic()

    for regex in commands_regex:
        res = regex.match(command)
        if res:
            # Retrieve function and permissions
            fn, perm = commands_regex[regex]

            # repo
            repo = res.groupdict()['repo']

            # Check permission
            check = g.perm_check(username, repo, perm)

            # Call handler if check
            if check:
                exit(fn(**res.groupdict()))
            else:
                logging.error("Incorrect permissions.")
                exit(2)

    logging.error(command)
    exit(1)

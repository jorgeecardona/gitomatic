import argparse
import logging
import os
import re
import subprocess
import configuration
from base import Gitomatic


def upload_pack(repo):
    repo_path = os.path.join('~/.gitomatic/repos', repo)
    p = subprocess.Popen(['/usr/bin/git-upload-pack', repo_path])
    return p.wait()


def receive_pack(repo):
    repo_path = os.path.join('~/.gitomatic/repos', repo)
    p = subprocess.Popen(['/usr/bin/git-receive-pack', repo_path])
    return p.wait()


def check_permissions(username, perms, repo):
    actual_perms = configuration.read_permission(repo, username)
    return set(perms).issubset(actual_perms)


def main():

    # Start Parser
    parser = argparse.ArgumentParser(
        description="Git auth tool.")
    parser.add_argument('username')
    args = parser.parse_args()

    # Get Gitomatic object.
    g = Gitomatic()

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

    for regex in commands_regex:
        res = regex.match(command)
        if res:
            # Retrieve function and permissions
            fn, perm = commands_regex[regex]

            # Check permission
            check = g.perm_check(
                username=username,
                perm=perm,
                **res.groupdict())

            # Call handler if check
            if check:
                exit(fn(**res.groupdict()))
            else:
                logging.error("Incorrect permissions.")
                exit(2)

    logging.error(command)
    exit(1)

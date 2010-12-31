import re
import os
from hashlib import sha1


def add(username, key):

    # Test for Valid Key.

    # Get hash of the key.
    hash_ = sha1(key).hexdigest()
    basename = '%s:%s' % (username, hash_)

    home_path = os.environ['HOME']
    key_path = os.path.join(
        home_path, '.gitomatic/keys', basename)

    # Write key
    fd = open(key_path, 'w')
    fd.write(key)
    fd.close()

    # Update Authorized Keys
    update_authorized_keys()

    # Return the Key
    return hash_


def remove(username, hash_):

    # Get filename
    basename = '%s:%s' % (username, hash_)
    home_path = os.environ['HOME']
    key_path = os.path.join(
        home_path, '.gitomatic/keys', basename)

    # Read key.
    fd = open(key_path)
    data = fd.read()
    fd.close()

    if hash_ != sha1(data).hexdigest():
        raise Exception("Invalid hash.")

    # Remove path
    os.remove(key_path)

    # Update Authorized Keys
    update_authorized_keys()

    return username


def update_authorized_keys():

    home_path = os.environ['HOME']

    # Build gitolite section.
    gitolite_section = ['### Start Gitolite ###']

    # Gather keys.
    filenames = os.walk(os.path.join(home_path, '.gitomatic/keys')).next()[2]
    for filename in filenames:
        # Userbame and hash_key
        username, hash_key = filename.split(':')

        # Read Key
        fd = open(os.path.join(home_path, '.gitomatic/keys', filename))
        key = fd.read()
        fd.close()

        # Create entry
        cmd = '/usr/local/bin/gitomatic-auth %s' % (username, )
        gitolite_section.append(
            "command=\"%s\",no-port-forwarding,no-X11-forwarding,"\
            "no-agent-forwarding,no-pty %s" % (cmd, key))

    #  Gitolite final section
    gitolite_section.append('### End Gitolite ###')
    gitolite_section = "\n\n".join(gitolite_section)

    # Read authorized_keys
    try:
        fd = open(os.path.join(home_path, '.ssh', 'authorized_keys'))
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
    fd = open(os.path.join(home_path, '.ssh', 'authorized_keys'), 'w')
    os.fchmod(fd.fileno(), 0o600)
    fd.write(authorized_keys)
    fd.close()

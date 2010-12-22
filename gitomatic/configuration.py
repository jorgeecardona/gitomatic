import os
import configobj


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

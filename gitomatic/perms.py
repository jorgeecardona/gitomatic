import configuration


def add(username, repo, perm):
    # Add a permission.
    actual = configuration.read_permission(repo, username)
    new_perm = actual.union(set(perm))
    configuration.write_permission(repo, username, new_perm)
    return username


def remove(username, repo, perm):
    # Remove a permission.
    actual = configuration.read_permission(repo, username)
    new_perm = actual - set(perm)
    configuration.write_permission(repo, username, new_perm)

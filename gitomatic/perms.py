import configuration


def add(name, username, perm):
    # Add a permission.
    actual = configuration.read_permission(name, username)
    new_perm = actual.union(set(perm))
    configuration.write_permission(name, username, new_perm)


def remove(name, username, perm):
    # Remove a permission.
    actual = configuration.read_permission(name, username)
    new_perm = actual - set(perm)
    configuration.write_permission(name, username, new_perm)

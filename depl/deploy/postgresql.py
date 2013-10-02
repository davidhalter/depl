import textwrap

from fabric.api import sudo


def load(settings, package):
    for need in ['user', 'password', 'database']:
        if settings[need] is None:
            raise ValueError('You need to define a %s to deploy postgres.' % need)

    # create db must be separate (postgres security concern)
    create_db = "CREATE DATABASE {database};".format(**settings)

    create_user = textwrap.dedent("""
    CREATE USER {user} WITH PASSWORD '{password}';
    GRANT ALL PRIVILEGES ON DATABASE '{database}' to {user};
    """).format(**settings)

    def setup_user():
        sudo('service postgresql start')
        sudo('psql -c "%s"' % create_db.replace('"', r'\"'), user='postgres')
        sudo('psql -c "%s"' % create_user.replace('"', r'\"'), user='postgres')
    return ['postgresql'], [setup_user]

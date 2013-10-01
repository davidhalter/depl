import textwrap

from fabric.api import sudo


def load(settings, package):
    for need in ['user', 'password', 'database']:
        if settings[need] is None:
            raise ValueError('You need to define a %s to deploy postgres.' % need)

    sql = textwrap.dedent("""
    CREATE DATABASE {database};
    CREATE USER {user} WITH PASSWORD '{password}';
    GRANT ALL PRIVILEGES ON DATABASE '{database}' to {user};
    """).format(**settings)

    def setup_user():
        sudo('psql -c "%s"' % sql.replace('"', r'\"'), user='postgres')
    return ['postgresql'], [setup_user]

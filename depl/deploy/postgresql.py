"""
PostgreSQL is basically just driven by a database/user/password configuration.
Everything else (replication, ports, etc) is not available, yet. For most web
applications though, this is enough. You can also specify multiple databases.

.. sourcecode:: yaml

    deploy:
        - postgresql
            database: foobar
            user: foo
            password: baz
"""
import textwrap

from fabric.api import sudo

from . import Package


def deploy(settings):
    for need in ['user', 'password', 'database']:
        if settings[need] is None:
            raise ValueError('You need to define a %s to deploy postgres.' % need)

    # create db must be separate (postgres security concern)
    create_db = "CREATE DATABASE {database};".format(**settings)

    create_user = textwrap.dedent("""
    CREATE USER {user} WITH PASSWORD '{password}';
    GRANT ALL PRIVILEGES ON DATABASE {database} to {user};
    """).format(**settings)

    db_exists = "select datname from pg_catalog.pg_database where datname='%s'"
    user_exists = "select usename from pg_catalog.pg_user where usename='%s'"
    alter_password = "ALTER ROLE {user} WITH PASSWORD '{password}';"

    def setup_user():
        def psql_command(sql):
            return sudo('psql -c "%s"' % sql.replace('"', r'\"'), user='postgres')

        def no_result(sql):
            return '(0 rows)' in psql_command(sql)

        sudo('service postgresql start')
        if no_result(db_exists % settings['database']):
            psql_command(create_db)
        if no_result(user_exists % settings['user']):
            psql_command(create_user)
        else:
            psql_command(alter_password.format(**settings))
    return Package('postgresql'), setup_user

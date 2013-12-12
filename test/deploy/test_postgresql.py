import pytest

from fabric.api import local

from ..helpers import config_file, main_run
from depl.deploy import postgresql as pg
from depl.deploy import Package


def test_postgres_dependencies():
    pg_settings = {'user': None, 'database': 'db', 'password': 'pw'}
    with pytest.raises(ValueError):
        pg.deploy(pg_settings)

    pg_settings = {'user': 'user', 'database': 'db', 'password': 'pw'}
    commands = pg.deploy(pg_settings)
    assert Package('postgresql') in commands


def delete_pg_connection():
    local("""sudo -u postgres psql -c "DROP DATABASE depl;" """)
    local("""sudo -u postgres psql -c "DROP USER depl;" """)


@config_file('''
    deploy:
        - postgresql:
            database: depl
            user: depl
            password: depl
    ''')
def test_postgres(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
    # delete it again - this is the test (if it has been created)
    delete_pg_connection()

import pytest

from fabric.api import local as local

from test_main import config_file, main_run
from depl import deploy
from depl.deploy import postgresql as pg
from depl.deploy import Package


def test_postgres_dependencies():
    pg_settings = {'user': None, 'database': 'db', 'password': 'pw'}
    with pytest.raises(ValueError):
        pg.load(pg_settings, deploy._Package)

    pg_settings = {'user': 'user', 'database': 'db', 'password': 'pw'}
    dependencies, commands = pg.load(pg_settings, deploy._Package)
    assert dependencies == set([Package('postgresql')])
    assert len(commands) == 1


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

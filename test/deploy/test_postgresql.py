import pytest

import psycopg2

from depl import deploy
from depl.deploy import postgresql as pg
from test_main import config_file


def test_postgres_dependencies():
    pg_settings = {'user': None, 'database': 'db', 'password': 'pw'}
    with pytest.raises(ValueError):
        pg.load(pg_settings, deploy._Package)

    pg_settings = {'user': 'user', 'database': 'db', 'password': 'pw'}
    dependencies, commands = pg.load(pg_settings, deploy._Package)
    assert dependencies == ['postgresql']
    assert len(commands) == 1


def delete_pg_connection():
    conn = psycopg2.connect("dbname='depl' user='depl' host='localhost' password='depl'")
    cur = conn.cursor()
    cur.execute("""DROP USER depl; DROP OWNED BY depl""")
    cur.execute("""DROP DATABASE depl;""")


@config_file('''
    deploy:
        - postgresql:
            database: depl
            user: depl
            password: depl
    ''')
def test_postgres(tempdir):
    # delete it again - this is the test (if it has been created)
    delete_pg_connection()

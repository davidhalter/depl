import pytest

from depl import deploy
from depl.deploy import postgresql as pg


def test_postgres_dependencies():
    pg_settings = {'user': None, 'database': 'db', 'password': 'pw'}
    with pytest.raises(ValueError):
        pg.load(pg_settings, deploy._Package)

    pg_settings = {'user': 'user', 'database': 'db', 'password': 'pw'}
    dependencies, commands = pg.load(pg_settings, deploy._Package)
    assert dependencies == ['postgresql']
    assert len(commands) == 1

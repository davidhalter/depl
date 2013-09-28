from depl import deploy
from depl.deploy import postgresql as pg


def test_postgres_dependencies():
    pg_settings = {}
    dependencies, commands = pg.load(pg_settings, deploy._Package)
    assert dependencies == ['postgresql']
    assert commands == []

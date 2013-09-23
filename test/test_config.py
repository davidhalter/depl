import pytest

from depl import config


def test_not_existing(tmpdir):
    p = str(tmpdir.join("not_existing.yml"))
    with pytest.raises(IOError):
        config.Config(p, [])


def test_simple(tmpdir):
    p = tmpdir.join("default.yml")
    p.write("""
    deploy:
      - django
      - reddis
    """)

    config.Config(str(p), [])

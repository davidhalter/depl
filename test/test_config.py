import textwrap

import pytest

from depl import config


def validate(tmpdir, code, fail):
    p = tmpdir.join("default.yml")
    p.write(textwrap.dedent(code))
    if fail:
        with pytest.raises(config.ValidationError):
            config.Config(str(p), [])
    else:
        assert config.Config(str(p), [])


def test_not_existing(tmpdir):
    p = str(tmpdir.join("not_existing.yml"))
    with pytest.raises(IOError):
        config.Config(p, [])


def test_simple_valid(tmpdir):
    s = """
    deploy:
      - django
      - reddis
    """
    validate(tmpdir, s, 1)


def test_simple_invalid(tmpdir):
    s = """
    deploy:
      django
      reddis
    """
    validate(tmpdir, s, 1)

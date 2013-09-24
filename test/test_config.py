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
    validate(tmpdir, s, True)


def test_deploy_invalid(tmpdir):
    s = """
    deploy:
      django
      reddis
    """
    validate(tmpdir, s, True)

    s = """
    deploy:
      - django
      - reddis:
          not_existing_option: 3
    """
    validate(tmpdir, s, True)
    s = """
    deploy:
      - django:
        dict_in_the_wrong_place: 4
    """
    validate(tmpdir, s, True)
    s = """
    deploy:
      - not_existing_deploy_line
    """
    validate(tmpdir, s, True)


def test_deploy_valid(tmpdir):
    s = """
    deploy:
      - redis
    """
    validate(tmpdir, s, False)

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
        return config.Config(str(p), [])


def test_not_existing(tmpdir):
    p = str(tmpdir.join("not_existing.yml"))
    with pytest.raises(IOError):
        config.Config(p, [])


def test_deploy_invalid(tmpdir):
    s = """
    - deploy:
        django
    """
    validate(tmpdir, s, True)

    s = """
    deploy:
      django
      redis
    """
    validate(tmpdir, s, True)

    s = """
    deploy:
      - django
      - redis:
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
    s = """
    deploy:
      - django:
          port: string instead of int
    """
    validate(tmpdir, s, True)
    s = """
    deploy:
      - django:
          not_existing_django_config: 80
    """
    validate(tmpdir, s, True)


def test_deploy_valid(tmpdir):
    s = """
    deploy:
      - django
      - redis
    """
    validate(tmpdir, s, False)

    s = """
    deploy:
      - django:
          port: 80
      - redis
    """
    validate(tmpdir, s, False)

    s = """
    deploy:
      - redis
    """
    validate(tmpdir, s, False)


def test_server(tmpdir):
    def servers_to_str(yml):
        return [str(s) for s in validate(tmpdir, yml, False).servers()]
    s = """
    deploy:
      - django
    server:
      - foo@bar:22:
          password: password
    """
    assert servers_to_str(s) == ['foo@bar:22']
    s = """
    deploy:
      - django
    server:
      - foo@bar:22:
          password: password
      - example.com
    """
    assert servers_to_str(s) == ['foo@bar:22', 'example.com']


def test_server_invalid(tmpdir):
    s = """
    deploy:
      - django
    server:
      - foo@bar:
          password: password
          wrong_option: foo
    """
    validate(tmpdir, s, True)
    s = """
    deploy:
      - django
    server:
      server_not_in_list
    """
    validate(tmpdir, s, True)

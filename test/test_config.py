import textwrap

import pytest

from depl import config


def validate(tmpdir, code, fail=False, hosts=(), pool=None):
    p = tmpdir.join("default.yml")
    p.write(textwrap.dedent(code))
    if fail:
        with pytest.raises(config.ValidationError):
            config.Config(str(p), hosts, pool)
    else:
        return config.Config(str(p), hosts, pool)


def hosts_to_str(tmpdir, yml, hosts=()):
    return [s.identifier for s in validate(tmpdir, yml, False, hosts)._get_hosts()]

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
    def deploys_to_str(yml):
        return [s.name for s in validate(tmpdir, yml, False)._get_deploys()]

    s = """
    deploy:
      - django
      - redis
    """
    assert deploys_to_str(s) == ['django', 'redis']

    s = """
    deploy:
      - django:
          port: 80
      - redis
    """
    assert deploys_to_str(s) == ['django', 'redis']
    validate(tmpdir, s, False)

    s = """
    deploy:
      - redis
    """
    assert deploys_to_str(s) == ['redis']


def test_hosts(tmpdir):
    s = """
    deploy:
      - django
    hosts:
      - foo@bar:22:
          password: password
    """
    assert hosts_to_str(tmpdir, s) == ['foo@bar:22']
    s = """
    deploy:
      - django
    hosts:
      - foo@bar:22:
          password: pwd
      - example.com
    """
    assert hosts_to_str(tmpdir, s) == ['foo@bar:22', 'example.com']
    assert list(validate(tmpdir, s)._get_hosts())[0].password == 'pwd'


def test_hosts_invalid(tmpdir):
    s = """
    deploy:
      - django
    hosts:
      - foo@bar:
          password: password
          wrong_option: foo
    """
    validate(tmpdir, s, True)
    s = """
    deploy:
      - django
    hosts:
      host_not_in_list
    """
    validate(tmpdir, s, True)


def test_pool(tmpdir):
    s = """
    deploy:
      - django
      - redis
    hosts:
      - foo@bar
      - other
    pool:
      foo:
        hosts: [foo@bar]
        deploy: [django]
    """
    pools = validate(tmpdir, s, False).pools()
    assert len(pools) == 1

    hosts = pools[0].hosts
    assert len(hosts) == 1
    assert hosts[0].identifier == 'foo@bar'
    deploys = pools[0].deploys
    assert len(deploys) == 1
    assert deploys[0].name == 'django'


def test_pool_invalid(tmpdir):
    s = """
    deploy:
      - django
    hosts:
      - foo@bar
    pool:
      foo:
        hosts: [foo@bar]
        deploy: [django]
        unknown_option: haha
    """
    validate(tmpdir, s, True)


def test_hosts_param(tmpdir):
    s = """
    deploy:
      - django
    """
    assert hosts_to_str(tmpdir, s, ['foo@bar']) == ['foo@bar']
    s = """
    deploy:
      - django
    hosts:
      - foo@baz
    """
    assert hosts_to_str(tmpdir, s, ['foo@bar']) == ['foo@bar']


def test_pool_param(tmpdir):
    s = """
    deploy:
      - django
      - redis
    hosts:
      - foo@bar
      - other
    pool:
      foo:
        hosts: [foo@bar]
        deploy: [django]
      bar:
        hosts: [foo@bar]
        deploy: [redis]
    """
    assert len(validate(tmpdir, s).pools()) == 2
    assert len(validate(tmpdir, s, pool='foo').pools()) == 1
    with pytest.raises(KeyError):
        validate(tmpdir, s, pool='not_existing').pools()


def test_pool_hosts_param(tmpdir):
    s = """
    deploy:
      - django
      - redis
    hosts:
      - foo@bar
      - other
    pool:
      foo:
        hosts: [foo@bar]
        deploy: [django]
      bar:
        hosts: [foo@bar]
        deploy: [redis]
    """
    assert len(validate(tmpdir, s).pools()) == 2
    pool = validate(tmpdir, s, hosts=['baz'], pool='foo').pools()[0]
    assert pool.name == 'foo'
    assert [s.identifier for s in pool.hosts] == ['baz']


def test_hosts_param_with_pool(tmpdir):
    """
    No pool param but a host param with pools, should only run on "known" SSH
    hosts!
    """
    s = """
    deploy:
      - django
      - redis
    hosts:
      - first
      - second
      - third:
          password: something
      - other
    pool:
      foo:
        hosts: [first]
        deploy: [django]
      bar:
        hosts: [first, second]
        deploy: [redis]
      baz:
        hosts: [third]
        deploy: [redis]
    """
    # other is not being used in pools
    pools = validate(tmpdir, s, hosts=['other']).pools()
    for pool in pools:
        assert pool.hosts == []

    # foo@bar is being used in foo/bar
    for pool in validate(tmpdir, s, hosts=['first']).pools():
        if pool.name == 'baz':
            assert pool.hosts == []
        else:
            assert [svr.identifier for svr in pool.hosts] == ['first']

    # third has other settings
    for pool in validate(tmpdir, s, hosts=['third']).pools():
        if pool.name == 'baz':
            assert [svr.identifier for svr in pool.hosts] == ['third']
            assert [svr.password for svr in pool.hosts] == ['something']
        else:
            assert pool.hosts == []

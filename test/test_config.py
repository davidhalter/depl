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


def servers_to_str(tmpdir, yml, hosts=()):
    return [s.identifier for s in validate(tmpdir, yml, False, hosts)._servers()]

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
        return [s.name for s in validate(tmpdir, yml, False)._deploys()]

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


def test_server(tmpdir):
    s = """
    deploy:
      - django
    server:
      - foo@bar:22:
          password: password
    """
    assert servers_to_str(tmpdir, s) == ['foo@bar:22']
    s = """
    deploy:
      - django
    server:
      - foo@bar:22:
          password: pwd
      - example.com
    """
    assert servers_to_str(tmpdir, s) == ['foo@bar:22', 'example.com']
    assert list(validate(tmpdir, s)._servers())[0].password == 'pwd'


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


def test_pool(tmpdir):
    s = """
    deploy:
      - django
      - redis
    server:
      - foo@bar
      - other
    pool:
      foo:
        server: [foo@bar]
        deploy: [django]
    """
    pools = validate(tmpdir, s, False).pools()
    assert len(pools) == 1

    servers = pools[0].servers
    assert len(servers) == 1
    assert servers[0].identifier == 'foo@bar'
    deploys = pools[0].deploys
    assert len(deploys) == 1
    assert deploys[0].name == 'django'


def test_pool_invalid(tmpdir):
    s = """
    deploy:
      - &web django
    server:
      - &server1 foo@bar
    pool:
      foo:
        server: [*server1]
        deploy: [*web]
        unknown_option: haha
    """
    validate(tmpdir, s, True)


def test_hosts_param(tmpdir):
    s = """
    deploy:
      - &web django
    """
    assert servers_to_str(tmpdir, s, ['foo@bar']) == ['foo@bar']
    s = """
    deploy:
      - &web django
    server:
      - foo@baz
    """
    assert servers_to_str(tmpdir, s, ['foo@bar']) == ['foo@bar']


def test_pool_param(tmpdir):
    s = """
    deploy:
      - &web django
      - &redis redis
    server:
      - &server1 foo@bar
      - other
    pool:
      foo:
        server: [*server1]
        deploy: [*web]
      bar:
        server: [*server1]
        deploy: [*redis]
    """
    assert len(validate(tmpdir, s).pools()) == 2
    assert len(validate(tmpdir, s, pool='foo').pools()) == 1
    with pytest.raises(KeyError):
        validate(tmpdir, s, pool='not_existing').pools()


def test_pool_hosts_param(tmpdir):
    s = """
    deploy:
      - &web django
      - &redis redis
    server:
      - &server1 foo@bar
      - other
    pool:
      foo:
        server: [*server1]
        deploy: [*web]
      bar:
        server: [*server1]
        deploy: [*redis]
    """
    assert len(validate(tmpdir, s).pools()) == 2
    pool = validate(tmpdir, s, hosts=['baz'], pool='foo').pools()[0]
    assert pool.name == 'foo'
    assert [s.identifier for s in pool.servers] == ['baz']


def test_hosts_param_with_pool(tmpdir):
    """
    No pool param but a host param with pools, should only run on "known" SSH
    hosts!
    """
    s = """
    deploy:
      - &web django
      - &redis redis
    server:
      - &server1 foo@bar
      - &server2 second
      - &server3 third:
          password: something
      - other
    pool:
      foo:
        server: [*server1]
        deploy: [*web]
      bar:
        server: [*server1, *server2]
        deploy: [*redis]
      baz:
        server: [*server3]
        deploy: [*redis]
    """
    # other is not being used in pools
    pools = validate(tmpdir, s, hosts=['other']).pools()
    for pool in pools:
        assert pool.servers == []

    # foo@bar is being used in foo/bar
    for pool in validate(tmpdir, s, hosts=['foo@bar']).pools():
        if pool.name == 'baz':
            assert pool.servers == []
        else:
            assert [svr.identifier for svr in pool.servers] == ['foo@bar']

    # third has other settings
    import yaml
    print yaml.load(s)
    for pool in validate(tmpdir, s, hosts=['third']).pools():
        if pool.name == 'baz':
            assert [svr.identifier for svr in pool.servers] == ['third']
            assert [svr.password for svr in pool.servers] == ['something']
        else:
            assert pool.servers == []

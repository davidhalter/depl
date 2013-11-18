import textwrap

import pytest

from depl import config


def validate(tmpdir, code, fail=False, hosts=(), pool=None,
             file_name="default.yml"):
    p = tmpdir.join(file_name)
    p.write(textwrap.dedent(code))

    # set recursion paths
    config._recursion_paths = []
    if fail:
        with pytest.raises(config.ValidationError):
            config.Config(str(p), hosts, pool)
    else:
        return config.Config(str(p), hosts, pool)


def hosts_to_str(tmpdir, yml, hosts=()):
    pools = validate(tmpdir, yml, False, hosts).pools
    assert len(pools) == 1
    return [s.identifier for s in pools[0].hosts]


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
    def deploy_to_str(yml):
        pools = validate(tmpdir, yml, False).pools
        assert len(pools) == 1
        return [s.name for s in pools[0].deploy]

    s = """
    deploy:
      - django
      - redis
    """
    assert deploy_to_str(s) == ['django', 'redis']
    deploy = validate(tmpdir, s, False).pools[0].deploy[0]
    assert deploy.settings['port'] == 80

    s = """
    deploy:
      - django:
          port: 81
      - redis
    """
    assert deploy_to_str(s) == ['django', 'redis']
    deploy = validate(tmpdir, s, False).pools[0].deploy[0]
    assert deploy.settings['port'] == 81
    assert deploy.settings['url'] == 'localhost'

    s = """
    deploy:
      - redis
    """
    assert deploy_to_str(s) == ['redis']


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
    assert list(validate(tmpdir, s).pools[0].hosts)[0].password == 'pwd'


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
    pools:
      - foo:
          hosts: [foo@bar]
          deploy: [django]
    """
    pools = validate(tmpdir, s, False).pools
    assert len(pools) == 1

    hosts = pools[0].hosts
    assert len(hosts) == 1
    assert hosts[0].identifier == 'foo@bar'
    deploy = pools[0].deploy
    assert len(deploy) == 1
    assert deploy[0].name == 'django'


def test_pool_invalid(tmpdir):
    s = """
    deploy:
      - django
    hosts:
      - foo@bar
    pools:
      - foo:
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
    pools:
      - foo:
          hosts: [foo@bar]
          deploy: [django]
      - bar:
          hosts: [foo@bar]
          deploy: [redis]
    """
    assert len(validate(tmpdir, s).pools) == 2
    assert len(validate(tmpdir, s, pool='foo').pools) == 1
    with pytest.raises(KeyError):
        validate(tmpdir, s, pool='not_existing').pools


def test_pool_hosts_param(tmpdir):
    s = """
    deploy:
      - django
      - redis
    hosts:
      - foo@bar
      - other
    pools:
      - foo:
          hosts: [foo@bar]
          deploy: [django]
      - bar:
          hosts: [foo@bar]
          deploy: [redis]
    """
    assert len(validate(tmpdir, s).pools) == 2
    pool = validate(tmpdir, s, hosts=['baz'], pool='foo').pools[0]
    assert pool.id == 'foo'
    assert [h.identifier for h in pool.hosts] == ['baz']


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
    pools:
      - foo:
          hosts: [first]
          deploy: [django]
      - bar:
          hosts: [first, second]
          deploy: [redis]
      - baz:
          hosts: [third]
          deploy: [redis]
    """
    # other is not being used in pools
    pools = validate(tmpdir, s, hosts=['other']).pools
    for pool in pools:
        assert pool.hosts == []

    # foo@bar is being used in foo/bar
    for pool in validate(tmpdir, s, hosts=['first']).pools:
        if pool.id == 'baz':
            assert pool.hosts == []
        else:
            assert [host.identifier for host in pool.hosts] == ['first']

    # third has other settings
    for pool in validate(tmpdir, s, hosts=['third']).pools:
        if pool.id == 'baz':
            assert [host.identifier for host in pool.hosts] == ['third']
            assert [host.password for host in pool.hosts] == ['something']
        else:
            assert pool.hosts == []


def test_extends_simple(tmpdir):
    # -> multi inheritance
    s1 = """
    deploy:
      - django
    """

    s2 = """
    deploy:
      - redis
    """

    s3 = """
    deploy:
      - postgresql

    extends:
      - extend1.yml
      - extend2.yml
    """
    # create first/second file
    validate(tmpdir, s1, hosts=['other'], file_name='extend1.yml')
    validate(tmpdir, s2, hosts=['other'], file_name='extend2.yml')

    # create third
    pools = validate(tmpdir, s3, hosts=['other']).pools
    assert len(pools) == 1
    assert [p.name for p in pools[0].deploy] == ['django', 'redis', 'postgresql']

    # -> simple inheritance
    s2 = """
    deploy:
      - redis

    extends:
      - extend1.yml
    """

    s3 = """
    deploy:
      - postgresql

    extends:
      - extend2.yml
    """

    # create third
    validate(tmpdir, s2, hosts=['other'], file_name='extend2.yml')
    pools = validate(tmpdir, s3, hosts=['other']).pools
    assert len(pools) == 1
    assert [p.name for p in pools[0].deploy] == ['django', 'redis', 'postgresql']


def test_extends(tmpdir):
    s1 = """
    deploy:
      - django:
          id: django1
    hosts:
      - first:
          password: "shouldn't appear"
      - second
    pools:
        - foo:
            hosts: [first]
            deploy: [django1]
        - bar:
            hosts: [second]
            deploy: [django1]
    """

    s2 = """
    deploy:
      - django:
          id: django2
      - redis
    hosts:
      - first:
          password: "should appear"
    pools:
      - bar:
          hosts: [second]
          deploy: [django2]
    extends:
      - extend.yml
    """
    # create first file
    validate(tmpdir, s1, file_name='extend.yml')

    pools = validate(tmpdir, s2, hosts=['other']).pools
    assert len(pools) == 2
    assert not pools[0].hosts and not pools[0].hosts
    # create second
    pools = validate(tmpdir, s2).pools
    assert len(pools) == 2

    for pool in pools:
        if pool.id == 'foo':
            assert [host.identifier for host in pool.hosts] == ['first']
            assert [host.password for host in pool.hosts] == ['should appear']
        else:
            assert [host.identifier for host in pool.hosts] == ['second']
            assert [host.password for host in pool.hosts] == [None]


def test_extends_recursion(tmpdir):
    s1 = """
    deploy:
      - django

    extends:
      - extend1.yml
    """
    with pytest.raises(RuntimeError) as excinfo:
        validate(tmpdir, s1, file_name='extend1.yml')
    assert excinfo.value.message == 'Recursion in depl files.'


def test_dictionary_in_dictionary(tmpdir):
    """Dictionary should be filled with values from grammar file."""
    s = """
    deploy:
      - django:
          port: 80
          ssl:
            port: 444
    """
    settings = validate(tmpdir, s).pools[0].deploy[0].settings
    assert settings['ssl']['port'] == 444
    assert settings['ssl']['key'] is None

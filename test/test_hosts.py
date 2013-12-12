from depl import config
from depl import hosts


def test_run(tmpdir):
    pool = config.Pool(None, [config.Host('localhost')],
                             [config.Deploy('redis', {'id': 'redis'})])

    hosts.run_in_pool(pool, ['ls'])


def test_deploy(monkeypatch):
    def mockreturn(pool, commands):
        commands = list(commands)
        assert len(commands) >= 1
    monkeypatch.setattr(hosts, 'run_in_pool', mockreturn)

    pool = config.Pool(None, [config.Host('localhost')],
                             [config.Deploy('redis', {'id': 'redis'})])
    hosts.execute_pool(pool, 'deploy')

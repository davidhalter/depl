from fabric.api import settings
from fabric import tasks

from depl import deploy

host = 'localhost'


def test_package_manager_stuff():
    with settings(hosts=[host]):
        result = tasks.execute(deploy.package_manager.system)
        assert result[host] in ['apt', 'yum', 'pacman']

        result = tasks.execute(deploy.package_manager._manager)
        assert result[host] in ['apt-get', 'yum', 'pacman']

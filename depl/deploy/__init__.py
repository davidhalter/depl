"""
Deploys have the same name as in ``grammar.yml``, are stored as python modules
in the ``deploy`` package. These need to contain a ``load()`` function that
returns a list of commands - either python functions (remember to use fabric!)
- or strings that need to be executed, as well as a list of dependencies.

Dependencies are stored in a ``dependencies.yml`` file. You easily change the
packages for your package manager.
"""

import os
from datetime import datetime

import yaml
from fabric.api import settings, run, sudo, warn_only


def load(name, settings):
    module = __import__('depl.deploy.' + name, globals(), locals(), [name], -1)
    module_dependencies, commands = module.load(settings, package_manager.system())

    def install_dependencies():
        package_manager.run_update()
        for dep in module_dependencies:
            dep_name = dependencies[dep][package_manager.system()]
            sudo(package_manager.install_str().format(dep_name))
    yield install_dependencies
    for cmd in commands:
        yield cmd


class _PackageRepository(object):
    def __init__(self, uri, public_key=None):
        self.uri = uri

    def enable(self):
        pass


class AptPackageRepository(_PackageRepository):
    system = 'apt'

    def enable(self):
        package_manager.install('software-properties-common')
        sudo('add-apt-repository -y ' + self.url)
        sudo('apt-get update ' + self.url)


class Package(object):
    def __init__(self, package_names, repos=()):
        self.package_name = package_names
        self.repos = repos

    def install(self):
        for repo in self.repos:
            if repo.system == package_manager.system():
                repo.enable()

        dep_string = dependencies[self.package_name][package_manager.system()]
        package_manager.install(dep_string)


class _PackageManager(object):
    """Lookup the package manager lazily"""
    MANAGERS = ['apt-get', 'pacman', 'yum']

    def __init__(self):
        self._manager = None

    def _install_str(self):
        man = self._manager()
        if man == 'pacman':
            install = ' -S {0}'
        elif man == 'yum':
            install = ' install {0}'
        elif man == 'apt-get':
            # dpkg checks first if it's already installed
            # -q -> quiet, always say yes (-y) - no prompts!
            return 'dpkg -s {0} 2>/dev/null >/dev/null || ' + man + ' -q install -y {0}'
        return man + install

    def install(self, package_str):
        sudo(self.install_str().format(package_str))

    def system(self):
        return 'apt' if self._manager() == 'apt-get' else self._manager()

    def _manager(self):
        if self._manager:
            return self._manager
        for name in self.MANAGERS:
            with settings(warn_only=True):
                # Everything must be run with fabric - otherwise detection is
                # not possible.
                result = run('which ' + name)
                if result.return_code == 0:
                    break
        else:
            raise NotImplementedError("Didn't find a package manager for your OS.")
        self._manager = name
        return name

    def run_update(self):
        if self.system() == 'apt':
            with warn_only():
                timestamp = run('stat -c %Y /var/lib/apt/periodic/update-success-stamp')
                if timestamp.succeeded:
                    date = datetime.fromtimestamp(int(timestamp))
            if timestamp.failed or (datetime.now() - date).days > 1:
                # update unless the package info is older
                sudo('apt-get -q update')
        else:
            raise NotImplementedError()


with open(os.path.join(os.path.dirname(__file__), 'dependencies.yml')) as f:
    dependencies = yaml.load(f)

package_manager = _PackageManager()

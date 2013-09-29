"""
Deploys have the same name as in ``grammar.yml``, are stored as python modules
in the ``deploy`` package. These need to contain a ``load()`` function that
returns a list of commands - either python functions (remember to use fabric!)
- or strings that need to be executed, as well as a list of dependencies.

Dependencies are stored in a ``dependencies.yml`` file. You easily change the
packages for your package manager.
"""

import os

import yaml
from fabric.api import settings, run


def load(name, settings):
    module = __import__('depl.deploy.' + name, globals(), locals(), [name], -1)
    module_dependencies, commands = module.load(settings, _Package.system())

    for dep in module_dependencies:
        dep_name = dependencies[dep][_Package.system()]
        yield 'sudo %s %s' % (_Package.install(), dep_name)
    for cmd in commands:
        yield cmd


class _Package(object):
    """Lookup the package manager lazily"""
    MANAGERS = ['apt-get', 'pacman', 'yum']
    def __init__(self):
        self._manager = None

    def install(self):
        install = ' install' if self.manager() != 'pacman' else ' -S'
        return self.manager() + install

    def system(self):
        return 'apt' if self.manager() == 'apt-get' else self.manager()

    def manager(self):
        if self._manager:
            return self._manager
        for name in self.MANAGERS:
            with settings(warn_only=True):
                # Everything must be run with fabric - otherwise detection is not
                # possible.
                result = run('which ' + name)
                if result.return_code == 0:
                    break
        else:
            raise NotImplementedError("Didn't find a package manager for your OS.")
        self._manager = name
        return name


_Package = _Package()

with open(os.path.join(os.path.dirname(__file__), 'dependencies.yml')) as f:
    dependencies = yaml.load(f)

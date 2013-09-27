"""
Deploys have the same name as in ``grammar.yml``, are stored as python modules
in the ``deploy`` package. These need to contain a ``load()`` function that
returns a list of commands - either python functions (remember to use fabric!)
- or strings that need to be executed, as well as a list of dependencies.

Dependencies are stored in a ``dependencies.yml`` file. You easily change the
packages for your package manager.
"""

import os
from distutils.spawn import find_executable

import yaml


def load(name, settings):
    module = __import__('depl.deploy', globals(), locals(), [name], -1)
    commands, module_dependencies = module.load(settings, package_manager)

    for dep in module_dependencies:
        yield 'sudo %s %s' % (pkg_install, _dependency_lookup(dep))
    for cmd in commands:
        yield cmd

def _dependency_lookup(name):
    return dependencies[name]['apt' if name == 'apt-get' else name]

def _get_package_manager():
    for name in ['apt-get', 'pacman', 'yum']:
        if find_executable(name) is not None:
            break
    else:
        raise NotImplementedError("Didn't find a package manager for your OS.")
    install = ' install' if name != 'pacman' else ' -S'
    return name, name + install


with open(os.path.join(os.path.dirname(__file__), 'dependencies.yml')) as f:
    dependencies = yaml.load(f)

package_manager, pkg_install = _get_package_manager()

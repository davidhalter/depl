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
        yield dep
    for cmd in commands:
        yield cmd


def get_package_manager():
    result = None
    for name in ['apt-get', 'pacman', 'yum']:
        if find_executable(name) is not None:
            result = name
            break
    if result is None:
        raise NotImplementedError("Didn't find a package manager for your OS.")
    return result


with open(os.path.join(os.path.dirname(__file__), 'dependencies.yml')) as f:
    dependencies = yaml.load(f)

package_manager = get_package_manager()

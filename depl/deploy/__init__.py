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
from fabric.context_managers import quiet

from depl import helpers


def load(name, settings):
    """Returns an iterable of commands to execute - basically callbacks."""
    module = __import__('depl.deploy.' + name, globals(), locals(), [name], -1)
    module_dependencies, commands = module.load(settings)
    return [package_manager.run_update] + list(module_dependencies) + commands


def _apt_add_repo(repo, pgp=None, no_deb_src=False):
    APT_PATH = '/etc/apt/sources.list'
    package_manager.install('software-properties-common')
    sudo('add-apt-repository -y "%s"' % repo)
    if no_deb_src:
        # annoying case of mongodb, doesn't work with deb-src, so remove it.
        src_repo = 'deb-src' + repo[3:]
        txt = helpers.read_file(APT_PATH)
        lines = txt.splitlines()
        try:
            del lines[lines.index(src_repo)]
        except ValueError:
            pass
        else:
            txt = '\n'.join(lines)
            helpers.write_file(txt, APT_PATH, True)

    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv %s' % pgp)
    sudo('apt-get -q update')


class Package(object):
    """
    Represents a depl package - see ``deploy/dependencies.yml``.
    Possible to install the package with ``self.__call__``.
    """
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __call__(self):
        """installation call"""
        dep_string = dependencies[self.name][package_manager.system()]
        if isinstance(dep_string, dict):
            repo = dep_string['repo']
            pgp = dep_string.get('pgp')
            if package_manager.system() == 'apt':
                _apt_add_repo(repo, pgp, dep_string.get('no-deb-src', False))
            else:
                raise NotImplementedError()
            dep_string = dep_string['name']

        package_manager.install(dep_string)


class _PackageManager(object):
    """Lookup the package manager lazily"""
    MANAGERS = ['apt-get', 'pacman', 'yum']

    def __init__(self):
        self.__manager = None

    def install(self, package_str):
        man = self._manager()
        if man == 'pacman':
            sudo(man + ' -S {0}'.format(package_str))
        elif man == 'yum':
            sudo(man + ' install {0}'.format(package_str))
        elif man == 'apt-get':
            install = False
            with quiet():
                # Improve the speed by asking dpkg first if package exists
                # already.
                output = sudo('dpkg -s {0}'.format(package_str))
                # sometimes a project is deinstalled - also check that.
                if output.failed or 'Status: deinstall' in output:
                    install = True
            if install:
                # -q -> quiet, always say yes (-y) - no prompts!
                sudo(man + ' -q install -y {0}'.format(package_str))

    def system(self):
        return 'apt' if self._manager() == 'apt-get' else self._manager()

    def _manager(self):
        if self.__manager:
            return self.__manager
        for name in self.MANAGERS:
            with settings(warn_only=True):
                # Everything must be run with fabric - otherwise detection is
                # not possible.
                result = run('which ' + name)
                if result.return_code == 0:
                    break
        else:
            raise NotImplementedError("Didn't find a package manager for your OS.")
        self.__manager = name
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

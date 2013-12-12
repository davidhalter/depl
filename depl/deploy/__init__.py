"""
Deploys have the same name as in ``grammar.yml``, are stored as python modules
in the ``deploy`` package. These need to contain a ``deploy()`` function that
returns a list of commands - either python functions (remember to use fabric!)
- or strings that need to be executed, as well as a list of dependencies.

Dependencies are stored in a ``dependencies.yml`` file. You easily change the
packages for your package manager.
"""

import os
import re
from datetime import datetime

import yaml
from fabric.api import settings, run, sudo, warn_only
from fabric.context_managers import quiet, hide

from depl import helpers


def load_commands(name, settings, action='deploy'):
    """Returns an iterable of commands to execute - basically callbacks."""
    def install_packages():
        # only working for apt
        with hide('stdout'):
            # Need a new line after sources.list, which sometimes doesn't end
            # with one, easiest option: awk.
            apt_txt = run('awk \'FNR==1{print ""}1\' '
                          '/etc/apt/sources.list /etc/apt/sources.list.d/*')

        force_update = False
        for package in packages:
            if package.needs_additional_repo(apt_txt):
                package.install_additional_repo()
                force_update = True

        package_manager.run_update(force_update)

        for package in packages:
            package.install()

    module = __import__('depl.deploy.' + name, globals(), locals(), [name], -1)
    commands = getattr(module, action)(settings)
    packages = set([p for p in commands if isinstance(p, Package)])
    commands = tuple([p for p in commands if not isinstance(p, Package)])

    return (install_packages,) + commands


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

    if pgp is not None:
        sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv %s' % pgp)


class Package(object):
    """
    Represents a depl package - see ``deploy/dependencies.yml``.
    Possible to install the package with ``self.__call__``.
    """
    def __init__(self, name):
        self.name = name

        self._dep_string = dependencies[self.name][package_manager.system()]
        self._properties = {}
        if isinstance(self._dep_string, dict):
            self._properties = self._dep_string
            self._dep_string = self._dep_string['name']

    def __eq__(self, other):
        return isinstance(other, Package) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def needs_additional_repo(self, sources_txt):
        if 'repo' not in self._properties:
            return False

        # only working for apt
        repo_search = self._properties['repo']
        if repo_search.startswith('ppa:'):
            repo_search = 'deb http://ppa.launchpad.net/' + repo_search[4:]
        repo_search = re.escape(repo_search)
        return re.search('^%s' % repo_search, sources_txt, re.MULTILINE) is None

    def install_additional_repo(self):
        if package_manager.system() == 'apt':
            p = self._properties
            _apt_add_repo(p['repo'], p.get('pgp'), p.get('no-deb-src', False))
        else:
            raise NotImplementedError()

    def install(self):
        package_manager.install(self._dep_string)


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

    def run_update(self, force=False):
        if self.system() == 'apt':
            if not force:
                with warn_only():
                    timestamp = run('stat -c %Y /var/lib/apt/periodic/update-success-stamp')
                    if timestamp.succeeded:
                        date = datetime.fromtimestamp(int(timestamp))
            if force or timestamp.failed or (datetime.now() - date).days > 1:
                # update unless the package info is older
                sudo('apt-get -q update > /dev/null')
        else:
            raise NotImplementedError()


with open(os.path.join(os.path.dirname(__file__), 'dependencies.yml')) as f:
    dependencies = yaml.load(f)

package_manager = _PackageManager()

from fabric.api import sudo

from . import Package
from . import mongodb

APT_REPO = \
    "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"


def load(settings):
    def install():
        sudo('curl https://install.meteor.com | /bin/sh')

    dependencies, commands = mongodb.load(settings)
    return dependencies | set([Package('nodejs')]), commands + [install]

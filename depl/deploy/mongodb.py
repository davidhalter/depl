"""
MongoDB is very easy to setup - but there remains one glitch, by default the
mongodb port 27017 is open. Maybe add ``bind_ip = 127.0.0.1`` to
``/etc/mongodb.conf``?
"""
from fabric.api import sudo

from . import Package

APT_REPO = \
    "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"


def load(settings):
    def start():
        # Start the service - e.g. it's stopped on travis by default.
        sudo('/etc/init.d/mongodb start')

    return set([Package('mongodb')]), [start]

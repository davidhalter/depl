"""
MongoDB is very easy to setup - but there remains one glitch, by default the
mongodb port 27017 is open. Maybe add ``bind_ip = 127.0.0.1`` to
``/etc/mongodb.conf``?
"""
from . import Package

APT_REPO = \
    "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"


def load(settings):
    return set([Package('mongodb')]), []

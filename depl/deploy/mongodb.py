"""
MongoDB is very easy to setup. There are no configuration options, just mention
it:

.. sourcecode:: yaml

    deploy:
        - mongodb

There remains one glitch, by default the mongodb port 27017 is open. Maybe add
``bind_ip = 127.0.0.1`` to ``/etc/mongodb.conf``? I have no idea how insecure
it is, but it seems to be an open door.
"""
from fabric.api import sudo

from . import Package


def deploy(settings):
    def start():
        # Start the service - e.g. it's stopped on travis by default.
        sudo('/etc/init.d/mongodb start')

    return Package('mongodb'), Package('curl'), start

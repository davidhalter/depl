"""
Redis has no configuration options (yet), use it like this:

.. sourcecode:: yaml

    deploy:
        - redis
"""
from . import Package


def deploy(settings):
    # redis dependency, no commands
    return Package('redis'),

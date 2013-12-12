from . import Package


def deploy(settings):
    # redis dependency, no commands
    return Package('redis'),

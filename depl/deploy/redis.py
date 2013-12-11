from . import Package


def load(settings):
    # redis dependency, no commands
    return Package('redis'),

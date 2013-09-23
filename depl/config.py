import yaml

class Config(object):
    def __init__(self, path, hosts):
        with open(path) as f:
            content = f.read()
        self.cnf = yaml.load(content)

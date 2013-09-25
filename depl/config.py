import os

import yaml


class ValidationError(Exception):
    pass


class Config(object):
    def __init__(self, path, hosts=(), pool=None):
        self._hosts_option = hosts
        self._pool_option = pool

        with open(path) as f:
            content = f.read()
        self._cnf = yaml.load(content)
        self._deploy = []
        self._server = []

        self._validate()

    def _validate(self):
        if not isinstance(self._cnf, dict):
            raise ValidationError('Should be a dict')

        with open(os.path.join(os.path.dirname(__file__), 'grammar.yml')) as f:
            grammar = yaml.load(f)
        for key, value in self._cnf.items():
            if key not in grammar:
                raise ValidationError('"%s" is an unkown configuration option'
                                        % key)

            setattr(self, '_' + key, self._validate_detail(value, grammar[key]))

    def _validate_detail(self, current, grammar):
        result = current
        if isinstance(current, list):
            if not isinstance(grammar, list):
                raise ValidationError("Didn't expect a list in %s" % current)

            list_dict = {}
            for item in grammar:
                if isinstance(item, dict):
                    key, value = item.items()[0]
                    list_dict[key] = value
                else:
                    key = item
                    list_dict[item] = None

            result = []
            is_playeholder = len(list_dict) == 1 \
                             and key[0] == '<' and key[-1] == '>'
            # <something> denotes a placeholder (anything)

            for element in current:
                if isinstance(element, dict):
                    if len(element) != 1:
                        raise ValidationError('Dictionary directly in list, %s'
                                              % element)
                    key, value = element.items()[0]
                    if key not in list_dict and not is_playeholder:
                        raise ValidationError('Key %s not found in grammar'
                                              % key)
                    gram = list_dict.values()[0] if is_playeholder \
                            else list_dict[key]
                    el = self._validate_detail(value, gram)
                    result.append((key, el))
                elif isinstance(element, list):
                    raise ValidationError('List not expected in list %s' % element)
                else:
                    if element not in list_dict and not is_playeholder:
                        raise ValidationError('Element %s not found in grammar (%s)'
                                              % (element, list_dict))
                    result.append(element)
        elif isinstance(current, dict):
            if not isinstance(grammar, dict):
                raise ValidationError("Expected a dictionary in %s" % current)

            is_playeholder = len(grammar) == 1 and grammar.keys()[0][0] == '<' \
                             and grammar.keys()[0][-1] == '>'
            result = {}
            for key, value in current.items():
                if key not in grammar and not is_playeholder:
                    raise ValidationError("Key %s is not in grammar." % key)

                gram = grammar.values()[0] if is_playeholder else grammar[key]
                result[key] = self._validate_detail(value, gram)
        else:
            # normal type
            if type(grammar) != type(current):
                if grammar is None:
                    result = str(current)
                else:
                    raise ValidationError("Grammar type doesn't match - %s with %s"
                                          % (grammar, current))
        return result

    def _servers(self):
        for server in self._hosts_option or self._server:
            if self._hosts_option:
                for s in self._server:
                    if isinstance(s, tuple) and s[0] == server:
                        # Overwrite the host option with all the server
                        # settings, if they have the same host string.
                        server = s
            if isinstance(server, tuple):
                yield Server(*server)
            else:
                yield Server(server)

    def _deploys(self):
        for deploy in self._deploy:
            if isinstance(deploy, tuple):
                yield Deploy(*deploy)
            else:
                yield Deploy(deploy)

    def pools(self):
        servers = list(self._servers())
        deploys = list(self._deploys())
        def get_ids(ids, objects, is_server=False):
            for obj in objects:
                for id in ids:
                    if obj.id == id or is_server and self._pool_option and self._hosts_option:
                        yield obj
                if not ids:
                    yield obj

        result = []
        for name, pool in self._pool.items():
            if self._pool_option not in (name, None):
                continue
            result.append(Pool(name, get_ids(pool['server'], servers, True),
                                     get_ids(pool['deploy'], deploys)))
        if self._pool_option and not result:
            raise KeyError("Didn't find the pool '%s'." % self._pool_option)
        if not self._pool:
            # Create a default pool, if there's none.
            result.append(Pool(None, self._servers(), self._deploys()))
        return result


class Server(object):
    def __init__(self, identifier, settings={}):
        self.identifier = identifier
        self.password = settings.get('password', None)
        self.id = settings.get('id', identifier)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.identifier)


class Deploy(object):
    def __init__(self, name, settings=None):
        self.name = name
        self.settings = settings or {}
        self.id = self.settings.get('id', name)


class Pool(object):
    def __init__(self, name, servers, deploys):
        self.name = name
        self.servers = list(servers)
        self.deploys = list(deploys)

import os

import yaml


class ValidationError(Exception):
    pass


class Config(object):
    def __init__(self, path, hosts=(), pool=None):
        self._hosts_option = hosts
        self._pool_option = pool

        self._path = os.path.abspath(path)
        with open(path) as f:
            content = f.read()
        self._cnf = yaml.load(content)
        self._deploy = []
        self._hosts = []
        self._pool = []
        self._extends = []

        self._validate()

        # first merge hosts and deploy
        self._deploy = list(self._process_deploy())
        self._hosts = list(self._process_hosts())
        configs = []
        for extends in reversed(self._extends):
            path = os.path.join(os.path.dirname(self._path), extends)
            c = Config(path, self._hosts_option, self._pool_option)
            configs.append(c)
            self._merge(c, '_deploy')
            self._merge(c, '_hosts')

        # check hosts
        if self._hosts_option:
            self._hosts = [h for h in self._hosts
                           if h.identifier in self._hosts_option]
        # then merge pools
        for c in configs:
            for key, value in reversed(c._pool):
                if key not in [p[0] for p in self._pool]:  # list of tuple
                    self._pool.insert(0, (key, value))

        self.pools = lambda: self._process_pools()

    def _merge(self, other, name):
        current = getattr(self, name)
        for obj in reversed(getattr(other, name)):
            if obj.id not in [cur.id for cur in current]:
                current.insert(0, obj)

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
                raise ValidationError("dict found: %s but %s expected. "
                                      % (current, grammar))

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

    def _process_hosts(self):
        for host in self._hosts_option or self._hosts:
            if self._hosts_option:
                for s in self._hosts:
                    if isinstance(s, tuple) and s[0] == host:
                        # Overwrite the host option with all the host
                        # settings, if they have the same host string.
                        host = s
            if isinstance(host, tuple):
                yield Host(*host)
            else:
                yield Host(host)

    def _process_deploy(self):
        for deploy in self._deploy:
            if isinstance(deploy, tuple):
                yield Deploy(*deploy)
            else:
                yield Deploy(deploy)

    def _process_pools(self):
        hosts = self._hosts
        deploys = self._deploy
        def get_ids(ids, objects, is_host=False):
            for obj in objects:
                for id in ids:
                    if obj.id == id or is_host and self._pool_option and self._hosts_option:
                        yield obj
                if not ids:
                    yield obj

        result = []
        for id, pool in self._pool:
            if self._pool_option not in (id, None):
                continue
            result.append(Pool(id, list(get_ids(pool['hosts'], hosts, True)),
                                   list(get_ids(pool['deploy'], deploys))))
        if self._pool_option and not result:
            raise KeyError("Didn't find the pool '%s'." % self._pool_option)
        if not self._pool:
            # Create a default pool, if there's none.
            result.append(Pool(None, self._hosts, self._deploy))
        return result


class Host(object):
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

    def __repr__(self):
        return '<%s: %s (%s)>' % (type(self).__name__, self.name, self.id)


class Pool(object):
    def __init__(self, id, hosts, deploy):
        self.id = id
        self.hosts = hosts
        self.deploy = deploy

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.id)

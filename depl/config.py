import os

import yaml

_recursion_paths = []


def avoid_recursion(func):
    def wrapper(self, path, *args, **kwargs):
        path = os.path.abspath(path)
        if path in _recursion_paths:
            raise RuntimeError('Recursion in depl files.')
        _recursion_paths.append(path)
        func(self, path, *args, **kwargs)
    return wrapper


class ValidationError(Exception):
    pass


class Config(object):
    @avoid_recursion
    def __init__(self, path, hosts=(), pool=None):
        self._hosts_option = hosts
        self._pool_option = pool

        self._path = path
        with open(path) as f:
            content = f.read()
        self._cnf = yaml.load(content)
        self._deploy = []
        self._hosts = []
        self._pools = []
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
            for key, value in reversed(c._pools):
                if key not in [p[0] for p in self._pools]:  # list of tuple
                    self._pools.insert(0, (key, value))

        self.pools = self._process_pools()

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

            a = self._validate_detail(value, grammar[key])
            setattr(self, '_' + key, a)

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
            # <something> denotes a placeholder (anything)
            is_placeholder = len(list_dict) == 1 and \
                key[0] == '<' and key[-1] == '>'

            for element in current:
                if isinstance(element, dict):
                    # dicts in lists are always tuples - they don't have
                    # multiple entries.
                    if len(element) != 1:
                        raise ValidationError('Dictionary directly in list, %s'
                                              % element)
                    k, value = element.items()[0]
                    if k not in list_dict and not is_placeholder:
                        raise ValidationError('Key %s not found in grammar'
                                              % k)
                    defaults = list_dict.values()[0] if is_placeholder \
                        else list_dict[k]
                    el = self._validate_detail(value, defaults)
                    result.append((k, el))
                elif isinstance(element, list):
                    raise ValidationError('List not expected in list %s' % element)
                else:
                    if element not in list_dict and not is_placeholder:
                        raise ValidationError('Element %s not found in grammar (%s)'
                                              % (element, list_dict))

                    if element in list_dict and isinstance(list_dict[element], dict):
                        result.append((element, list_dict[element]))
                    elif is_placeholder and isinstance(list_dict[key], dict):
                        result.append((element, list_dict[key]))
                    else:
                        result.append(element)
        elif isinstance(current, dict):
            if not isinstance(grammar, dict):
                raise ValidationError("dict found: %s but %s expected. "
                                      % (current, grammar))

            is_placeholder = len(grammar) == 1 and grammar.keys()[0][0] == '<'\
                and grammar.keys()[0][-1] == '>'
            result = dict(grammar)  # grammar is also the default
            for k, value in current.items():
                if k not in grammar and not is_placeholder:
                    raise ValidationError("Key %s is not in grammar." % k)

                gram = grammar.values()[0] if is_placeholder else grammar[k]
                result[k] = self._validate_detail(value, gram)
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
        def get_ids(ids, objects, is_host=False):
            for obj in objects:
                for id in ids:
                    if obj.id == id or is_host and self._pool_option and self._hosts_option:
                        yield obj
                if not ids:
                    yield obj

        hosts = self._hosts
        deploys = self._deploy
        result = []
        for id, pool in self._pools:
            if self._pool_option not in (id, None):
                continue
            result.append(Pool(id, list(get_ids(pool['hosts'], hosts, True)),
                               list(get_ids(pool['deploy'], deploys))))
        if self._pool_option and not result:
            raise KeyError("Didn't find the pool '%s'." % self._pool_option)
        if not self._pools:
            # Create a default pool, if there's none.
            result.append(Pool(None, self._hosts, self._deploy))
        return result


class Host(object):
    def __init__(self, identifier, settings={}):
        self.identifier = identifier
        self.password = settings.get('password', None)
        # set identifier if key doesn't exist or it is None.
        self.id = settings.get('id', identifier) or identifier

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.identifier)


class Deploy(object):
    def __init__(self, name, settings):
        self.name = name
        self.settings = settings
        if name in ('sh', 'fab'):
            # sh and fab are very simple string only, just use the name as its
            # id for now, maybe later switch to counting them.
            self.id = name
        else:
            self.id = self.settings['id']

    def __repr__(self):
        return '<%s: %s (%s)>' % (type(self).__name__, self.name, self.id)


class Pool(object):
    def __init__(self, id, hosts, deploy):
        self.id = id
        self.hosts = hosts
        self.deploy = deploy

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.id)

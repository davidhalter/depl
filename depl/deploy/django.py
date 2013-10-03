import json
from StringIO import StringIO
import textwrap
from os.path import exists
import re

from depl import deploy
from depl.deploy import python
from depl.config import Deploy
from fabric.api import cd, prefix, put, sudo, warn_only, local


def load(settings, package):
    if not exists('manage.py'):
        raise LookupError('Django projects need a manage.py')

    # settings
    settings_module = settings['settings']
    if settings_module is None:
        with open('manage.py') as f:
            m = re.search('''["']DJANGO_SETTINGS_MODULE['"], ["']([\d\w_.]+)["']''',
                         f.read())
            if not m:
                raise LookupError("manage.py doesn't have a settings module defined")
            settings_module = m.groups()[0]

    remote_path = '/var/www/depl_' + settings['id']

    # static files
    depl_settings = textwrap.dedent("""
    from %s import *

    STATIC_ROOT = 'depl_staticfiles'
    """ % settings_module)
    settings['static'] = {'/static': 'depl_staticfiles'}

    # wsgi - use the right settings
    wsgi_file = python.search_wsgi(settings)
    depl_wsgi = textwrap.dedent("""
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "depl_settings")
    from %s import *
    """) % wsgi_file
    settings['wsgi'] = 'depl_wsgi'

    def django_stuff():
        with cd(remote_path):
            put(StringIO(depl_settings), 'depl_settings.py', use_sudo=True)
            put(StringIO(depl_wsgi), 'depl_wsgi.py', use_sudo=True)
            sudo('chown www-data:www-data depl_settings.py')
            with prefix('source venv/bin/activate'):
                # collectstatic
                sudo('django-admin.py collectstatic --noinput --pythonpath . '
                     '--settings=depl_settings ', user='www-data')
                # syncdb (also do a migrate if something needs to be migrated)
                sudo('django-admin.py syncdb --noinput --pythonpath . '
                     '--settings=depl_settings --migrate', user='www-data')

            # Restart both uwsgi & nginx, they might need it. But in the future
            # we could order the commands better.
            sudo('service uwsgi restart')
            sudo('service nginx restart')

    dependencies, commands = python.load(settings, package)
    add_dep, add_commands = db_auto_detect(settings['id'], settings_module)
    return dependencies | add_dep, add_commands + commands + [django_stuff]


def db_auto_detect(django_id, settings_module):
    def get_deploys(json_str):
        count = 0
        for name, db_settings in json.loads(json_str).items():
            engine = db_settings['ENGINE']
            if 'psycopg2' not in engine:
                # for now only postgresql is supported
                continue

            if db_settings['HOST']:
                db_settings['HOST']
            if db_settings['HOST'] not in ['localhost', '127.0.0.1', '']:
                # only localhost autodetection allowed (everything else doesn't
                # make sense)
                continue
            if db_settings['PORT']:
                # Port settings not yet supported
                continue

            settings = {
                'id': 'auto_dectect_%s_%s' % (django_id, count),
                'database': db_settings['NAME'],
                'user': db_settings['USER'],
                'password': db_settings['PASSWORD']
            }
            yield 'psycopg2-build-tools', Deploy('postgresql', settings)
            count += 1

    with warn_only():
        json_str = local('python -c "import json;'
                         'from %s import *;'
                         'print(json.dumps(DATABASES))"' % settings_module,
                         capture=True)
        if json_str.failed:
            return [], []

    commands = []
    dependencies = set()
    for dependency, deploy_obj in get_deploys(json_str):
        commands += deploy.load(deploy_obj.name, deploy_obj.settings)
        dependencies.add(dependency)
    return dependencies, commands

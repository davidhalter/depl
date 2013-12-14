"""
Django supports the following additional options:

.. sourcecode:: yaml

    deploy:
        - django:
            settings: project.settings  # depl searches automatically
            admin:
                user: null
                email: null

Note that the admin interface doesn't yet allow you to specify a password. A
`pull request <https://github.com/fabric/fabric/pull/1021>`_ for fabric is
pending. Until that you have to enter your password manually.

If you don't need an admin super user, you can just deploy it like this:

.. sourcecode:: yaml

    deploy:
        - django

Django is driven by uwsgi.
"""
import json
from StringIO import StringIO
import textwrap
from os.path import exists
import re

from depl.deploy import Package, load_commands
from depl.deploy import wsgi
from depl.config import Deploy
from fabric.api import cd, prefix, put, sudo, warn_only, local


def deploy(settings):
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
    wsgi_file = wsgi.search_wsgi(settings)
    depl_wsgi = textwrap.dedent("""
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "depl_settings")
    from %s import *
    """) % wsgi_file
    settings['wsgi'] = 'depl_wsgi'

    def django_cmd(cmd, no_input=True):
        no_input = '--noinput' if no_input else ''
        return 'django-admin.py %s %s --pythonpath . ' \
            '--settings=depl_settings ' % (cmd, no_input)

    user = settings['admin']['user']
    if user is not None:
        email = settings['admin']['email']
        if email is None:
            raise ValueError('Admin email must be provided.')

    def django_stuff():
        with cd(remote_path):
            put(StringIO(depl_settings), 'depl_settings.py', use_sudo=True)
            put(StringIO(depl_wsgi), 'depl_wsgi.py', use_sudo=True)
            sudo('chown www-data:www-data depl_settings.py')
            with prefix('source venv/bin/activate'):
                # collectstatic
                sudo(django_cmd('collectstatic'), user='www-data')
                # syncdb (also do a migrate if something needs to be migrated)
                c = django_cmd('syncdb')
                # sometimes migrate is not available...
                sudo(c + ' --migrate || ' + c, user='www-data')

                if user:
                    cmd = django_cmd('createsuperuser', no_input=False)
                    sudo(cmd + " --username '%s' --email '%s' || true"
                         % (user, email))

            # Restart both uwsgi & nginx, they might need it. But in the future
            # we could order the commands better.
            sudo('service depl_uwsgi restart')
            sudo('service nginx restart')

    commands = wsgi.deploy(settings)
    db_commands = db_auto_detect(settings['id'], settings_module)
    return db_commands + commands + (django_stuff,)


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
            yield Package('psycopg2-build-tools'), Deploy('postgresql', settings)
            count += 1

    with warn_only():
        json_str = local('python -c "import json;'
                         'from %s import *;'
                         'print(json.dumps(DATABASES))"' % settings_module,
                         capture=True)
        if json_str.failed:
            return [], []

    commands = []
    for dependency, deploy_obj in get_deploys(json_str):
        commands += load_commands(deploy_obj.name, deploy_obj.settings)
        commands.append(dependency)
    return tuple(commands)

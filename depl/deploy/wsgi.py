"""
The only additional option for wsgi is ``wsgi``:

.. sourcecode:: yaml

    deploy:
        - wsgi:
            wsgi: foo:bar
            port: 8080

WSGI plugins are driven by uwsgi.
"""
import os
from StringIO import StringIO
import textwrap

from fabric.api import put, sudo
from fabric.context_managers import cd, prefix

from depl.deploy import _utils
from . import Package


def deploy(settings):
    remote_path = '/var/www/depl_' + settings['id']
    local_path = '.'

    # python projects should always have a 'requirements.txt'.
    if not os.path.exists(os.path.join(local_path, 'requirements.txt')):
        raise LookupError("requirements.txt doesn't exist in your Python project (%s)."
                          % local_path)

    # configure nginx
    socket = remote_path + '/uwsgi.sock'
    uwsgi_nginx = "include uwsgi_params; uwsgi_pass unix:%s;" % socket

    locations = {'/': uwsgi_nginx}
    if 'static' in settings:
        for url, path in settings['static'].items():
            locations[url] = 'alias %s;' % os.path.join(remote_path, path)

    nginx_conf = _utils.nginx_config(settings, locations)

    wsgi_path = search_wsgi(settings)
    uwsgi_file = _gen_uwsgi_file(wsgi_path, remote_path, socket)

    uwsgi_start_file = _gen_uwsgi_start_file(remote_path)

    def install_python():
        sudo('pip -q install virtualenv')
        with cd(remote_path):
            sudo('ls venv || virtualenv venv', user='www-data')
            with prefix('source venv/bin/activate'):
                # maybe need the latest setuptools (some packages might require
                # it)
                #sudo('pip -q install -r --upgrade setuptools', user='www-data')
                sudo('pip -q install -r requirements.txt', user='www-data')
                sudo('pip -q install uwsgi', user='www-data')

    def setup_uwsgi():
        sudo('mkdir /etc/uwsgi && mkdir /etc/uwsgi/vassals || true')
        #logs
        sudo('mkdir /var/log/uwsgi || true')
        sudo('chown -R www-data:www-data /var/log/uwsgi')

        put(uwsgi_file, '/etc/uwsgi/vassals/depl_%s.ini' % settings['id'], use_sudo=True)
        put(uwsgi_start_file, '/etc/init/depl_uwsgi.conf', use_sudo=True)
        sudo('service depl_uwsgi restart')

    commands = (
        _utils.move_project_to_www(local_path, remote_path),
        install_python,
        setup_uwsgi,
        _utils.generate_ssl_keys(settings['id'], settings['ssl']),
        _utils.install_nginx(nginx_conf, settings['id']),
    )
    return tuple(Package(d) for d in ['pip', 'uwsgi-build-tools', 'nginx']) + commands


def _gen_uwsgi_file(wsgi_file, remote_path, socket):
    # configure uwsgi
    uwsgi_config = """
    [uwsgi]
    #application's base folder
    base = {0}

    #python module to import
    app = {1}
    module = %(app)

    chdir = %(base)
    home = %(base)/venv
    pythonpath = %(base)

    #socket file's location
    socket = {2}

    #permissions for the socket file
    chmod-socket    = 644

    #location of log files
    logto = /var/log/uwsgi/%n.log

    uid = www-data
    gid = www-data
    """.format(remote_path, wsgi_file, socket)

    uwsgi_file = StringIO(textwrap.dedent(uwsgi_config))
    return uwsgi_file


def _gen_uwsgi_start_file(remote_path):
    # find a way to make this platform independent - should run on systems
    # without upstart, too. Not sure if `init.d` scripts would resolve the
    # issue for upstart/systemd systems.
    auto_start = """
    description "uWSGI"
    start on runlevel [2345]
    stop on runlevel [06]
    respawn

    env UWSGI=%s
    env LOGTO=/var/log/uwsgi/emperor.log

    exec $UWSGI --master --emperor /etc/uwsgi/vassals --die-on-term --uid www-data --gid www-data --logto $LOGTO
    """ % (remote_path + '/venv/bin/uwsgi')
    return StringIO(textwrap.dedent(auto_start))


def search_wsgi(settings):
    wsgi_path = settings.get('wsgi')
    if wsgi_path is None:
        # search for a file in the project named "wsgi"
        for root, dirnames, filenames in os.walk('.'):
            if root == '.' or not os.path.basename(root).startswith('.'):
                for filename in filenames:
                    if filename == 'wsgi.py':
                        p = os.path.join(root, filename)[2:-3]
                        wsgi_path = p.replace(os.path.sep, '.')
                        break
                if wsgi_path:
                    break
        else:
            raise ValueError('WSGI path not set and no file named wsgi.py in the project found')
    return wsgi_path

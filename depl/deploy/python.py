import os
from io import StringIO
import textwrap

from fabric.api import put, sudo, run
from fabric.context_managers import cd

from depl.deploy._utils import nginx_config, install_nginx, move_project_to_www


def load(settings, package):
    remote_path = '/var/www/depl-' + settings['id']
    local_path = os.path.abspath('.')

    # python projects should always have a 'requirements.txt'.
    if not os.path.exists(os.path.join(local_path, 'requirements.txt')):
        raise LookupError("requirements.txt doesn't exist in your Python project.")

    # configure nginx
    socket = remote_path + '/uwsgi.sock'
    uwsgi_nginx = "include uwsgi_params; uwsgi_pass unix:%s;" % socket

    locations = {'/': uwsgi_nginx}
    nginx_conf = nginx_config(settings['url'], settings['port'], locations)
    nginx_file = StringIO(nginx_conf)

    uwsgi_file = _gen_uwsgi_file(settings['wsgi'], remote_path, socket)

    uwsgi_start_file = _gen_uwsgi_start_file(remote_path)

    def install_python():
        sudo('pip install virtualenv')
        with cd(remote_path):
            run('virtualenv venv')
            run('source venv/bin/activate')
            run('pip install -r requirements.txt')

            run('pip install uwsgi')
            run('deactivate')

    def setup_uwsgi():
        sudo('mkdir /etc/uwsgi && mkdir /etc/uwsgi/vassals || true')

        put(uwsgi_file, '/etc/uwsgi/vassals/depl-%s.ini' % settings['id'])
        put(uwsgi_start_file, '/etc/init/uwsgi')
        sudo('service uwsgi restart')

    commands = [
        move_project_to_www(local_path, remote_path),
        install_python,
        setup_uwsgi,
        install_nginx(nginx_file, settings['id']),
    ]
    return ['pip'], commands


def _gen_uwsgi_file(wsgi_file, remote_path, socket):
    # configure uwsgi
    uwsgi_config = """
    [uwsgi]
    #application's base folder
    base = {0}

    #python module to import
    app = {1}
    module = %(app)

    home = %(base)/venv
    pythonpath = %(base)

    #socket file's location
    socket = {2}

    #permissions for the socket file
    chmod-socket    = 666

    #the variable that holds a flask application inside the module imported at line #6
    callable = app

    #location of log files
    logto = /var/log/uwsgi-%n.log

    uid = www-data
    gid = www-data
    """.format(remote_path, wsgi_file, socket)

    uwsgi_file = StringIO(textwrap.dedent(uwsgi_config))
    return uwsgi_file


def _gen_uwsgi_start_file(remote_path):
    auto_start = """
    description "uWSGI"
    start on runlevel [2345]
    stop on runlevel [06]
    respawn

    env UWSGI=%s
    env LOGTO=/var/log/uwsgi-emperor.log

    exec $UWSGI --master --emperor /etc/uwsgi/vassals --die-on-term --uid www-data --gid www-data --logto $LOGTO
    """ % (remote_path + '/venv/bin/uwsgi')
    return StringIO(textwrap.dedent(auto_start))

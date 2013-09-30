import os
from io import StringIO

from fabric.api import put, sudo, run

from depl.deploy._utils import nginx_config, install_nginx_callable


def load(settings, package):
    path = '/var/www/depl-' + settings['id']

    # configure nginx
    socket = path + '/uwsgi.sock'
    uwsgi_nginx = "include uwsgi_params; uwsgi_pass unix:%s;" % socket

    locations = {'/': uwsgi_nginx}
    nginx_conf = nginx_config(settings['url'], settings['port'], locations)
    nginx_file = StringIO(nginx_conf)

    # configure uwsgi

    def install_python():
        sudo('mkdir /var/www || true')
        user = run('whoami')
        sudo('chown %s %s' % (user, '/var/www/'))
        sudo('mkdir %s || true')
        put('.', path)

        sudo('pip install virtualenv')

    install_nginx = install_nginx_callable(nginx_file, settings['id'])
    return ['pip'], [install_nginx, install_python]

"""
To deploy meteor, just use something like:

.. sourcecode:: yaml

    deploy:
        - meteor:
            port: 8080

There are no additional options to the :ref:`general web options
<general-web>`.
"""
from StringIO import StringIO
import textwrap

from fabric.api import sudo, put
from fabric.context_managers import quiet, shell_env

from . import Package
from . import mongodb, _utils

APT_REPO = \
    "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"


def deploy(settings):
    def install():
        # remove a lot of output (orginally stderr) by removing the %
        meteor_path = '/var/www/.meteor'
        with quiet():
            install_meteor = False
            if sudo('test -d %s' % meteor_path, user='www-data').failed:
                install_meteor = True
        if install_meteor:
            # meteor installer needs access rights for $HOME
            sudo('chown www-data:www-data /var/www/')
            with shell_env(HOME='/var/www'):
                sudo('curl https://install.meteor.com '
                     '| sed "s/if sudo cp/if echo/g"'  # remove annoying sudo operation
                     '| /bin/sh 2>&1 | grep -v "%"',
                     user='www-data')
            # link from /usr/local/bin/
            sudo('ln -f -s %s/tools/latest/bin/meteor /usr/local/bin/meteor'
                 % meteor_path)

    def meteor_upstart():
        # find a more general way - not upstart - look at comment in python
        # uwsgi upstart.
        auto_start = """
        description "meteor"
        start on runlevel [2345]
        stop on runlevel [06]
        respawn

        script
            cd "%s"
            exec sudo -u www-data meteor
        end script
        """ % remote_path

        file = StringIO(textwrap.dedent(auto_start))
        put(file, '/etc/init/depl_%s.conf' % settings['id'], use_sudo=True)
        sudo('service depl_meteor restart')

    locations = {'/': """
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    """}
    nginx_conf = _utils.nginx_config(settings, locations)
    remote_path = '/var/www/depl_' + settings['id']

    mongo_commands = mongodb.deploy(settings)
    commands = (
        _utils.move_project_to_www(settings['path'], remote_path),
        install,
        meteor_upstart,
        _utils.generate_ssl_keys(settings['id'], settings['ssl']),
        _utils.install_nginx(nginx_conf, settings['id']),
    )
    return (Package('nodejs'),) + mongo_commands + commands

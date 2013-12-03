from StringIO import StringIO
import textwrap

from fabric.api import run, sudo, put
from fabric.context_managers import quiet

from . import Package
from . import mongodb, _utils

APT_REPO = \
    "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"


def load(settings):
    def install():
        # remove a lot of output (orginally stderr) by removing the %
        with quiet(''):
            do_it = False
            if run('test -d ~/.meteor').status_code == 1:
                do_it = True
        if do_it:
            run('curl https://install.meteor.com | /bin/sh 2>&1 | grep -v "%"')
            sudo('ln -f -s ~/.meteor/meteor /usr/local/bin/meteor')

        sudo('service nginx restart')

    def meteor_upstart(remote_path):
        # find a more general way - not upstart - look at comment in python
        # uwsgi upstart.
        auto_start = """
        description "meteor"
        start on runlevel [2345]
        stop on runlevel [06]
        respawn

        env UWSGI=%s
        env LOGTO=/var/log/uwsgi/emperor.log

        script
            cd "%s"
            exec sudo -u www-data meteor
        end script
        """ % remote_path
        file = StringIO(textwrap.dedent(auto_start))
        put(file, '/etc/init/meteor.conf', use_sudo=True)
        sudo('service meteor start')

    locations = {'/': """
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    """}
    nginx_conf = _utils.nginx_config(settings, locations)

    dependencies, commands = mongodb.load(settings)
    commands += [
        _utils.move_project_to_www('.', '~/'),
        install,
        meteor_upstart,
        _utils.install_nginx(nginx_conf, settings['id']),
    ]
    return dependencies | set([Package('nodejs')]), commands

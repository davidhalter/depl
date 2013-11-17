import os
import textwrap

from fabric.api import put, sudo
from fabric.contrib.project import upload_project

SSL_PATH = '/etc/nginx/ssl'
SSL_FILE_PATH = '%s/depl_%s' % (SSL_PATH, depl_id)


def lazy(func):
    def wrapper(*args, **kwargs):
        return lambda: func(*args, **kwargs)
    return wrapper


def nginx_config(settings, locations):
    config = """
        server {
            listen      [::]:%s;
            server_name %s;
            charset     utf-8;
            client_max_body_size 75M;

        %s

        %s
        }
    """

    ssl = settings['ssl']

    add_ssl = """
    ssl_certificate %s
    ssl_certificate_key %s
    """ % (SSL_FILE_PATH + '.crt', SSL_FILE_PATH + '.key')

    l = '    location %s {%s}'
    locations = [l % (path, values) for path, values in locations.items()]
    locations = '\n'.join(locations)

    add_http = ''
    cfgs = (settings['port'], add_http), (ssl['port'] + ' ssl', add_ssl)
    config_txt = ''
    for port, add_config in cfgs:
        config_txt += textwrap.dedent(config) % (port, settings['url'],
                                                 add_config, locations)
    return config_txt


@lazy
def install_nginx(nginx_file, id):
    put(nginx_file, '/etc/nginx/conf.d/depl_%s.conf' % id, use_sudo=True)
    # remove the default configuration
    sudo('rm /etc/nginx/sites-enabled/default || true')
    sudo('/etc/init.d/nginx restart')


@lazy
def move_project_to_www(local_path, remote_path):
    sudo('mkdir /var/www || true')
    depl_tmp = '/var/www/tmp_depl'
    sudo('mkdir %s || true' % depl_tmp)
    upload_project(local_path, depl_tmp, use_sudo=True)
    _, local_name = os.path.split(local_path)
    # delete all the files in the target directory that are also in the source
    # directory and move the source.
    sudo('mkdir %s || true' % remote_path)
    sudo('ls -A {from_p} | xargs -I [] sh -c '
         '"rm -rf {to_p}/[] || true; mv {from_p}/[] {to_p}"'
         .format(from_p=os.path.join(depl_tmp, local_name), to_p=remote_path))
    sudo('rm -rf %s' % depl_tmp)
    sudo('chown -R www-data:www-data ' + remote_path)


@lazy
def generate_ssl_keys(depl_id, ssl_config):
    # The whole generation thing is a proof of concept to have ssl running
    # without a CA. This makes it easier to deploy things the first time.
    # So keep in mind: This **doesn't protect you against "Man in the Middle"**
    # attacks!
    # However it's important that somebody with a security background improves
    # this.
    pass_out = ' -passin pass:depl'
    pass_in = ' -passin pass:depl'
    sudo('mkdir %s || true' % SSL_PATH)
    # generate key
    sudo('openssl genrsa -des3 -out {1}.key.orig 1024{2}'
         .format(SSL_FILE_PATH, pass_out))
    # generate certificate signing request
    sudo('echo -e "\n\n\n\n\n\n\n\n" | '
         'openssl req -new -key {0}.key.orig -out {0}.csr {1}'
         .format(SSL_FILE_PATH, pass_in))
    # remove password from key
    sudo('openssl rsa -in {0}.key.orig -out {0}.key {1}'
         .format(SSL_FILE_PATH, pass_in))
    sudo('openssl x509 -req -days 9999 -in {0}.csr -signkey {0}.key -out {0}.crt'
         .format(SSL_FILE_PATH))

"""

Nginx Configuration
-------------------

Nginx can typically be configured with two simple https/http port settings. If
you set one of the port to ``REDIRECT``, it will redirect to the other
protocol. You can also disable the protocol by setting the port number to
``false``.

"""
import os
import textwrap
from StringIO import StringIO

from fabric.api import put, sudo
from fabric.contrib.project import upload_project
from fabric.contrib import files

SSL_PATH = '/etc/nginx/ssl'
SSL_FILE_PATH = '%s/depl_%%s' % SSL_PATH


def lazy(func):
    def wrapper(*args, **kwargs):
        return lambda: func(*args, **kwargs)
    return wrapper


def nginx_config(settings, locations):
    ssl_file_path = SSL_FILE_PATH % settings['id']
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

    if bool(ssl['key']) != bool(ssl['certificate']):
        raise ValueError('SSL certificate given but not key - need both!')

    add_ssl = """
    ssl_certificate %s;
    ssl_certificate_key %s;
    """ % (ssl_file_path + '.crt', ssl_file_path + '.key')

    l = '    location %s {%s}'
    locations = [l % (path, values) for path, values in locations.items()]
    locations = '\n'.join(locations)

    http_port = settings['port']
    cfgs = (('http', http_port, '', settings['redirect'], ssl['port']),
            ('https', ssl['port'] and '%s ssl' % ssl['port'], add_ssl, ssl['redirect'], http_port))
    config_txt = ''
    for proto, port, add_config, redirect, other_port in cfgs:
        # if port is set to zero - disable it
        if port:
            l = locations
            if redirect is not None:
                if redirect in ('http', 'https'):
                    l = "    return 301 %s://$host:%s$request_uri;" \
                        % (redirect, other_port)
                else:
                    l = "    return 301 %s" % redirect
            config_txt += textwrap.dedent(config) % (port, settings['url'],
                                                     add_config, l)
    return config_txt


@lazy
def install_nginx(nginx_txt, id):
    nginx_file = StringIO(nginx_txt)
    put(nginx_file, '/etc/nginx/conf.d/depl_%s.conf' % id, use_sudo=True)
    # remove the default configuration
    sudo('rm /etc/nginx/sites-enabled/default || true')
    sudo('/etc/init.d/nginx restart')


@lazy
def move_project_to_www(local_path, remote_path):
    local_path = os.path.abspath(local_path)
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
    """
    Done with the help of
    https://www.digitalocean.com/community/articles/how-to-create-a-ssl-certificate-on-nginx-for-ubuntu-12-04
    and some other good influences.
    """
    ssl_file_path = SSL_FILE_PATH % depl_id
    # The whole generation thing is a proof of concept to have ssl running
    # without a CA. This makes it easier to deploy things the first time.
    # So keep in mind: This **doesn't protect you against "Man in the Middle"**
    # attacks!
    # However it's important that somebody with a security background improves
    # this.
    pass_out = ' -passout pass:depl'
    pass_in = ' -passin pass:depl'
    sudo('mkdir %s || true' % SSL_PATH)

    if ssl_config['key']:
        put(ssl_config['key'], ssl_file_path + '.key', use_sudo=True)
        put(ssl_config['certificate'], ssl_file_path + '.crt', use_sudo=True)
    else:
        if not files.exists(ssl_file_path + '.key'):
            # generate key
            sudo('openssl genrsa -des3 {1} -out {0}.key.orig 1024'
                 .format(ssl_file_path, pass_out))
            # generate certificate signing request
            sudo('echo -e "\n\n\n\n\n\n\n\n" | '
                 'openssl req -new -key {0}.key.orig -out {0}.csr {1}'
                 .format(ssl_file_path, pass_in))
            # remove password from key
            sudo('openssl rsa -in {0}.key.orig -out {0}.key {1}'
                 .format(ssl_file_path, pass_in))
        if not files.exists(ssl_file_path + '.crt'):
            sudo('openssl x509 -req -days 9999 -in {0}.csr -signkey {0}.key -out {0}.crt'
                 .format(ssl_file_path))

import textwrap

from fabric.api import put, sudo
from fabric.contrib.project import upload_project


def lazy(func):
    def wrapper(*args, **kwargs):
        return lambda: func(*args, **kwargs)
    return wrapper

def nginx_config(url, port, locations):
    config = """
        server {
            listen      %s;
            server_name %s;
            charset     utf-8;
            client_max_body_size 75M;

        %s
        }
    """

    l = '    location %s {%s}'
    locations = [l % (path, values) for path, values in locations.items()]
    config_txt = textwrap.dedent(config) % (port, url, '\n'.join(locations))
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
    sudo('mkdir %s || true' % remote_path)
    upload_project(local_path, remote_path, use_sudo=True)
    sudo('chown -R www-data:www-data ' + remote_path)

import textwrap

from fabric.api import put, sudo


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
    config_txt = textwrap.dedent(config) % (url, locations)
    return config_txt


def install_nginx_callable(nginx_file, id):
    def install_nginx():
        put(nginx_file, '/etc/nginx/conf.d/depl-%s.conf' % id, use_sudo=True)
        sudo('/etc/init.d/nginx restart')
    return install_nginx
